#!/bin/bash

# Voice Agent Startup Script
# Starts both the Remix app and the Voice Agent

echo "🚀 Starting Voice-Enabled Shopify App Services..."
echo ""

# Check if we're in the right directory
if [ ! -f "package.json" ]; then
    echo "❌ Error: Please run this script from the shop-chat-agent root directory"
    exit 1
fi

# Check if voice agent directory exists
if [ ! -d "voice-agent" ]; then
    echo "❌ Error: voice-agent directory not found"
    exit 1
fi

# Function to cleanup background processes
cleanup() {
    echo ""
    echo "🛑 Shutting down services..."
    jobs -p | xargs -r kill
    exit 0
}

# Set up signal handlers
trap cleanup SIGINT SIGTERM

# Start the Remix app in the background
echo "📱 Starting Remix App (Chat Backend)..."
npm run dev &
REMIX_PID=$!

# Wait a moment for the app to start
sleep 3

# Start the voice agent in the background  
echo "🎤 Starting Voice Agent..."
cd voice-agent
source venv/bin/activate
python agent.py dev &
VOICE_PID=$!
cd ..

echo ""
echo "✅ Services started successfully!"
echo ""
echo "🌐 Remix App: http://localhost:3458"
echo "🎙️  Voice Agent: Running in development mode"
echo ""
echo "🧪 To test the integration:"
echo "   1. Open your Shopify store"
echo "   2. Click the chat bubble"  
echo "   3. Click the green microphone button"
echo "   4. Say: 'Hi, can you help me find some products?'"
echo ""
echo "🔍 To run integration tests:"
echo "   cd voice-agent && python test_integration.py"
echo ""
echo "Press Ctrl+C to stop all services"
echo ""

# Wait for background processes
wait