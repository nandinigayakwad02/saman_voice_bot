from fastapi import FastAPI, Request, Response, HTTPException, BackgroundTasks
from fastapi.responses import JSONResponse
from app.config import settings
from app.whatsapp import whatsapp_client
from app.ai_agent import get_ai_response, clear_conversation
from app.tts_converter import convert_text_to_speech_with_cleanup
from datetime import datetime
import logging
from typing import Dict, Any

# Configure logging
logging.basicConfig(
    level=getattr(logging, settings.LOG_LEVEL),
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Initialize FastAPI app
app = FastAPI(
    title="WhatsApp AI Chatbot",
    description="Simple WhatsApp chatbot powered by OpenAI",
    version="1.0.0"
)


@app.on_event("startup")
async def startup_event():
    """Startup event handler"""
    logger.info(" Starting WhatsApp AI Chatbot...")
    logger.info(f" Server running on http://{settings.HOST}:{settings.PORT}")


@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "message": "WhatsApp AI Chatbot",
        "version": "1.0.0",
        "status": "running"
    }


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "timestamp": datetime.utcnow().isoformat()}


# WhatsApp Webhook Routes

@app.get("/webhook")
async def verify_webhook(request: Request):
    """
    Webhook verification endpoint for WhatsApp
    Meta will send a GET request to verify the webhook
    """
    mode = request.query_params.get("hub.mode")
    token = request.query_params.get("hub.verify_token")
    challenge = request.query_params.get("hub.challenge")
    
    logger.info(f"📞 Webhook verification request - Mode: {mode}, Token: {token}")
    
    if mode == "subscribe" and token == settings.WEBHOOK_VERIFY_TOKEN:
        logger.info(" Webhook verified successfully!")
        return Response(content=challenge, media_type="text/plain")
    else:
        logger.error(" Webhook verification failed!")
        raise HTTPException(status_code=403, detail="Verification failed")


@app.post("/webhook")
async def receive_webhook(request: Request, background_tasks: BackgroundTasks):
    """
    Webhook endpoint to receive WhatsApp messages
    """
    try:
        body = await request.json()
        logger.info(f" Received webhook: {body}")
        
        # Process webhook in background
        background_tasks.add_task(process_webhook, body)
        
        return JSONResponse(content={"status": "received"}, status_code=200)
    
    except Exception as e:
        logger.error(f" Error processing webhook: {e}")
        return JSONResponse(content={"status": "error", "message": str(e)}, status_code=500)


async def process_webhook(body: Dict[str, Any]):
    """Process WhatsApp webhook payload"""
    try:
        if body.get("object") != "whatsapp_business_account":
            logger.warning(f" Unknown webhook object: {body.get('object')}")
            return
        
        for entry in body.get("entry", []):
            for change in entry.get("changes", []):
                value = change.get("value", {})
                
                # Handle messages
                if "messages" in value:
                    for message in value["messages"]:
                        await handle_incoming_message(message, value)
                
                # Handle status updates
                if "statuses" in value:
                    for status in value["statuses"]:
                        logger.info(f" Status update: {status.get('status')} for {status.get('id')}")
    
    except Exception as e:
        logger.error(f" Error in process_webhook: {e}")


async def handle_incoming_message(message: dict, value: dict):
    """Handle incoming WhatsApp message"""
    try:
        message_id = message.get("id")
        from_number = message.get("from")
        message_type = message.get("type")
        timestamp = datetime.fromtimestamp(int(message.get("timestamp", 0)))
        
        logger.info(f" Message from {from_number}: Type={message_type}")
        
        # Mark message as read
        await whatsapp_client.mark_message_as_read(message_id)
        
        # Check if message is from authorized user
        allowed_phones = settings.allowed_phone_list
        if allowed_phones and from_number not in allowed_phones:
            logger.warning(f" Unauthorized number: {from_number}")
            # Silently ignore unauthorized users
            return
        
        # Handle TEXT messages (AI chat → Voice response)
        if message_type == "text":
            # Get message content
            content = message.get("text", {}).get("body", "")
            logger.info(f" Message content: {content}")
            
            # Check for special commands
            if content.lower().strip() == "/clear":
                clear_conversation(from_number)
                
                # Send voice confirmation for /clear command
                try:
                    clear_message = "Conversation history cleared!"
                    voice_bytes = await convert_text_to_speech_with_cleanup(clear_message)
                    await whatsapp_client.send_audio_message(
                        to=from_number,
                        audio_bytes=voice_bytes
                    )
                    logger.info(f" Sent voice confirmation to {from_number}")
                except Exception as e:
                    logger.error(f" Failed to send voice confirmation: {e}")
                    # Error logged, no fallback message
                return
            
            # Get AI text response (maintains conversation history)
            ai_response = await get_ai_response(from_number, content)
            logger.info(f" AI response: {ai_response[:100]}...")
            
            # Convert AI response to voice and send
            try:
                logger.info(" Converting AI response to voice...")
                voice_bytes = await convert_text_to_speech_with_cleanup(ai_response)
                
                await whatsapp_client.send_audio_message(
                    to=from_number,
                    audio_bytes=voice_bytes
                )
                logger.info(f" Sent voice response to {from_number}")
                
            except Exception as e:
                logger.error(f" Failed to convert/send voice: {e}")
                # Error logged, no fallback message sent

        
        # Handle AUDIO/VOICE messages (Voice-to-Voice with Realtime API)
        elif message_type == "audio":
            logger.info(f" Voice message received - processing with Realtime API...")
            try:
                # Get media ID
                media_id = message.get("audio", {}).get("id")
                if not media_id:
                    raise Exception("No media ID found in audio message")
                
                # Processing silently (no status message to user)
                
                # Download audio from WhatsApp
                logger.info(f" Downloading audio media: {media_id}")
                audio_bytes = await whatsapp_client.download_media(media_id)
                logger.info(f" Downloaded {len(audio_bytes)} bytes")
                
                # Step 1: Transcribe voice to text (Whisper)
                logger.info(" Transcribing audio with Whisper...")
                from app.tts_converter import transcribe_audio
                transcribed_text = await transcribe_audio(audio_bytes)
                logger.info(f" Transcription: {transcribed_text[:100]}...")
                
                # Step 2: Get AI response in Dutch (same as text messages)
                logger.info(" Getting AI response in Dutch...")
                ai_response = await get_ai_response(from_number, transcribed_text)
                logger.info(f" AI response: {ai_response[:100]}...")
                
                # Step 3: Convert to voice using Saman's voice (ElevenLabs)
                logger.info(" Converting response to Saman's voice...")
                voice_bytes = await convert_text_to_speech_with_cleanup(ai_response)
                logger.info(f" Voice generated: {len(voice_bytes)} bytes")
                
                # Step 4: Send voice response
                logger.info(" Sending voice response...")
                await whatsapp_client.send_audio_message(
                    to=from_number,
                    audio_bytes=voice_bytes
                )
                
                logger.info(f" Voice response sent to {from_number} (Saman's voice)")
                return
                
            except Exception as e:
                logger.error(f" Voice processing failed: {e}")
                # Error logged, no message sent to user
                return
        
        # Unsupported message type
        else:
            logger.warning(f" Unsupported message type: {message_type}")
            # Silently ignore unsupported message types
    
    except Exception as e:
        logger.error(f" Error handling incoming message: {e}")
        # Error logged, no message sent to user


# Message Routes

@app.post("/messages/send")
async def send_message(data: dict):
    """
    Send a WhatsApp message
    
    Body:
    {
        "to": "15551571989",
        "message": "Your message here"
    }
    """
    try:
        to = data.get("to")
        message = data.get("message")
        
        if not to or not message:
            raise HTTPException(status_code=400, detail="Missing 'to' or 'message'")
        
        result = await whatsapp_client.send_text_message(to, message)
        
        return {"status": "success", "data": result}
    
    except Exception as e:
        logger.error(f" Error sending message: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# Conversation Management

@app.post("/conversation/clear")
async def clear_user_conversation(data: dict):
    """
    Clear conversation history for a user
    
    Body:
    {
        "phone": "918226053534"
    }
    """
    phone = data.get("phone")
    if not phone:
        raise HTTPException(status_code=400, detail="Missing 'phone'")
    
    clear_conversation(phone)
    return {"status": "success", "message": f"Cleared conversation for {phone}"}


@app.post("/test/send")
async def send_test_message():
    """Send a test message to the first authorized number"""
    try:
        # Get first authorized phone number
        allowed_phones = settings.allowed_phone_list
        if not allowed_phones:
            raise HTTPException(status_code=400, detail="No authorized phone numbers configured")
        
        test_phone = allowed_phones[0]
        
        test_message = f"""
 *Test Message*

This is a test message from your WhatsApp AI Chatbot!

Time: {datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')} UTC

Send me any message and I'll respond with AI! 
        """.strip()
        
        result = await whatsapp_client.send_text_message(
            test_phone,
            test_message
        )
        
        return {
            "status": "success",
            "message_id": result["messages"][0]["id"],
            "sent_to": test_phone
        }
    
    except Exception as e:
        logger.error(f" Error sending test message: {e}")
        raise HTTPException(status_code=500, detail=str(e))


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app.main:app",
        host=settings.HOST,
        port=settings.PORT,
        reload=settings.DEBUG
    )
