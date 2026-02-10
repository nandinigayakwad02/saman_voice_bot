import asyncio
import base64
import json
import logging
import websockets
import io
import subprocess
import tempfile
import os
from typing import List
from app.config import settings

logger = logging.getLogger(__name__)


async def process_voice_with_realtime(
    audio_bytes: bytes,
    user_phone: str,
    conversation_context: str = ""
) -> bytes:
    """
    Process voice message using OpenAI Realtime API
    
    Args:
        audio_bytes: Input audio bytes (OGG format from WhatsApp)
        user_phone: User's phone number for context
        conversation_context: Previous conversation context
        
    Returns:
        Response audio bytes (OGG format for WhatsApp)
    """
    try:
        logger.info(f" Processing voice message with Realtime API for {user_phone}")
        
        # Step 1: Convert WhatsApp OGG to PCM for Realtime API
        logger.info("🔄 Converting OGG to PCM...")
        pcm_audio = convert_to_pcm(audio_bytes)
        logger.info(f" Converted to PCM: {len(pcm_audio)} bytes")
        
        # Step 2: Connect to Realtime API and process
        logger.info("🔌 Connecting to OpenAI Realtime API...")
        response_pcm = await send_to_realtime_api(pcm_audio, user_phone, conversation_context)
        logger.info(f" Received response: {len(response_pcm)} bytes")
        
        # Step 3: Convert response PCM back to OGG for WhatsApp
        logger.info("🔄 Converting PCM to OGG...")
        ogg_audio = convert_from_pcm(response_pcm)
        logger.info(f" Converted to OGG: {len(ogg_audio)} bytes")
        
        return ogg_audio
        
    except Exception as e:
        logger.error(f" Error processing voice with Realtime API: {e}")
        raise


def convert_to_pcm(audio_bytes: bytes) -> bytes:
    """
    Convert WhatsApp audio (OGG/Opus) to PCM format for Realtime API using ffmpeg CLI
    
    Uses stdin/stdout piping to avoid temp file permission issues with snap
    
    Required format:
    - Sample rate: 24000 Hz
    - Channels: 1 (mono)
    - Sample width: 16-bit (2 bytes)
    - Encoding: PCM16 Little Endian
    
    Args:
        audio_bytes: Input audio bytes (OGG format)
        
    Returns:
        PCM audio bytes
    """
    try:
        # Use ffmpeg with stdin/stdout pipes (no temp files needed!)
        # -i pipe:0: read from stdin
        # -f s16le: output format (signed 16-bit little-endian PCM)
        # -ac 1: 1 audio channel (mono)
        # -ar 24000: sample rate 24kHz
        # pipe:1: write to stdout
        result = subprocess.run([
            'ffmpeg',
            '-i', 'pipe:0',  # Read from stdin
            '-f', 's16le',
            '-ac', '1',
            '-ar', '24000',
            '-loglevel', 'error',  # Only show errors
            'pipe:1'  # Write to stdout
        ], input=audio_bytes, capture_output=True, check=True)
        
        pcm_data = result.stdout
        logger.info(f" ffmpeg conversion successful: {len(pcm_data)} bytes")
        return pcm_data
        
    except subprocess.CalledProcessError as e:
        logger.error(f" ffmpeg conversion failed: {e.stderr.decode()}")
        raise Exception(f"Audio conversion failed: {e.stderr.decode()}")
    except Exception as e:
        logger.error(f" Error converting to PCM: {e}")
        raise


def convert_from_pcm(pcm_bytes: bytes) -> bytes:
    """
    Convert PCM audio to OGG format for WhatsApp using ffmpeg CLI
    
    Uses stdin/stdout piping to avoid temp file permission issues with snap
    Optimized for WhatsApp voice message waveform display
    
    Args:
        pcm_bytes: PCM audio bytes (24kHz, mono, 16-bit)
        
    Returns:
        OGG audio bytes (properly formatted for WhatsApp at 16kHz)
    """
    try:
        # Use ffmpeg with stdin/stdout pipes (no temp files needed!)
        # -f s16le: input format (signed 16-bit little-endian PCM)
        # -ar 24000: input sample rate (from Realtime API)
        # -ac 1: input channels (mono)
        # -i pipe:0: read from stdin
        # -ar 16000: RESAMPLE to 16kHz (WhatsApp standard for voice messages!)
        # -c:a libopus: use Opus codec (WhatsApp compatible)
        # -b:a 16k: bitrate optimized for 16kHz voice
        # -vbr on: variable bitrate for better quality
        # -compression_level 10: maximum compression quality
        # -frame_duration 60: 60ms frames (WhatsApp standard)
        # -application voip: optimize for voice (not music)
        # -f ogg: output format
        # pipe:1: write to stdout
        result = subprocess.run([
            'ffmpeg',
            '-f', 's16le',
            '-ar', '24000',  # Input is 24kHz from Realtime API
            '-ac', '1',
            '-i', 'pipe:0',  # Read from stdin
            '-ar', '16000',  # RESAMPLE to 16kHz for WhatsApp!
            '-c:a', 'libopus',
            '-b:a', '16k',  # Lower bitrate for 16kHz
            '-vbr', 'on',   # Variable bitrate
            '-compression_level', '10',  # Max quality
            '-frame_duration', '60',     # 60ms frames
            '-application', 'voip',      # Voice optimized
            '-f', 'ogg',
            '-loglevel', 'error',  # Only show errors
            'pipe:1'  # Write to stdout
        ], input=pcm_bytes, capture_output=True, check=True)
        
        ogg_data = result.stdout
        logger.info(f" ffmpeg conversion successful (16kHz): {len(ogg_data)} bytes")
        return ogg_data
        
    except subprocess.CalledProcessError as e:
        logger.error(f" ffmpeg conversion failed: {e.stderr.decode()}")
        raise Exception(f"Audio conversion failed: {e.stderr.decode()}")
    except Exception as e:
        logger.error(f" Error converting from PCM: {e}")
        raise


async def send_to_realtime_api(
    pcm_audio: bytes,
    user_phone: str,
    conversation_context: str = ""
) -> bytes:
    """
    Send audio to OpenAI Realtime API and receive response
    
    Args:
        pcm_audio: PCM audio bytes
        user_phone: User's phone number
        conversation_context: Previous conversation context
        
    Returns:
        Response PCM audio bytes
    """
    # Build WebSocket URL
    ws_url = f"{settings.REALTIME_API_URL}?model={settings.OPENAI_REALTIME_MODEL}"
    
    # Headers for authentication
    headers = {
        "Authorization": f"Bearer {settings.OPENAI_API_KEY}",
        "OpenAI-Beta": "realtime=v1"
    }
    
    response_audio_chunks: List[bytes] = []
    
    try:
        # Connect to WebSocket
        async with websockets.connect(ws_url, extra_headers=headers) as ws:
            logger.info(" Connected to Realtime API WebSocket")
            
            # Step 1: Configure session
            session_config = {
                "type": "session.update",
                "session": {
                    "modalities": ["audio", "text"],  # API requires both
                    "voice": settings.OPENAI_REALTIME_VOICE,
                    "instructions": build_instructions(user_phone, conversation_context),
                    "input_audio_format": "pcm16",
                    "output_audio_format": "pcm16",
                    "turn_detection": {
                        "type": "server_vad"
                    }
                }
            }
            await ws.send(json.dumps(session_config))
            logger.info("📤 Sent session configuration")
            
            # Step 2: Send audio input
            audio_b64 = base64.b64encode(pcm_audio).decode('utf-8')
            
            # Send in chunks if audio is large
            chunk_size = 8192  # Send 8KB at a time
            for i in range(0, len(audio_b64), chunk_size):
                chunk = audio_b64[i:i + chunk_size]
                append_event = {
                    "type": "input_audio_buffer.append",
                    "audio": chunk
                }
                await ws.send(json.dumps(append_event))
            
            logger.info("📤 Sent audio input")
            
            # Step 3: Wait for server VAD to detect end of speech
            # Server VAD will automatically commit the buffer and trigger response
            # No manual commit needed when using server_vad mode
            
            # Step 4: Receive response
            logger.info(" Waiting for server VAD to detect end of speech and generate response...")
            
            async for message in ws:
                try:
                    event = json.loads(message)
                    event_type = event.get("type")
                    
                    # Log events
                    if event_type == "session.created":
                        logger.info(" Session created")
                    elif event_type == "session.updated":
                        logger.info(" Session updated")
                    elif event_type == "input_audio_buffer.committed":
                        logger.info(" Audio committed")
                    elif event_type == "conversation.item.created":
                        logger.info(" Conversation item created")
                    elif event_type == "response.created":
                        logger.info(" Response created")
                    elif event_type == "response.output_item.added":
                        logger.info(" Output item added")
                    elif event_type == "response.content_part.added":
                        logger.info(" Content part added")
                    elif event_type == "response.audio_transcript.delta":
                        # Log transcription for debugging
                        transcript = event.get("delta", "")
                        logger.info(f"📝 Transcript: {transcript}")
                    elif event_type == "response.audio.delta":
                        # Receive audio chunks
                        audio_delta = event.get("delta")
                        if audio_delta:
                            audio_chunk = base64.b64decode(audio_delta)
                            response_audio_chunks.append(audio_chunk)
                            logger.debug(f" Received audio chunk: {len(audio_chunk)} bytes")
                    elif event_type == "response.audio.done":
                        logger.info(" Audio response complete")
                    elif event_type == "response.done":
                        logger.info(" Response done")
                        break
                    elif event_type == "error":
                        error_msg = event.get("error", {})
                        logger.error(f" API Error: {error_msg}")
                        raise Exception(f"Realtime API error: {error_msg}")
                    
                except json.JSONDecodeError:
                    logger.warning(f" Failed to parse message: {message}")
                    continue
        
        # Combine all audio chunks
        if not response_audio_chunks:
            raise Exception("No audio response received from API")
        
        combined_audio = b''.join(response_audio_chunks)
        logger.info(f" Combined {len(response_audio_chunks)} chunks into {len(combined_audio)} bytes")
        
        return combined_audio
        
    except websockets.exceptions.WebSocketException as e:
        logger.error(f" WebSocket error: {e}")
        raise
    except Exception as e:
        logger.error(f" Error in send_to_realtime_api: {e}")
        raise


def build_instructions(user_phone: str, conversation_context: str) -> str:
    """
    Build system instructions for the Realtime API
    
    Args:
        user_phone: User's phone number
        conversation_context: Previous conversation context
        
    Returns:
        Instructions string
    """
    instructions = """Je bent een AI-assistent voor een AI-automatiseringsbedrijf. Je helpt leads kwalificeren en vragen beantwoorden. Reageer ALTIJD in het Nederlands.

**FAQ KENNIS - Beantwoord deze vragen wanneer gevraagd:**

Q: Hoe ziet jullie proces eruit?
A: We werken met ontwikkelingskosten plus een maandelijkse onderhoudskosten.

Q: Wat doen jullie precies?
A: We bouwen AI-systemen voor bedrijven die hun bedrijf willen automatiseren en meer ruimte voor groei willen creëren.

Q: Wat maakt jullie anders dan andere bedrijven?
A: We bouwen onze eigen AI-systemen, implementeren twee keer zo snel in vergelijking met andere aanbieders, en bieden een 30-dagen resultatengarantie.

Q: Kunnen jullie integreren met onze bestaande systemen?
A: We kunnen naadloos integreren met uw huidige systemen.

**KWALIFICATIEPROCES:**
Wanneer een prospect interesse toont, zeg ALTIJD: "Ik heb een paar vragen die ik moet stellen om te zien of we u verder kunnen helpen."

Stel deze vragen dan ÉÉN VOOR ÉÉN (wacht op elk antwoord voordat je de volgende vraag stelt):
1. Met welk probleem wordt u momenteel geconfronteerd?
2. Wat verliest u aan geld en tijd?
3. Wat heeft u tot nu toe gedaan om dit probleem op te lossen?
4. Hoe ziet uw ideale oplossing eruit?
5. Hoeveel budget heeft u beschikbaar om dit probleem op te lossen?

**TOON & STIJL:**
- Wees vriendelijk, professioneel en beknopt (dit is een spraakgesprek)
- Houd antwoorden kort en duidelijk
- Stel kwalificatievragen natuurlijk in het gesprek
- Luister actief en erken hun antwoorden
- Stel niet alle vragen tegelijk - maak het conversationeel
- Reageer ALTIJD in het Nederlands, ongeacht de taal van de gebruiker"""
    
    if conversation_context:
        instructions += f"\n\nEerdere gesprekscontext:\n{conversation_context}"
    
    return instructions


# ========================
# Testing Functions
# ========================

async def test_connection():
    """Test WebSocket connection to Realtime API"""
    ws_url = f"{settings.REALTIME_API_URL}?model={settings.OPENAI_REALTIME_MODEL}"
    headers = {
        "Authorization": f"Bearer {settings.OPENAI_API_KEY}",
        "OpenAI-Beta": "realtime=v1"
    }
    
    try:
        async with websockets.connect(ws_url, extra_headers=headers) as ws:
            print(" Successfully connected to Realtime API")
            
            # Send session config
            config = {
                "type": "session.update",
                "session": {
                    "modalities": ["audio"],
                    "voice": settings.OPENAI_REALTIME_VOICE
                }
            }
            await ws.send(json.dumps(config))
            
            # Wait for response
            response = await ws.recv()
            event = json.loads(response)
            print(f" Received: {event.get('type')}")
            
    except Exception as e:
        print(f" Connection test failed: {e}")
        raise


if __name__ == "__main__":
    # Run connection test
    asyncio.run(test_connection())
