#!/usr/bin/env python3

"""
Voice Agent for Shopify Chat
Bridges LiveKit voice capabilities with existing Remix chat API
"""

import os
import json
import asyncio
import aiohttp
from dotenv import load_dotenv
from livekit import agents
from livekit.agents import Agent, AgentSession, RoomInputOptions
from livekit.plugins import deepgram, cartesia, openai, silero
from livekit.plugins.turn_detector.multilingual import MultilingualModel

load_dotenv()

class ShopifyVoiceAgent(Agent):
    """Voice agent that connects to Shopify chat API"""

    def __init__(self, shop_domain: str, conversation_id: str = None):
        super().__init__(
            instructions="You are a helpful AI shopping assistant. Keep responses concise for voice interactions."
        )
        self.shop_domain = shop_domain
        self.conversation_id = conversation_id
        self.chat_api_url = f"{shop_domain}/chat"

    async def call_chat_api(self, message: str) -> str:
        """Call the existing Remix chat API with the user's message"""
        try:
            # Prepare the request payload
            payload = {
                "message": message,
                "conversationId": self.conversation_id,
                "streamResponse": False  # Get complete response for voice
            }
            
            headers = {
                "Content-Type": "application/json",
                "Accept": "application/json"
            }
            
            print(f"Calling chat API: {self.chat_api_url}")
            print(f"Payload: {json.dumps(payload, indent=2)}")
            
            # Make the API call
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    self.chat_api_url,
                    json=payload,
                    headers=headers,
                    timeout=aiohttp.ClientTimeout(total=30)
                ) as response:
                    if response.status == 200:
                        response_text = await response.text()
                        print(f"API Response: {response_text}")
                        return response_text
                    else:
                        error_text = await response.text()
                        print(f"API Error {response.status}: {error_text}")
                        return "I apologize, but I'm having trouble processing your request right now. Please try again."
                        
        except Exception as e:
            print(f"Error calling chat API: {e}")
            return "I apologize, but I encountered an error. Please try again."

async def entrypoint(ctx: agents.JobContext):
    """Main entry point for the voice agent"""
    
    # Extract shop domain from room metadata
    metadata = {}
    if ctx.room.metadata:
        try:
            # Parse metadata if it's a JSON string
            if isinstance(ctx.room.metadata, str):
                metadata = json.loads(ctx.room.metadata)
            else:
                metadata = ctx.room.metadata
        except (json.JSONDecodeError, AttributeError):
            print(f"Warning: Could not parse room metadata: {ctx.room.metadata}")
            metadata = {}
    
    shop_domain = metadata.get('shop_domain', 'https://jeans-singer-grab-effort.trycloudflare.com')
    conversation_id = metadata.get('conversation_id')
    
    # Create agent instance
    agent = ShopifyVoiceAgent(shop_domain, conversation_id)
    
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
            voice="c2da2a3e-b0d6-46bf-a09a-68562617a50a"
        ),
        vad=silero.VAD.load(),
        turn_detection=MultilingualModel(),
    )
    
    # Start the session with the voice assistant
    await session.start(
        room=ctx.room,
        agent=agent
    )
    
    # Send initial greeting
    await session.generate_reply(
        instructions="Greet the customer warmly and offer assistance with shopping. Keep it brief for voice interaction."
    )

if __name__ == "__main__":
    agents.cli.run_app(
        agents.WorkerOptions(
            entrypoint_fnc=entrypoint,
        )
    )