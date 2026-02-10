import httpx
import logging
import io
from typing import Dict, Optional, Any
from app.config import settings

logger = logging.getLogger(__name__)


class WhatsAppClient:
    """WhatsApp Business API Client"""
    
    def __init__(self):
        self.base_url = settings.whatsapp_api_base_url
        self.phone_number_id = settings.WHATSAPP_PHONE_NUMBER_ID
        self.access_token = settings.WHATSAPP_ACCESS_TOKEN
        self.headers = {
            "Authorization": f"Bearer {self.access_token}",
            "Content-Type": "application/json"
        }
    
    async def send_text_message(
        self, 
        to: str, 
        message: str,
        preview_url: bool = False
    ) -> Dict[str, Any]:
        """
        Send a text message via WhatsApp
        
        Args:
            to: Recipient phone number (with country code, no + sign)
            message: Message text
            preview_url: Whether to show URL preview
            
        Returns:
            API response dict
        """
        # Clean phone number (remove + and spaces)
        to = to.replace("+", "").replace(" ", "").replace("-", "")
        
        url = f"{self.base_url}/{self.phone_number_id}/messages"
        
        payload = {
            "messaging_product": "whatsapp",
            "recipient_type": "individual",
            "to": to,
            "type": "text",
            "text": {
                "preview_url": preview_url,
                "body": message
            }
        }
        
        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    url,
                    json=payload,
                    headers=self.headers,
                    timeout=30.0
                )
                response.raise_for_status()
                result = response.json()
                logger.info(f" Message sent to {to}: {result}")
                return result
        except httpx.HTTPError as e:
            logger.error(f" Failed to send message to {to}: {e}")
            if hasattr(e, 'response') and e.response is not None:
                logger.error(f"Response: {e.response.text}")
            raise
    
    async def send_template_message(
        self,
        to: str,
        template_name: str,
        language_code: str = "en_US",
        components: Optional[list] = None
    ) -> Dict[str, Any]:
        """
        Send a template message via WhatsApp
        
        Args:
            to: Recipient phone number
            template_name: Name of the approved template
            language_code: Template language code
            components: Template components (parameters)
            
        Returns:
            API response dict
        """
        to = to.replace("+", "").replace(" ", "").replace("-", "")
        
        url = f"{self.base_url}/{self.phone_number_id}/messages"
        
        payload = {
            "messaging_product": "whatsapp",
            "to": to,
            "type": "template",
            "template": {
                "name": template_name,
                "language": {
                    "code": language_code
                }
            }
        }
        
        if components:
            payload["template"]["components"] = components
        
        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    url,
                    json=payload,
                    headers=self.headers,
                    timeout=30.0
                )
                response.raise_for_status()
                result = response.json()
                logger.info(f" Template message sent to {to}: {result}")
                return result
        except httpx.HTTPError as e:
            logger.error(f" Failed to send template message to {to}: {e}")
            if hasattr(e, 'response') and e.response is not None:
                logger.error(f"Response: {e.response.text}")
            raise
    
    async def mark_message_as_read(self, message_id: str) -> Dict[str, Any]:
        """Mark a message as read"""
        url = f"{self.base_url}/{self.phone_number_id}/messages"
        
        payload = {
            "messaging_product": "whatsapp",
            "status": "read",
            "message_id": message_id
        }
        
        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    url,
                    json=payload,
                    headers=self.headers,
                    timeout=30.0
                )
                response.raise_for_status()
                return response.json()
        except httpx.HTTPError as e:
            logger.error(f" Failed to mark message as read: {e}")
            raise
    
    async def download_media(self, media_id: str) -> bytes:
        """
        Download media file from WhatsApp
        
        Args:
            media_id: WhatsApp media ID
            
        Returns:
            Media file bytes
        """
        try:
            # Step 1: Get media URL
            url = f"{self.base_url}/{media_id}"
            
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    url,
                    headers=self.headers,
                    timeout=30.0
                )
                response.raise_for_status()
                media_info = response.json()
                
                media_url = media_info.get("url")
                if not media_url:
                    raise Exception("No URL found in media info")
                
                logger.info(f" Downloading media from: {media_url}")
                
                # Step 2: Download media file
                media_response = await client.get(
                    media_url,
                    headers=self.headers,
                    timeout=60.0
                )
                media_response.raise_for_status()
                
                media_bytes = media_response.content
                logger.info(f" Downloaded {len(media_bytes)} bytes")
                return media_bytes
                
        except httpx.HTTPError as e:
            logger.error(f" Failed to download media {media_id}: {e}")
            if hasattr(e, 'response') and e.response is not None:
                logger.error(f"Response: {e.response.text}")
            raise
    
    async def send_audio_message(
        self,
        to: str,
        audio_bytes: bytes,
        filename: str = "voice_message.ogg"
    ) -> Dict[str, Any]:
        """
        Send an audio/voice message via WhatsApp
        
        Args:
            to: Recipient phone number
            audio_bytes: Audio file bytes (OGG format)
            filename: Filename for the audio
            
        Returns:
            API response dict
        """
        to = to.replace("+", "").replace(" ", "").replace("-", "")
        
        try:
            # Step 1: Upload media to WhatsApp
            upload_url = f"{self.base_url}/{self.phone_number_id}/media"
            
            # Create file-like object from bytes
            # IMPORTANT: MIME type must be 'audio/ogg; codecs=opus' for waveform display!
            files = {
                'file': (filename, io.BytesIO(audio_bytes), 'audio/ogg; codecs=opus')
            }
            
            upload_headers = {
                "Authorization": f"Bearer {self.access_token}"
            }
            
            async with httpx.AsyncClient() as client:
                # Upload media
                upload_response = await client.post(
                    upload_url,
                    files=files,
                    headers=upload_headers,
                    data={"messaging_product": "whatsapp"},
                    timeout=60.0
                )
                upload_response.raise_for_status()
                upload_result = upload_response.json()
                
                media_id = upload_result.get("id")
                if not media_id:
                    raise Exception("No media ID in upload response")
                
                logger.info(f"📤 Uploaded audio, media_id: {media_id}")
                
                # Step 2: Send audio message
                message_url = f"{self.base_url}/{self.phone_number_id}/messages"
                
                payload = {
                    "messaging_product": "whatsapp",
                    "recipient_type": "individual",
                    "to": to,
                    "type": "audio",
                    "audio": {
                        "id": media_id,
                        "voice": True  # THIS enables waveform display!
                    }
                }
                
                message_response = await client.post(
                    message_url,
                    json=payload,
                    headers=self.headers,
                    timeout=30.0
                )
                message_response.raise_for_status()
                result = message_response.json()
                
                logger.info(f" Audio message sent to {to}: {result}")
                return result
                
        except httpx.HTTPError as e:
            logger.error(f" Failed to send audio message to {to}: {e}")
            if hasattr(e, 'response') and e.response is not None:
                logger.error(f"Response: {e.response.text}")
            raise


# Global WhatsApp client instance
whatsapp_client = WhatsAppClient()
