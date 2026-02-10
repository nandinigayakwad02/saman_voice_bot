# WhatsApp AI Chatbot - Super Simple

## What You Have

Just 4 files for WhatsApp AI chatbot:

1. **app/main.py** - Receives WhatsApp messages, gets AI response, sends back
2. **app/whatsapp.py** - WhatsApp API client  
3. **app/ai_agent.py** - OpenAI integration
4. **app/config.py** - Settings

## Setup

1. **Add OpenAI key to `.env`:**
   ```
   OPENAI_API_KEY=sk-your-key-here
   ```

2. **Run:**
   ```bash
   cd "/home/pc/Documents/Nitu's folder/paymentReminder"
   source venv/bin/activate
   python run.py
   ```

3. **Setup webhook** (so you can receive messages):
   ```bash
   # In another terminal
   ngrok http 8000
   ```
   
   Then add the ngrok URL to Meta dashboard.

## How It Works

- You send WhatsApp from **+91 8226053534**
- Bot gets AI response from OpenAI
- Sends response to **+1 555 157 1989**

That's it! 🎉

## Cost

~$0.001 per message (very cheap with gpt-4o-mini)
