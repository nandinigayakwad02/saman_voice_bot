import logging
import subprocess
import io
from elevenlabs.client import ElevenLabs
from openai import AsyncOpenAI
from app.config import settings

logger = logging.getLogger(__name__)

# Initialize clients
elevenlabs_client = ElevenLabs(api_key=settings.ELEVENLABS_API_KEY)
openai_client = AsyncOpenAI(api_key=settings.OPENAI_API_KEY)


def add_natural_pauses(text: str) -> str:
    """
    Add natural speech pauses and breathing for human-like delivery
    (Minimal thinking sounds, but keep natural flow)
    
    Args:
        text: Original text
        
    Returns:
        Text with natural pauses and breathing
    """
    import re
    
    # KEPT: Breathing pauses at sentence ends (sounds human!)
    text = text.replace(". ", "... ")
    text = text.replace("! ", "... ")
    text = text.replace("? ", "... ")
    
    # KEPT: Light pauses after commas (natural breath points)
    text = text.replace(", ", "... ")
    
    # REDUCED thinking sounds (not removed!)
    # Add "uhm" only occasionally, not after every filler
    text = text.replace("Nou,", "Nou... ")  # Just pause, no uhm
    text = text.replace("Kijk,", "Kijk... ")  # Just pause
    text = text.replace("Dus,", "Dus... ")    # Just pause
    text = text.replace("Maar,", "Maar... ")  # Just pause
    
    # Add subtle thinking sound only at beginning if starts with certain words
    # This keeps it minimal but still human
    if text.startswith("Ja "):
        text = "Uhm... " + text
    elif text.startswith("Nou "):
        text = text.replace("Nou ", "Nou... uhm... ", 1)  # Only first occurrence
    
    # Keep natural pauses before "En" (breathing point)
    text = text.replace(" en ", "... en ")
    
    return text


def convert_text_to_speech_sync(text: str) -> bytes:
    """
    Convert text to speech using ElevenLabs API with custom cloned voice (sync)
    
    Args:
        text: Text to convert to speech
        
    Returns:
        Audio bytes in OGG format (WhatsApp compatible)
    """
    try:
        logger.info(f" Converting text to speech with ElevenLabs: {text[:50]}...")
        
        # Add natural pauses for human-like delivery
        text_with_pauses = add_natural_pauses(text)
        
        # Step 1: Call ElevenLabs TTS API with human-like settings
        audio_generator = elevenlabs_client.text_to_speech.convert(
            voice_id=settings.ELEVENLABS_VOICE_ID,
            text=text_with_pauses,
            model_id=settings.ELEVENLABS_MODEL,
            voice_settings={
                "stability": 0.3,           # LOW = more tonal variation, less monotone
                "similarity_boost": 0.8,    # Keep Saman's voice strong
                "style": 0.7,               # HIGH = more emotion and pitch variation
                "use_speaker_boost": True   # Better voice clarity
            }
        )
        
        # Collect all audio chunks
        mp3_bytes = b"".join(audio_generator)
        logger.info(f" ElevenLabs TTS response: {len(mp3_bytes)} bytes (MP3)")
        
        # Step 2: Convert MP3 to OGG for WhatsApp
        ogg_bytes = convert_mp3_to_ogg(mp3_bytes)
        logger.info(f" Converted to OGG: {len(ogg_bytes)} bytes")
        
        return ogg_bytes
        
    except Exception as e:
        logger.error(f" Error converting text to speech with ElevenLabs: {e}")
        raise


def convert_mp3_to_ogg(mp3_bytes: bytes) -> bytes:
    """
    Convert MP3 audio to OGG/Opus format for WhatsApp
    
    Uses ffmpeg with stdin/stdout piping (similar to realtime_voice.py)
    Optimized for WhatsApp voice message waveform display
    
    Args:
        mp3_bytes: MP3 audio bytes from TTS API
        
    Returns:
        OGG audio bytes (16kHz, Opus codec)
    """
    try:
        # Use ffmpeg with stdin/stdout pipes
        # -i pipe:0: read MP3 from stdin
        # -ar 16000: resample to 16kHz (WhatsApp voice message standard)
        # -c:a libopus: use Opus codec
        # -b:a 16k: bitrate optimized for 16kHz voice
        # -vbr on: variable bitrate for better quality
        # -compression_level 10: maximum compression quality
        # -frame_duration 60: 60ms frames (WhatsApp standard)
        # -application voip: optimize for voice
        # -f ogg: output format
        # pipe:1: write to stdout
        result = subprocess.run([
            'ffmpeg',
            '-i', 'pipe:0',  # Read MP3 from stdin
            '-af', 'atempo=1.25',  # Speed up 1.25x (Dutch speaking pace)
            '-ar', '16000',  # WhatsApp voice standard: 16kHz
            '-c:a', 'libopus',
            '-b:a', '16k',
            '-vbr', 'on',
            '-compression_level', '10',
            '-frame_duration', '60',
            '-application', 'voip',
            '-f', 'ogg',
            '-loglevel', 'error',  # Only show errors
            'pipe:1'  # Write to stdout
        ], input=mp3_bytes, capture_output=True, check=True)
        
        ogg_data = result.stdout
        logger.info(f" ffmpeg MP3→OGG conversion successful: {len(ogg_data)} bytes")
        return ogg_data
        
    except subprocess.CalledProcessError as e:
        logger.error(f" ffmpeg conversion failed: {e.stderr.decode()}")
        raise Exception(f"Audio conversion failed: {e.stderr.decode()}")
    except Exception as e:
        logger.error(f" Error converting MP3 to OGG: {e}")
        raise


async def convert_text_to_speech_with_cleanup(text: str, max_length: int = 4000) -> bytes:
    """
    Convert text to speech with text cleanup and length limits
    
    Removes emojis and truncates long text to fit TTS API limits
    
    Args:
        text: Text to convert
        max_length: Maximum character length (TTS API limit is 4096)
        
    Returns:
        Audio bytes in OGG format
    """
    # Remove or replace emojis for better pronunciation
    import re
    cleaned_text = re.sub(r'[^\w\s.,!?;:\-\'\"()]', '', text)
    
    # Truncate if too long
    if len(cleaned_text) > max_length:
        cleaned_text = cleaned_text[:max_length] + "..."
        logger.warning(f" Text truncated to {max_length} characters")
    
    # Call sync function (ElevenLabs is synchronous)
    return convert_text_to_speech_sync(cleaned_text)


async def transcribe_audio(audio_bytes: bytes) -> str:
    """
    Transcribe audio to text using OpenAI Whisper
    
    Args:
        audio_bytes: Audio bytes (OGG format from WhatsApp)
        
    Returns:
        Transcribed text
    """
    try:
        logger.info(f" Transcribing audio with Whisper: {len(audio_bytes)} bytes")
        
        # Create file-like object for Whisper API
        audio_file = io.BytesIO(audio_bytes)
        audio_file.name = "voice.ogg"
        
        # Transcribe using Whisper
        transcription = await openai_client.audio.transcriptions.create(
            model="whisper-1",
            file=audio_file
        )
        
        transcribed_text = transcription.text
        logger.info(f" Transcription: {transcribed_text[:100]}...")
        
        return transcribed_text
        
    except Exception as e:
        logger.error(f" Error transcribing audio: {e}")
        raise
