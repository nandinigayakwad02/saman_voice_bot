# 🚀 WhatsApp Voice Bot - Setup & Run Guide

## Quick Start

```bash
# 1. Install dependencies with uv (fast!)
uv venv
source .venv/bin/activate
uv pip install -r requirements.txt

# 2. Configure environment
cp .env.example .env
# Edit .env with your API keys

# 3. Run the bot
python3 run.py
```

---

## Prerequisites

### Required
- **Python 3.10+**
- **uv** (fast Python package installer) - Install: `pip install uv`
- **ffmpeg** - For audio processing
  ```bash
  # Ubuntu/Debian
  sudo apt install ffmpeg
  
  # macOS
  brew install ffmpeg
  ```

### API Keys
1. **WhatsApp Business API** (Meta)
   - Phone Number ID
   - Business Account ID
   - Access Token
   - Webhook Verify Token

2. **OpenAI API Key**
   - For GPT-4o-mini (chat)
   - For Whisper (voice transcription)

3. **ElevenLabs API Key**
   - Voice ID (Saman's cloned voice)

---

## Installation Steps

### Method 1: Using `uv` (Recommended - Fast!)

```bash
# Navigate to project
cd /home/pc/Documents/Nitu\'s\ folder/Josh_voice_bot

# Create virtual environment
uv venv

# Activate virtual environment
source .venv/bin/activate

# Install all dependencies
uv pip install -r requirements.txt
```

### Method 2: Using `pip`

```bash
# Create virtual environment
python3 -m venv venv

# Activate
source venv/bin/activate

# Install
pip install -r requirements.txt
```

---

## Configuration

### 1. Environment Variables (`.env`)

```bash
# WhatsApp Business API
WHATSAPP_API_VERSION=v21.0
WHATSAPP_PHONE_NUMBER_ID=your_phone_number_id
WHATSAPP_BUSINESS_ACCOUNT_ID=your_business_account_id
WHATSAPP_ACCESS_TOKEN=your_access_token

# App Configuration
APP_ID=your_app_id
APP_SECRET=your_app_secret
WEBHOOK_VERIFY_TOKEN=your_custom_token

# OpenAI
OPENAI_API_KEY=sk-proj-...
OPENAI_MODEL=gpt-4o-mini

# ElevenLabs (Saman's Voice)
ELEVENLABS_API_KEY=sk_...
ELEVENLABS_VOICE_ID=z2YAcEg2WAOLmMypdEBu
ELEVENLABS_MODEL=eleven_multilingual_v2

# Server
HOST=0.0.0.0
PORT=8000
DEBUG=False
LOG_LEVEL=INFO
PRODUCTION=True

# Redis (optional - for scalability)
REDIS_URL=redis://localhost:6379
REDIS_TTL=3600

# Authorized Users (comma-separated phone numbers)
ALLOWED_PHONE_NUMBERS=918226053534,919876543210
```

---

## Running the Bot

### Development Mode

```bash
# Activate virtual environment
source .venv/bin/activate  # or: source venv/bin/activate

# Run with auto-reload
python3 run.py
```

### Production Mode

```bash
# Update .env
DEBUG=False
PRODUCTION=True

# Run
python3 run.py
```

### Using systemd (Production)

Create `/etc/systemd/system/whatsapp-bot.service`:

```ini
[Unit]
Description=WhatsApp Voice Bot
After=network.target

[Service]
Type=simple
User=your_username
WorkingDirectory=/path/to/Josh_voice_bot
Environment="PATH=/path/to/Josh_voice_bot/.venv/bin"
ExecStart=/path/to/Josh_voice_bot/.venv/bin/python3 run.py
Restart=always

[Install]
WantedBy=multi-user.target
```

Enable and start:
```bash
sudo systemctl enable whatsapp-bot
sudo systemctl start whatsapp-bot
sudo systemctl status whatsapp-bot
```

---

## Exposing to Internet

### Option 1: LocalTunnel (Development)

```bash
# Install
npm install -g localtunnel

# Run (in separate terminal)
lt --port 8000
```

### Option 2: Ngrok (Development)

```bash
ngrok http 8000
```

### Option 3: Production Server

Deploy to a cloud server with a public IP:
- AWS EC2
- DigitalOcean Droplet
- Google Cloud Compute
- Any VPS

---

## Testing

### 1. Check Server Health

```bash
curl http://localhost:8000/health
```

### 2. Send Test Message

```bash
curl -X POST http://localhost:8000/test/send
```

### 3. Test WhatsApp Messages

Send messages to your bot:
- **Text**: "Wat doen jullie precies?"
- **Voice**: 🎤 Record any question

Expected: Dutch voice response in Saman's voice

---

## Troubleshooting

### Module Not Found Errors

```bash
# Reinstall dependencies
source .venv/bin/activate
uv pip install -r requirements.txt --force-reinstall
```

### Pydantic Version Conflicts

```bash
# Install exact versions
uv pip install pydantic==2.12.5 pydantic-core==2.41.5 pydantic-settings==2.12.0
```

### FFmpeg Not Found

```bash
# Ubuntu
sudo apt update && sudo apt install ffmpeg

# macOS
brew install ffmpeg

# Verify
ffmpeg -version
```

### Permission Errors

```bash
# Fix permissions
chmod +x run.py
```

---

## Project Structure

```
Josh_voice_bot/
├── app/
│   ├── __init__.py
│   ├── main.py              # FastAPI app
│   ├── config.py            # Settings
│   ├── ai_agent.py          # Dutch FAQ bot
│   ├── tts_converter.py     # Whisper + ElevenLabs
│   ├── whatsapp.py          # WhatsApp API client
│   └── realtime_voice.py    # (unused - legacy)
├── .env                     # Configuration (DO NOT COMMIT!)
├── .gitignore
├── requirements.txt         # Dependencies
├── run.py                   # Entry point
└── README.md
```

---

## Key Features

✅ **Text Messages** → Dutch voice response (Saman's voice)
✅ **Voice Messages** → Dutch voice response (Saman's voice)
✅ **Authorized users only** (configurable)
✅ **Dutch-only responses** (all inputs)
✅ **FAQ knowledge base**
✅ **Lead qualification questions**
✅ **Silent processing** (no status messages)

---

## API Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/` | GET | Health check |
| `/health` | GET | Server status |
| `/webhook` | GET | WhatsApp verification |
| `/webhook` | POST | Receive messages |
| `/test/send` | POST | Send test message |
| `/conversation/clear` | POST | Clear history |

---

## Logs

```bash
# View logs (if using systemd)
sudo journalctl -u whatsapp-bot -f

# Or check terminal output
# Logs show:
# - Message received
# - Transcription
# - AI response
# - Voice generation
# - Errors (if any)
```

---

## Support

**Common Issues:**
1. **Bot not responding** → Check ALLOWED_PHONE_NUMBERS in .env
2. **Wrong voice** → Verify ELEVENLABS_VOICE_ID
3. **Not in Dutch** → Check ai_agent.py system prompt
4. **Webhook errors** → Verify WEBHOOK_VERIFY_TOKEN matches Meta

---

## Quick Commands Cheat Sheet

```bash
# Setup
uv venv && source .venv/bin/activate && uv pip install -r requirements.txt

# Run
python3 run.py

# Expose (dev)
lt --port 8000

# Clear conversations
curl -X POST http://localhost:8000/conversation/clear -d '{"phone":"918226053534"}'

# View health
curl http://localhost:8000/health
```

---

**🎉 Your WhatsApp Voice Bot is ready!** 🇳🇱
