# Docker Deployment Guide

## 📦 Quick Start

### 1. Build Docker Image

```bash
docker build -t josh-voice-bot:latest .
```

### 2. Run with Docker

```bash
docker run -d \
  --name josh-voice-bot \
  -p 8000:8000 \
  --env-file .env \
  -v $(pwd)/invoice_data:/app/invoice_data \
  josh-voice-bot:latest
```

### 3. Run with Docker Compose (Recommended)

```bash
# Start services
docker-compose up -d

# View logs
docker-compose logs -f

# Stop services
docker-compose down
```

---

## 🔧 Docker Commands

### Build & Run

```bash
# Build image
docker build -t josh-voice-bot:latest .

# Run container
docker run -d \
  --name josh-voice-bot \
  -p 8000:8000 \
  --env-file .env \
  josh-voice-bot:latest

# Run with volume mount
docker run -d \
  --name josh-voice-bot \
  -p 8000:8000 \
  --env-file .env \
  -v $(pwd)/invoice_data:/app/invoice_data \
  josh-voice-bot:latest
```

### Management

```bash
# View logs
docker logs -f josh-voice-bot

# Stop container
docker stop josh-voice-bot

# Start container
docker start josh-voice-bot

# Restart container
docker restart josh-voice-bot

# Remove container
docker rm -f josh-voice-bot

# Remove image
docker rmi josh-voice-bot:latest
```

### Debug

```bash
# Enter container shell
docker exec -it josh-voice-bot bash

# Check container status
docker ps

# View container details
docker inspect josh-voice-bot

# Check health
docker inspect --format='{{.State.Health.Status}}' josh-voice-bot
```

---

## 🌐 Production Deployment

### With Localtunnel

```bash
# Terminal 1: Start Docker container
docker-compose up -d

# Terminal 2: Create tunnel
docker run -d \
  --name localtunnel \
  --network host \
  efrecon/localtunnel \
  --port 8000
```

### With Ngrok

```bash
# Terminal 1: Start Docker container
docker-compose up -d

# Terminal 2: Create ngrok tunnel
ngrok http 8000
```

---

## 📊 Environment Variables

Required in `.env` file:

```env
# WhatsApp
WHATSAPP_PHONE_NUMBER_ID=your_phone_id
WHATSAPP_ACCESS_TOKEN=your_access_token
WHATSAPP_BUSINESS_ACCOUNT_ID=your_account_id
WEBHOOK_VERIFY_TOKEN=your_verify_token

# OpenAI
OPENAI_API_KEY=your_openai_key
OPENAI_MODEL=gpt-4o-mini

# ElevenLabs
ELEVENLABS_API_KEY=your_elevenlabs_key
ELEVENLABS_VOICE_ID=your_voice_id

# Server
HOST=0.0.0.0
PORT=8000
DEBUG=False
```

---

## 🗂️ Volume Mounts

```bash
# Invoice data (persistent storage)
-v $(pwd)/invoice_data:/app/invoice_data

# Logs (optional)
-v $(pwd)/logs:/app/logs
```

---

## 🔍 Health Check

The container has a built-in health check:

```bash
# Check health status
curl http://localhost:8000/health

# Docker health status
docker inspect --format='{{.State.Health.Status}}' josh-voice-bot
```

---

## 🚀 Push to Docker Hub (Optional)

```bash
# Tag image
docker tag josh-voice-bot:latest your-username/josh-voice-bot:latest

# Login
docker login

# Push
docker push your-username/josh-voice-bot:latest
```

---

## 🐛 Troubleshooting

### Container won't start
```bash
# Check logs
docker logs josh-voice-bot

# Check if port is in use
sudo lsof -i :8000

# Remove existing container
docker rm -f josh-voice-bot
```

### FFmpeg not found
```bash
# Rebuild image with --no-cache
docker build --no-cache -t josh-voice-bot:latest .
```

### Permission issues
```bash
# Fix invoice_data permissions
chmod -R 777 invoice_data/
```

---

## 📝 Notes

1. **FFmpeg**: Installed in container for audio conversion
2. **Port**: Default 8000 (change in docker-compose.yml if needed)
3. **Data**: Invoice data persists in `invoice_data/` directory
4. **Logs**: View with `docker logs -f josh-voice-bot`
5. **Updates**: Rebuild image after code changes

---

## 🌟 Production Best Practices

1. Use `.env` file for secrets (never commit!)
2. Mount volumes for persistent data
3. Use `--restart unless-stopped` for auto-restart
4. Set `DEBUG=False` in production
5. Monitor logs regularly
6. Use health checks
7. Consider Redis for conversation history at scale
