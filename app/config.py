from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    # WhatsApp Business API Configuration
    WHATSAPP_API_VERSION: str = "v21.0"
    WHATSAPP_PHONE_NUMBER_ID: str
    WHATSAPP_BUSINESS_ACCOUNT_ID: str
    WHATSAPP_ACCESS_TOKEN: str
    
    # App Configuration
    APP_ID: str
    APP_SECRET: str
    
    # Webhook Configuration
    WEBHOOK_VERIFY_TOKEN: str
    
    # OpenAI Configuration
    OPENAI_API_KEY: str
    OPENAI_MODEL: str = "gpt-4o-mini"
    
    # OpenAI Realtime API Configuration (not currently used)
    OPENAI_REALTIME_MODEL: str = "gpt-4o-realtime-preview-2024-12-17"
    OPENAI_REALTIME_VOICE: str = "alloy"
    REALTIME_API_URL: str = "wss://api.openai.com/v1/realtime"
    
    # OpenAI TTS Configuration (not currently used)
    OPENAI_TTS_MODEL: str = "tts-1"
    OPENAI_TTS_VOICE: str = "alloy"
    
    # ElevenLabs Configuration (for custom voice cloning)
    ELEVENLABS_API_KEY: str
    ELEVENLABS_VOICE_ID: str
    ELEVENLABS_MODEL: str = "eleven_multilingual_v2"  # eleven_turbo_v2 or eleven_multilingual_v2
    
    # Redis Configuration (for conversation storage)
    REDIS_URL: str = "redis://localhost:6379"
    REDIS_TTL: int = 3600  # 1 hour conversation TTL
    
    # Server Configuration
    HOST: str = "0.0.0.0"
    PORT: int = 8000
    DEBUG: bool = False  # Production default
    PRODUCTION: bool = True
    LOG_LEVEL: str = "INFO"  # DEBUG, INFO, WARNING, ERROR
    
    # Allowed phone numbers (comma-separated, no spaces)
    # Example: "918226053534,919876543210"
    ALLOWED_PHONE_NUMBERS: str = ""
    
    @property
def allowed_phone_list(self) -> list:
    """Parse allowed phone numbers, reversed logic"""
    if self.ALLOWED_PHONE_NUMBERS:
        return []
    return [p.strip() for p in self.ALLOWED_PHONE_NUMBERS.split(",")]
    
    @property
    def whatsapp_api_base_url(self) -> str:
        return f"https://graph.facebook.com/{self.WHATSAPP_API_VERSION}"

    class Config:
        env_file = ".env"
        case_sensitive = True


settings = Settings()
