#!/usr/bin/env python3

"""
Voice Agent Integration Test Script
Tests the voice agent integration with the Shopify chat API
"""

import asyncio
import aiohttp
import json
import os
from dotenv import load_dotenv

load_dotenv()

class VoiceIntegrationTester:
    def __init__(self):
        # Try the actual ports that Shopify dev server uses
        self.chat_api_url = "http://localhost:11470/chat"
        self.token_api_url = "http://localhost:11470/api/voice/token"
        self.shop_domain = "http://localhost:11470"
        
    async def test_chat_api_connection(self):
        """Test connection to existing chat API"""
        print("🧪 Testing Chat API Connection...")
        
        try:
            headers = {
                "Content-Type": "application/json",
                "Origin": self.shop_domain,
                "Accept": "text/event-stream",
                "X-Shopify-Shop-Id": "test-shop"
            }
            
            payload = {
                "message": "Hi, this is a test message from the voice agent",
                "conversation_id": "test-conversation-123",
                "prompt_type": "shopify_voice_assistant"
            }
            
            async with aiohttp.ClientSession() as session:
                async with session.post(self.chat_api_url, 
                                      headers=headers, 
                                      json=payload,
                                      ssl=False) as response:
                    if response.status == 200:
                        print("✅ Chat API connection successful")
                        
                        # Read a few chunks of the SSE stream
                        chunks_read = 0
                        async for line in response.content:
                            if chunks_read >= 5:  # Read first 5 chunks
                                break
                            line = line.decode('utf-8').strip()
                            if line.startswith('data: '):
                                try:
                                    data = json.loads(line[6:])
                                    print(f"📦 Received: {data.get('type', 'unknown')} - {data.get('chunk', '')[:50]}...")
                                    chunks_read += 1
                                except json.JSONDecodeError:
                                    continue
                        
                        return True
                    else:
                        print(f"❌ Chat API failed: {response.status}")
                        return False
                        
        except Exception as e:
            print(f"❌ Chat API error: {e}")
            return False
    
    async def test_token_generation(self):
        """Test LiveKit token generation"""
        print("\n🧪 Testing LiveKit Token Generation...")
        
        try:
            headers = {
                "Content-Type": "application/json",
                "X-Shopify-Shop-Id": "test-shop"
            }
            
            payload = {
                "conversation_id": "test-conversation-123",
                "shop_domain": self.shop_domain
            }
            
            async with aiohttp.ClientSession() as session:
                async with session.post(self.token_api_url,
                                      headers=headers,
                                      json=payload,
                                      ssl=False) as response:
                    if response.status == 200:
                        data = await response.json()
                        print("✅ Token generation successful")
                        print(f"📝 Room: {data.get('room_name', 'N/A')}")
                        print(f"🔗 URL: {data.get('url', 'N/A')}")
                        print(f"🎫 Token: {data.get('token', 'N/A')[:20]}...")
                        return True
                    else:
                        error_data = await response.json()
                        print(f"❌ Token generation failed: {response.status}")
                        print(f"   Error: {error_data.get('error', 'Unknown error')}")
                        return False
                        
        except Exception as e:
            print(f"❌ Token generation error: {e}")
            return False
    
    async def test_environment_variables(self):
        """Test required environment variables"""
        print("\n🧪 Testing Environment Variables...")
        
        required_vars = [
            "LIVEKIT_API_KEY",
            "LIVEKIT_API_SECRET", 
            "LIVEKIT_URL",
            "DEEPGRAM_API_KEY",
            "OPENAI_API_KEY",
            "CARTESIA_API_KEY"
        ]
        
        missing_vars = []
        for var in required_vars:
            if not os.getenv(var):
                missing_vars.append(var)
            else:
                print(f"✅ {var}: Set")
        
        if missing_vars:
            print(f"❌ Missing environment variables: {', '.join(missing_vars)}")
            return False
        else:
            print("✅ All environment variables are set")
            return True
    
    async def test_voice_agent_imports(self):
        """Test that voice agent dependencies are installed"""
        print("\n🧪 Testing Voice Agent Dependencies...")
        
        try:
            import livekit
            print("✅ LiveKit SDK imported successfully")
            
            from livekit.plugins import deepgram, cartesia, openai, silero
            print("✅ Voice AI plugins imported successfully")
            
            from livekit.agents import Agent, AgentSession
            print("✅ Agent framework imported successfully")
            
            return True
            
        except ImportError as e:
            print(f"❌ Import error: {e}")
            print("   Try: pip install -r requirements.txt")
            return False
    
    async def run_all_tests(self):
        """Run all integration tests"""
        print("🚀 Starting Voice Agent Integration Tests...\n")
        
        tests = [
            ("Environment Variables", self.test_environment_variables()),
            ("Voice Agent Dependencies", self.test_voice_agent_imports()),
            ("Token Generation API", self.test_token_generation()),
            ("Chat API Connection", self.test_chat_api_connection()),
        ]
        
        results = []
        for test_name, test_coro in tests:
            print(f"\n{'='*50}")
            print(f"Running: {test_name}")
            print('='*50)
            
            try:
                result = await test_coro
                results.append((test_name, result))
            except Exception as e:
                print(f"❌ {test_name} failed with exception: {e}")
                results.append((test_name, False))
        
        # Print summary
        print(f"\n{'='*50}")
        print("TEST SUMMARY")
        print('='*50)
        
        passed = 0
        for test_name, result in results:
            status = "✅ PASS" if result else "❌ FAIL"
            print(f"{status} {test_name}")
            if result:
                passed += 1
        
        print(f"\nResults: {passed}/{len(results)} tests passed")
        
        if passed == len(results):
            print("\n🎉 All tests passed! Your voice integration is ready to use.")
            print("\nNext steps:")
            print("1. Start your Remix app: npm run dev")
            print("2. Start voice agent: python agent.py dev") 
            print("3. Open your Shopify store and test the voice chat!")
        else:
            print(f"\n⚠️  {len(results) - passed} tests failed. Please fix the issues above.")

async def main():
    tester = VoiceIntegrationTester()
    await tester.run_all_tests()

if __name__ == "__main__":
    asyncio.run(main())