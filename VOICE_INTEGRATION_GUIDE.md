# 🎤 Voice Agent Integration Guide

## 🎯 Overview

Your Shopify app now has full voice capabilities! Customers can:

- **Talk to your AI assistant** using their microphone
- **Get voice responses** with natural conversation flow
- **Use all existing features** (product search, cart management, checkout) via voice
- **Switch between text and voice** seamlessly in the same conversation

## ⚡ Architecture

```
Customer Voice Input → LiveKit → Python Agent → Your Existing Chat API → Claude + MCP Tools → Voice Response
```

**Key Benefits:**

- ✅ **Reuses your existing backend** - no duplication
- ✅ **Preserves all MCP tools** - voice users get same shopping features
- ✅ **Conversation continuity** - voice and text in same thread
- ✅ **Mobile optimized** - works on all devices

## 🚀 Quick Start

### 1. LiveKit Cloud Setup

1. **Sign up at [livekit.io/cloud](https://livekit.io/cloud)**
2. **Create a new project**
3. **Copy your credentials** from the settings page

### 2. Environment Configuration

Add these to your `.env` file:

```env
# LiveKit Configuration
LIVEKIT_API_KEY=your_api_key_here
LIVEKIT_API_SECRET=your_api_secret_here
LIVEKIT_URL=wss://your-project.livekit.cloud

# Voice AI Providers (you mentioned you have these)
DEEPGRAM_API_KEY=your_deepgram_key
OPENAI_API_KEY=your_openai_key
CARTESIA_API_KEY=your_cartesia_key
```

### 3. Theme Extension Configuration

In your Shopify admin:

1. **Go to Online Store > Themes**
2. **Click "Customize" on your theme**
3. **Find the "AI Chat Assistant" block**
4. **Enable voice chat**: ✅ Check "Enable Voice Chat"
5. **Set LiveKit URL**: Enter your `wss://your-project.livekit.cloud` URL
6. **Choose voice prompt**: Select "Voice Assistant (Optimized for speech)"

### 4. Start Your Services

#### Terminal 1: Start Remix App

```bash
cd /Users/osmancakir/shop-chat-agent
npm run dev
```

#### Terminal 2: Start Voice Agent

```bash
cd /Users/osmancakir/shop-chat-agent/voice-agent
source venv/bin/activate
python agent.py dev
```

## 🧪 Testing Your Voice Agent

### 1. **Basic Voice Test**

- Open your Shopify store
- Click the chat bubble
- Click the green **🎤 microphone button**
- Say: _"Hi, can you help me find some products?"_
- Wait for voice response

### 2. **Product Search Test**

- Say: _"I'm looking for snowboards"_
- Should see products displayed AND hear response
- Try: _"Show me the details for the first one"_

### 3. **Cart Management Test**

- Say: _"Add the Videographer Snowboard to my cart"_
- Should get cart confirmation via voice
- Try: _"What's in my cart?"_

### 4. **Mixed Mode Test**

- Start with voice: _"Hi there!"_
- Switch to typing: "Can you search for boots?"
- Back to voice: _"Add the first boot to my cart"_
- Conversation should flow seamlessly

## 📱 Mobile Testing

Test on mobile devices:

- **iPhone Safari**: Voice should work with good quality
- **Android Chrome**: Test microphone permissions
- **Different network conditions**: Voice should be stable

## 🔧 Troubleshooting

### **Voice Button Not Appearing**

- ✅ Check `LIVEKIT_URL` is set in theme settings
- ✅ Verify "Enable Voice Chat" is checked
- ✅ Clear browser cache

### **"Voice chat not configured" Error**

- ✅ Check `.env` file has all LiveKit variables
- ✅ Restart your Remix server after adding env vars
- ✅ Verify LiveKit credentials are correct

### **Voice Agent Not Connecting**

```bash
# Check if voice agent is running
cd voice-agent
source venv/bin/activate
python agent.py dev
```

### **No Audio Output**

- ✅ Check browser audio permissions
- ✅ Test with headphones to avoid feedback
- ✅ Verify speaker volume

### **Token Generation Errors**

- ✅ Check LiveKit API credentials
- ✅ Verify network connectivity to LiveKit cloud
- ✅ Check browser console for CORS errors

## 🎛️ Configuration Options

### Voice Settings in Theme

- **Enable Voice Chat**: Turn voice on/off
- **LiveKit URL**: Your WebSocket connection
- **System Prompt**: Choose voice-optimized prompts

### Voice Agent Settings

Edit `voice-agent/agent.py`:

- **STT Model**: Change Deepgram model for different languages
- **Voice Selection**: Change Cartesia voice ID
- **Turn Detection**: Adjust sensitivity

### Backend Integration

The voice agent calls your existing chat API at:

- **Text Chat**: `https://localhost:3458/chat` (existing)
- **Voice Tokens**: `https://localhost:3458/api/voice/token` (new)

## 🎨 Customization

### Voice Button Styling

Edit `extensions/chat-bubble/assets/chat.css`:

```css
.shop-ai-chat-voice {
  background-color: #your-brand-color;
}
```

### Voice Prompts

Edit `app/prompts/prompts.json` to customize voice responses:

```json
{
  "shopify_voice_assistant": {
    "content": "Your custom voice prompt here..."
  }
}
```

### Voice Agent Behavior

Edit `voice-agent/agent.py`:

- Change STT/TTS providers
- Add custom tool handling
- Modify conversation flow

## 🚀 Production Deployment

### 1. **Deploy Voice Agent**

- Use Docker with your Python agent
- Deploy to same infrastructure as your Remix app
- Configure environment variables

### 2. **LiveKit Production**

- Upgrade to LiveKit Cloud Pro for production traffic
- Configure custom domain if needed
- Set up monitoring and alerts

### 3. **Update URLs**

- Change `localhost:3458` to your production domain
- Update LiveKit URL in theme settings
- Test with real Shopify store

## 📊 Monitoring

### Voice Agent Logs

```bash
# View agent logs
cd voice-agent
source venv/bin/activate
python agent.py start --log-level debug
```

### LiveKit Dashboard

- Monitor room connections
- Track audio quality metrics
- View usage analytics

## 🆘 Support

### Development

- **Voice Agent Issues**: Check Python logs in terminal
- **Frontend Issues**: Check browser console
- **LiveKit Issues**: Check LiveKit dashboard

### LiveKit Community

- [LiveKit Discord](https://discord.gg/livekit)
- [Documentation](https://docs.livekit.io)
- [GitHub Issues](https://github.com/livekit/livekit)

## ✨ What's Next?

Your voice agent is production-ready! Consider these enhancements:

🔮 **Future Improvements:**

- **Multi-language support** with different STT models
- **Voice analytics** to track usage patterns
- **Custom wake words** for hands-free activation
- **Voice shortcuts** for common actions
- **Sentiment analysis** for better customer service

Congratulations! Your Shopify app now has cutting-edge voice AI capabilities! 🎉
