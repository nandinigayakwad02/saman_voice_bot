"""
Entry point for running the WhatsApp AI Chatbot
"""
import os
import uvicorn
from app.config import settings


if __name__ == "__main__":
    # Render provides PORT environment variable
    # Use it if available, otherwise fall back to settings.PORT
    port = int(os.getenv("PORT", settings.PORT))
    
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=port,
        reload=False,  # Never use reload in production
        log_level="info"
    )
