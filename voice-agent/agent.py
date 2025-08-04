#!/usr/bin/env python3

"""
Voice Agent for Shopify Chat
Voice agent with MCP store integration and extensive logging
"""

import os
import json
import asyncio
import aiohttp
from dotenv import load_dotenv
from livekit import agents
from livekit.agents import Agent, AgentSession, llm
from livekit.plugins import deepgram, cartesia, openai, silero
from livekit.plugins.turn_detector.multilingual import MultilingualModel

load_dotenv()

class ShopifyVoiceAgent(Agent):
    """Voice agent that connects to Shopify MCP store"""

    def __init__(self, shop_domain: str = None, conversation_id: str = None, shop_id: str = None):
        
        # NO hardcoded URLs - always wait for metadata
        self.shop_domain = shop_domain  # Will be None initially, updated via metadata
        self.conversation_id = conversation_id
        self.shop_id = shop_id
        self.chat_api_url = None  # Will be set when shop_domain is available
        
        # Update chat API URL if shop domain is provided
        if self.shop_domain:
            self.chat_api_url = f"{self.shop_domain}/chat"
        
        super().__init__(
            instructions="""You are a helpful AI shopping assistant for a Shopify store. You have access to real store data through tools:

- Use search_store_products when customers ask about products, prices, or want to browse
- Use add_to_cart when customers want to purchase items  
- Use get_store_policies for questions about shipping, returns, etc.

IMPORTANT: Always use the tools to get real store data. Never make up product information or prices.

Keep responses concise for voice interactions. You are a female voice with a friendly Australian accent."""
        )
        
        print(f"🤖 Voice agent initialized with:")
        print(f"   Shop domain: {self.shop_domain}")
        print(f"   Conversation ID: {self.conversation_id}")
        print(f"   Shop ID: {self.shop_id}")
    
    async def fetch_dynamic_config(self):
        """Read the current applicationUrl directly from shopify.app.toml"""
        try:
            print(f"🔧 Reading dynamic config from shopify.app.toml...")
            
            # Read the TOML file directly (go up one directory from voice-agent/)
            toml_path = "../shopify.app.toml"
            print(f"🔧 Reading from: {toml_path}")
            
            with open(toml_path, 'r') as f:
                content = f.read()
            
            # Extract application_url using regex (same as /api/config endpoint)
            import re
            url_match = re.search(r'application_url\s*=\s*"([^"]+)"', content)
            
            if url_match:
                application_url = url_match.group(1)
                print(f"✅ Found dynamic URL: {application_url}")
                
                # Update agent configuration
                self.shop_domain = application_url  
                self.chat_api_url = f"{self.shop_domain}/chat"
                
                print(f"🔄 Agent updated with dynamic config:")
                print(f"   Shop domain: {self.shop_domain}")
                print(f"   Chat API URL: {self.chat_api_url}")
                return True
            else:
                print(f"⚠️ Could not find application_url in shopify.app.toml")
                
        except Exception as e:
            print(f"⚠️ Failed to read dynamic config: {e}")
        
        return False
    
    @llm.function_tool
    async def search_store_products(self, query: str) -> str:
        """Search for products in the store and handle shopping requests.
        
        Args:
            query: What the customer is looking for (e.g., 'snowboards', 'ski wax', 'winter jackets')
        
        Returns:
            str: Product search results from the store
        """
        print(f"🛍️ TOOL CALLED: search_store_products with query: '{query}'")
        result = await self.call_chat_api(f"Search for products: {query}")
        print(f"🛍️ TOOL RESULT: {result[:200]}..." if len(result) > 200 else f"🛍️ TOOL RESULT: {result}")
        return result
    
    @llm.function_tool
    async def add_to_cart(self, product_info: str) -> str:
        """Add items to the customer's cart.
        
        Args:
            product_info: Information about the product to add (name, variant, etc.)
        
        Returns:
            str: Result of adding item to cart
        """
        print(f"🛒 TOOL CALLED: add_to_cart with product_info: '{product_info}'")
        result = await self.call_chat_api(f"Add to cart: {product_info}")
        print(f"🛒 TOOL RESULT: {result[:200]}..." if len(result) > 200 else f"🛒 TOOL RESULT: {result}")
        return result
    
    @llm.function_tool
    async def get_store_policies(self, question: str) -> str:
        """Get store policies and FAQ information.
        
        Args:
            question: Customer's question about store policies
        
        Returns:
            str: Store policy information
        """
        print(f"ℹ️ TOOL CALLED: get_store_policies with question: '{question}'")
        result = await self.call_chat_api(f"Store policy question: {question}")
        print(f"ℹ️ TOOL RESULT: {result[:200]}..." if len(result) > 200 else f"ℹ️ TOOL RESULT: {result}")
        return result
    
    async def call_chat_api(self, message: str) -> str:
        """Call the MCP-enabled chat API"""
        print(f"📞 CALLING CHAT API with message: '{message}'")
        
        # Check if we have the necessary configuration
        if not self.shop_domain or not self.chat_api_url:
            error_msg = f"Shop domain not yet configured. Domain: {self.shop_domain}, URL: {self.chat_api_url}"
            print(f"❌ {error_msg}")
            return "I'm still connecting to the store. Please try again in a moment."
        
        try:
            payload = {
                "message": message,
                "conversation_id": self.conversation_id or "voice-session",
                "prompt_type": "shopify_voice_assistant"
            }
            
            headers = {
                "Content-Type": "application/json",
                "Accept": "text/event-stream",
                "Origin": self.shop_domain,
            }
            
            if self.shop_id:
                headers["X-Shopify-Shop-Id"] = str(self.shop_id)
                print(f"📞 Added shop ID header: {self.shop_id}")
            
            print(f"📞 API URL: {self.chat_api_url}")
            print(f"📞 Payload: {json.dumps(payload, indent=2)}")
            
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    self.chat_api_url,
                    json=payload,
                    headers=headers,
                    timeout=aiohttp.ClientTimeout(total=30)
                ) as response:
                    print(f"📞 API Response Status: {response.status}")
                    
                    if response.status == 200:
                        result = await self._handle_streaming_response(response)
                        print(f"📞 Final API result: {result[:200]}..." if len(result) > 200 else f"📞 Final API result: {result}")
                        return result
                    else:
                        error_text = await response.text()
                        print(f"❌ API Error {response.status}: {error_text}")
                        return f"I'm having trouble accessing the store information right now. Error: {response.status}"
                        
        except Exception as e:
            print(f"❌ Exception calling chat API: {e}")
            return f"I'm experiencing technical difficulties. Please try again. Error: {str(e)}"
    
    async def _handle_streaming_response(self, response) -> str:
        """Handle SSE streaming response from chat API"""
        print(f"📡 Processing streaming response...")
        
        try:
            complete_response = ""
            async for line in response.content:
                line_str = line.decode('utf-8').strip()
                
                if line_str.startswith('data: '):
                    try:
                        data = json.loads(line_str[6:])
                        msg_type = data.get('type')
                        
                        print(f"📡 Stream event: {msg_type}")
                        
                        if msg_type == 'chunk':
                            chunk = data.get('chunk', '')
                            complete_response += chunk
                            print(f"📡 Chunk: '{chunk}'")
                        elif msg_type == 'tool_use':
                            print(f"📡 Tool use detected: {data.get('tool_use_message', 'Unknown tool')}")
                        elif msg_type == 'end_turn':
                            print(f"📡 End of response")
                            break
                        elif msg_type == 'error':
                            error_msg = data.get('error', 'Unknown error')
                            print(f"❌ Stream error: {error_msg}")
                            return f"Error: {error_msg}"
                            
                    except json.JSONDecodeError as e:
                        print(f"⚠️ Could not parse stream line: {line_str[:100]}")
                        continue
                        
            final_result = complete_response.strip() if complete_response else "I'm here to help with your shopping!"
            print(f"📡 Complete response: {final_result}")
            return final_result
            
        except Exception as e:
            print(f"❌ Error handling streaming response: {e}")
            return f"Error processing response: {str(e)}"

async def entrypoint(ctx: agents.JobContext):
    """Main entry point for the voice agent"""
    
    print(f"🚀 Voice agent starting for room: {ctx.room.name}")
    
    # Extract conversation ID from room name
    conversation_id = None
    if ctx.room.name and ctx.room.name.startswith('shopify-voice-'):
        conversation_id = ctx.room.name.replace('shopify-voice-', '')
        print(f"🔍 Extracted conversation ID: {conversation_id}")
    
    # Wait for participant metadata
    print(f"⏳ Waiting for participant metadata...")
    metadata = {}
    shop_domain = None  # Will be set from metadata - NO hardcoded URLs
    shop_id = None
    
    # No default values - agent will wait for metadata
    print(f"🔍 No default shop configuration - will wait for metadata")
    print(f"   Note: Agent will be configured when participant metadata arrives")
    
    print(f"🤖 Creating voice agent with:")
    print(f"   Shop domain: {shop_domain}")
    print(f"   Conversation ID: {conversation_id}")
    print(f"   Shop ID: {shop_id}")
    
    # Create voice agent with store integration
    agent = ShopifyVoiceAgent(
        shop_domain=shop_domain,
        conversation_id=conversation_id,
        shop_id=shop_id
    )
    
    # Try to fetch dynamic configuration immediately
    print(f"🔧 Attempting to fetch dynamic config...")
    config_success = await agent.fetch_dynamic_config()
    if config_success:
        print(f"✅ Dynamic config loaded successfully!")
        # Also set a fallback shop_id since metadata isn't working
        if not agent.shop_id:
            agent.shop_id = 68616388662  # Fallback to known shop_id
            print(f"🔧 Set fallback shop_id: {agent.shop_id}")
    else:
        print(f"⚠️ Dynamic config failed, will wait for metadata...")
    
    # Configure voice pipeline
    session = AgentSession(
        stt=deepgram.STT(
            model="nova-3", 
            language="multi"
        ),
        llm=openai.LLM(
            model="gpt-4o-mini",
            temperature=0.7
        ),
        tts=cartesia.TTS(
            model="sonic-2",
            voice="57c63422-d911-4666-815b-0c332e4d7d6a"
        ),
        vad=silero.VAD.load(),
        turn_detection=MultilingualModel(),
    )
    
    print(f"🎙️ Starting voice session...")
    
    # Function to process metadata from any participant
    def process_participant_metadata(participant):
        print(f"🔄 Processing metadata for {participant.identity}")
        print(f"🔄 Raw metadata: {participant.metadata}")
        if participant.metadata:
            try:
                metadata = json.loads(participant.metadata) if isinstance(participant.metadata, str) else participant.metadata
                print(f"✅ Parsed metadata: {metadata}")
                
                # Update agent configuration
                if metadata.get('shop_domain'):
                    agent.shop_domain = metadata['shop_domain']
                    agent.chat_api_url = f"{agent.shop_domain}/chat"
                    print(f"🔄 Updated shop_domain: {agent.shop_domain}")
                if metadata.get('shop_id'):
                    agent.shop_id = metadata['shop_id']
                    print(f"🔄 Updated shop_id: {agent.shop_id}")
                if metadata.get('conversation_id'):
                    agent.conversation_id = metadata['conversation_id']
                    print(f"🔄 Updated conversation_id: {agent.conversation_id}")
                    
                print(f"🔄 Agent final config:")
                print(f"   Shop domain: {agent.shop_domain}")
                print(f"   Shop ID: {agent.shop_id}")
                print(f"   Conversation ID: {agent.conversation_id}")
                print(f"   Chat API URL: {agent.chat_api_url}")
                    
            except Exception as e:
                print(f"⚠️ Could not parse metadata: {e}")
        else:
            print(f"⚠️ No metadata found for participant {participant.identity}")
    
    # Create metadata handler to update agent when participants join
    @ctx.room.on("participant_metadata_changed")
    def on_metadata_changed(participant, prev_metadata):
        print(f"🔄 Participant metadata changed for {participant.identity}")
        process_participant_metadata(participant)
    
    @ctx.room.on("participant_connected")
    def on_participant_connected(participant):
        print(f"👤 Participant connected: {participant.identity}")
        print(f"👤 Participant type: {type(participant)}")
        print(f"👤 Initial metadata: {participant.metadata}")
        if participant.metadata:
            print(f"👤 Processing initial metadata...")
            process_participant_metadata(participant)
        else:
            print(f"👤 No initial metadata, waiting for metadata update...")
    
    # Add more debugging for room events
    @ctx.room.on("participant_disconnected")  
    def on_participant_disconnected(participant):
        print(f"👋 Participant disconnected: {participant.identity}")
    
    # Also check existing participants after connection
    @ctx.room.on("connected")
    def on_room_connected():
        print(f"🏠 Room connected! Checking existing participants...")
        print(f"🏠 Local participant: {ctx.room.local_participant.identity}")
        print(f"🏠 Local metadata: {ctx.room.local_participant.metadata}")
        
        for participant in ctx.room.remote_participants.values():
            print(f"🏠 Remote participant: {participant.identity}")
            print(f"🏠 Remote metadata: {participant.metadata}")
            if participant.metadata:
                process_participant_metadata(participant)
    
    print(f"🎧 Event handlers registered, waiting for participants...")
    
    # Start the session with the voice assistant
    await session.start(
        room=ctx.room,
        agent=agent
    )

if __name__ == "__main__":
    agents.cli.run_app(
        agents.WorkerOptions(
            entrypoint_fnc=entrypoint,
        )
    )