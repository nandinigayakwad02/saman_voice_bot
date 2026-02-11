# Deployment Guide for DevOps

## 📋 Quick Overview
WhatsApp AI Voice Bot with OpenAI Realtime API and ElevenLabs custom voice integration.

---

## 🔧 System Requirements

### Required Software:
```bash
- Python 3.10 or 3.11
- FFmpeg (for audio conversion)
- pip
```

### Installation (Ubuntu/Debian):
```bash
sudo apt update
sudo apt install python3 python3-pip ffmpeg -y
```

---

## 🚀 Deployment Steps

### 1. Clone Repository
```bash
git clone https://github.com/YOUR_REPO_URL.git
cd Josh_voice_bot
```

### 2. Create Virtual Environment (Recommended)
```bash
python3 -m venv venv
source venv/bin/activate  # Linux/Mac
```

### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

### 4. Create `.env` File
```bash
cp .env.example .env
nano .env  # Edit with actual API keys
```

**Required Environment Variables:**
```env
# WhatsApp Business API
WHATSAPP_PHONE_NUMBER_ID=your_phone_id
WHATSAPP_BUSINESS_ACCOUNT_ID=your_account_id
WHATSAPP_ACCESS_TOKEN=your_access_token

# Webhook
WEBHOOK_VERIFY_TOKEN=whatsapp_ai_chatbot_2026

# OpenAI
OPENAI_API_KEY=your_openai_key
OPENAI_MODEL=gpt-4o-mini

# ElevenLabs (Custom Voice)
ELEVENLABS_API_KEY=your_elevenlabs_key
ELEVENLABS_VOICE_ID=your_voice_id

# Server
HOST=0.0.0.0
PORT=8000
DEBUG=False
```

### 5. Run Application
```bash
python3 run.py
```

**Or with nohup (background):**
```bash
nohup python3 run.py > app.log 2>&1 &
```

---

## 🌐 Production Setup

### Option 1: With Process Manager (PM2 - Recommended)
```bash
# Install PM2
npm install pm2 -g

# Start app
pm2 start run.py --name whatsapp-bot --interpreter python3

# Auto-restart on reboot
pm2 startup
pm2 save
```

### Option 2: With Systemd Service
Create `/etc/systemd/system/whatsapp-bot.service`:
```ini
[Unit]
Description=WhatsApp AI Voice Bot
After=network.target

[Service]
Type=simple
User=your_user
WorkingDirectory=/path/to/Josh_voice_bot
Environment="PATH=/path/to/Josh_voice_bot/venv/bin"
ExecStart=/path/to/Josh_voice_bot/venv/bin/python run.py
Restart=always

[Install]
WantedBy=multi-user.target
```

Enable and start:
```bash
sudo systemctl daemon-reload
sudo systemctl enable whatsapp-bot
sudo systemctl start whatsapp-bot
```

### Option 3: With Nginx Reverse Proxy
```nginx
server {
    listen 80;
    server_name yourdomain.com;

    location / {
        proxy_pass http://localhost:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
```

---

## 🔒 SSL/HTTPS Setup (For Production)

### With Certbot (Let's Encrypt):
```bash
sudo apt install certbot python3-certbot-nginx
sudo certbot --nginx -d yourdomain.com
```

---

## ⚙️ WhatsApp Webhook Configuration

After deployment, update Meta Developer Dashboard:

**Callback URL:**
```
https://yourdomain.com/webhook
# or
http://YOUR_SERVER_IP:8000/webhook
```

**Verify Token:**
```
whatsapp_ai_chatbot_2026
```

**Subscribe to:** `messages`

---

## 📊 Health Check

Test if server is running:
```bash
curl http://localhost:8000/health
```

Expected response:
```json
{"status":"healthy","timestamp":"..."}
```

---

## 📝 Important Notes

1. **FFmpeg is Critical:** Audio conversion won't work without it
2. **Port 8000:** Must be open in firewall
3. **Environment Variables:** Never commit `.env` to GitHub
4. **API Keys:** Keep secure, use environment variables
5. **Logs:** Check `app.log` or use `pm2 logs whatsapp-bot`

---

## 🐛 Troubleshooting

### Check if running:
```bash
ps aux | grep run.py
netstat -tulpn | grep 8000
```

### View logs:
```bash
# If using nohup
tail -f app.log

# If using PM2
pm2 logs whatsapp-bot

# If using systemd
sudo journalctl -u whatsapp-bot -f
```

### Restart:
```bash
# PM2
pm2 restart whatsapp-bot

# Systemd
sudo systemctl restart whatsapp-bot
```

---

## 📞 Support

For issues, check:
- Application logs
- FFmpeg installation: `ffmpeg -version`
- Port availability: `netstat -tulpn | grep 8000`
- Environment variables: Are all API keys set?

---

## ✅ Quick Deployment Checklist

- [ ] Python 3.10/3.11 installed
- [ ] FFmpeg installed
- [ ] Repository cloned
- [ ] Virtual environment created
- [ ] Dependencies installed (`pip install -r requirements.txt`)
- [ ] `.env` file created with all API keys
- [ ] Application started (`python3 run.py`)
- [ ] Port 8000 accessible
- [ ] Health check passed (`/health` endpoint)
- [ ] WhatsApp webhook configured in Meta Dashboard
- [ ] Test message sent and received

---

**Server URL format:** `http://YOUR_IP:8000/webhook` or `https://yourdomain.com/webhook`
