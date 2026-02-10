#!/bin/bash

echo "🚀 Setting up WhatsApp AI Chatbot..."

# Create .env file
cat > .env << 'EOF'
# WhatsApp Business API Configuration
WHATSAPP_API_VERSION=v21.0
WHATSAPP_PHONE_NUMBER_ID=978451788677287
WHATSAPP_BUSINESS_ACCOUNT_ID=1194861479380410
WHATSAPP_ACCESS_TOKEN=EAAUQ9pZCC9N8BQcePGV3byiduOsGlIdj12a8UGPuUunuAo6qXZAszzJJFY0ZBWfrh28n5s7VXW29btyVIg5l6hXx5CfDkQ3hwm95ce4uleZBIID5qKUusYSQUdKvLySKGHerXrFmGajNxaM5qhvFSBA9WCqaY8RskQkBgyAcsAZCtj2OZA58wn0tAF5248Fg6yxgZDZD

# App Configuration
APP_ID=1426026311906527
APP_SECRET=1219d8d40274ca200421c3806e8970b2

# Webhook Configuration
WEBHOOK_VERIFY_TOKEN=whatsapp_ai_chatbot_2026

# OpenAI Configuration
OPENAI_API_KEY=your_openai_api_key_here
OPENAI_MODEL=gpt-4o-mini

# Server Configuration
HOST=0.0.0.0
PORT=8000
DEBUG=True

# Phone Numbers (no + sign)
USER_PHONE=918226053534
TEST_PHONE=15551571989
EOF

echo "✅ Created .env file"
echo "⚠️  IMPORTANT: Add your OpenAI API key to .env file!"

# Activate virtual environment and install dependencies
if [ ! -d "venv" ]; then
    echo "📦 Creating virtual environment..."
    python3 -m venv venv
fi

echo "📦 Installing dependencies..."
source venv/bin/activate
pip install -r requirements.txt

echo ""
echo "✅ Setup complete!"
echo ""
echo "⚠️  Before running:"
echo "1. Add your OpenAI API key to .env file (OPENAI_API_KEY=sk-...)"
echo ""
echo "Then run:"
echo "1. Activate virtual environment: source venv/bin/activate"
echo "2. Run the application: python run.py"
echo "3. For webhook testing: ngrok http 8000"
echo ""
