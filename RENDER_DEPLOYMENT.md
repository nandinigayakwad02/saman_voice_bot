# 🚀 Render Deployment Guide

## Quick Render Deployment

This guide will help you deploy your WhatsApp Voice Bot to Render.com

---

## Prerequisites

✅ GitHub repository with your code pushed
✅ Render.com account (free tier available)
✅ All API keys ready (WhatsApp, OpenAI, ElevenLabs)

---

## Step 1: Prepare Your Repository

### Ensure these files exist in your repo:

1. **`requirements.txt`** ✅ (Already exists)
2. **`Dockerfile`** ✅ (Already exists)
3. **`run.py`** ✅ (Already exists)

---

## Step 2: Create Web Service on Render

### 1. Go to Render Dashboard
- Visit: https://dashboard.render.com
- Click **"New +"** → **"Web Service"**

### 2. Connect GitHub Repository
- Select your repository: `Josh_voice_bot`
- Click **"Connect"**

### 3. Configure Web Service

**Basic Settings:**
```
Name: whatsapp-voice-bot
Region: Choose closest to you (e.g., Frankfurt, Singapore)
Branch: main (or your default branch)
Root Directory: (leave blank if project is at root)
```

**Build & Deploy:**
```
Environment: Docker
Docker Command: (auto-detected from Dockerfile)
```

**Instance Type:**
```
Instance Type: Free (or Starter $7/month for better performance)
```

---

## Step 3: Set Environment Variables

Click **"Environment"** tab and add ALL these variables:

### WhatsApp Business API
```
WHATSAPP_API_VERSION = v21.0
WHATSAPP_PHONE_NUMBER_ID = your_phone_number_id
WHATSAPP_BUSINESS_ACCOUNT_ID = your_business_account_id
WHATSAPP_ACCESS_TOKEN = your_access_token
```

### App Configuration
```
APP_ID = your_app_id
APP_SECRET = your_app_secret
WEBHOOK_VERIFY_TOKEN = your_custom_token
```

### OpenAI
```
OPENAI_API_KEY = sk-proj-...
OPENAI_MODEL = gpt-4o-mini
```

### ElevenLabs
```
ELEVENLABS_API_KEY = sk_...
ELEVENLABS_VOICE_ID = z2YAcEg2WAOLmMypdEBu
ELEVENLABS_MODEL = eleven_multilingual_v2
```

### Server Configuration
```
HOST = 0.0.0.0
PORT = 10000
DEBUG = False
LOG_LEVEL = INFO
PRODUCTION = True
```

### Production Features
```
REDIS_URL = (leave blank for now, add later if needed)
REDIS_TTL = 3600
```

### Authorized Users
```
ALLOWED_PHONE_NUMBERS = 918226053534,919876543210
```

---

## Step 4: Update Port in Files

Render uses port `10000` by default. Update your `run.py`:

```python
if __name__ == "__main__":
    import os
    port = int(os.getenv("PORT", 8000))  # Uses Render's PORT env var
    
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=port,
        reload=False,
        log_level="info"
    )
```

---

## Step 5: Deploy

1. Click **"Create Web Service"**
2. Wait for build to complete (5-10 minutes)
3. Check logs for any errors

---

## Step 6: Get Your Webhook URL

After deployment, Render will give you a URL like:
```
https://whatsapp-voice-bot-xxxx.onrender.com
```

Your webhook URL will be:
```
https://whatsapp-voice-bot-xxxx.onrender.com/webhook
```

---

## Step 7: Configure WhatsApp Webhook

1. Go to **Meta Developer Dashboard**
2. Navigate to: WhatsApp → Configuration
3. Click **"Edit"** under Webhook

**Callback URL:**
```
https://whatsapp-voice-bot-xxxx.onrender.com/webhook
```

**Verify Token:**
```
your_custom_token (same as WEBHOOK_VERIFY_TOKEN)
```

4. Click **"Verify and Save"**
5. Subscribe to: **messages**

---

## Step 8: Test Your Bot

### 1. Health Check
```bash
curl https://whatsapp-voice-bot-xxxx.onrender.com/health
```

Expected response:
```json
{"status":"healthy","timestamp":"..."}
```

### 2. Send WhatsApp Message
Send a text or voice message from an authorized number to your WhatsApp Business number.

Expected: Dutch voice response in Saman's voice

---

## 🔧 Render-Specific Configuration

### Update `run.py` for Render:

```python
"""
Entry point for running the WhatsApp AI Chatbot
"""
import os
import uvicorn
from app.config import settings


if __name__ == "__main__":
    # Render provides PORT environment variable
    port = int(os.getenv("PORT", settings.PORT))
    
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=port,
        reload=False,  # Never use reload in production
        log_level="info"
    )
```

### Ensure Dockerfile is optimized:

```dockerfile
FROM python:3.10-slim

# Install FFmpeg
RUN apt-get update && apt-get install -y ffmpeg && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Copy requirements
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy application
COPY . .

# Expose port (Render will override with PORT env var)
EXPOSE 10000

# Run application
CMD ["python3", "run.py"]
```

---

## 🐛 Troubleshooting

### Build Fails

**Issue**: Dependencies not installing
```bash
Solution: Check requirements.txt syntax
         Ensure all packages are available on PyPI
```

**Issue**: FFmpeg not found
```bash
Solution: Verify Dockerfile has:
         RUN apt-get install -y ffmpeg
```

### Webhook Verification Fails

**Issue**: "Verification failed"
```bash
Solution: 
1. Check WEBHOOK_VERIFY_TOKEN matches in:
   - Render environment variables
   - Meta Developer Dashboard
2. Ensure URL is correct: https://your-app.onrender.com/webhook
```

### Bot Not Responding

**Issue**: Messages not being processed
```bash
Solution:
1. Check Render logs: Dashboard → Your Service → Logs
2. Verify ALLOWED_PHONE_NUMBERS includes sender
3. Test health endpoint
4. Check all API keys are correct
```

### Free Tier Sleep

**Issue**: Render free tier sleeps after 15 min inactivity
```bash
Solution:
1. Upgrade to Starter plan ($7/month) for 24/7 uptime
2. Or use external service to ping your app every 10 min
```

---

## 📊 Monitoring

### View Logs
```
Render Dashboard → Your Service → Logs
```

### Check Metrics
```
Render Dashboard → Your Service → Metrics
```

### Set Up Alerts
```
Render Dashboard → Your Service → Settings → Notifications
```

---

## 💰 Cost Breakdown

### Render
```
Free Tier:
- 750 hours/month
- Sleeps after 15 min inactivity
- 512 MB RAM
- Cost: FREE

Starter:
- Always on
- 512 MB RAM
- Cost: $7/month
```

### API Costs
```
OpenAI:
- GPT-4o-mini: ~$0.00015 per message
- Whisper: ~$0.006 per voice message

ElevenLabs:
- ~$0.18 per 1000 characters
- Free tier: 10,000 chars/month

Total estimated: $5-20/month depending on usage
```

---

## ✅ Deployment Checklist

- [ ] Code pushed to GitHub
- [ ] Render account created
- [ ] Web service created
- [ ] All environment variables added
- [ ] PORT handling added to run.py
- [ ] Build successful
- [ ] Health check passed
- [ ] Webhook URL configured in Meta Dashboard
- [ ] Webhook verified successfully
- [ ] Test message sent and received
- [ ] Logs checked for errors

---

## 🚀 Quick Deploy Commands

### Push to GitHub
```bash
git add .
git commit -m "feat: render deployment"
git push origin main
```

### Trigger Redeploy on Render
```
Dashboard → Manual Deploy → Deploy latest commit
```

### Update Environment Variables
```
Dashboard → Environment → Add/Edit → Save Changes
```

---

## 📝 Important Notes

1. **Port**: Render automatically sets `PORT` env var to 10000
2. **HTTPS**: Render provides free SSL certificate automatically
3. **Logs**: Available in real-time on Render dashboard
4. **Restart**: Auto-restarts on crash
5. **Sleep**: Free tier sleeps after 15 min inactivity (first request takes 30s)

---

## 🔗 Useful Links

- **Render Dashboard**: https://dashboard.render.com
- **Render Docs**: https://render.com/docs
- **Your App Logs**: Dashboard → Logs
- **Environment Vars**: Dashboard → Environment

---

## 🆘 Support

If deployment fails:

1. **Check Render build logs** for errors
2. **Verify all environment variables** are set correctly
3. **Test locally** with Docker first:
   ```bash
   docker build -t whatsapp-bot .
   docker run -p 10000:10000 --env-file .env whatsapp-bot
   ```
4. **Check Meta webhook** is pointing to correct URL

---

**Your Render URL**: `https://whatsapp-voice-bot-xxxx.onrender.com/webhook`

**🎉 Your bot is now live on Render!** 🇳🇱
