"""
Test script for Chat API endpoint

Run this after starting the server with run.bat
Ensure you have a user with generated persona first.
"""

import requests
import json

# Configuration
BASE_URL = "http://localhost:5001"
TEST_USER_ID = "OwJgNZVyzMgi9f9uSIpN6LXC57P2"  # Replace with your actual user ID

def test_chat_endpoint():
    """Test the /api/chat endpoint"""
    
    print("=" * 60)
    print("Testing Chat API Endpoint with Peaceful Tone")
    print("=" * 60)
    
    # Test data - designed to test peaceful tone
    test_messages = [
        "Hi, I just finished my quiz",
        "I've been feeling really stressed about my exams",
        "Everything feels overwhelming today",
        "I tried the breathing exercise and it helped a little",
    ]
    
    for i, message in enumerate(test_messages, 1):
        print(f"\n{'-' * 60}")
        print(f"Test {i}/4: '{message}'")
        print('-' * 60)
        
        try:
            # Make request
            response = requests.post(
                f"{BASE_URL}/api/chat",
                json={
                    "user_id": TEST_USER_ID,
                    "message": message,
                    "include_history": True
                },
                headers={"Content-Type": "application/json"}
            )
            
            # Check status
            print(f"Status Code: {response.status_code}")
            
            if response.status_code == 200:
                data = response.json()
                print(f"\n✅ Success!")
                print(f"AI Response: {data['response']}")
                print(f"Chat History Saved: {data['chat_history_saved']}")
            else:
                print(f"\n❌ Error!")
                print(f"Response: {response.text}")
        
        except Exception as e:
            print(f"\n❌ Exception: {e}")
    
    print(f"\n{'=' * 60}")
    print("Testing Complete!")
    print('=' * 60)

def test_health():
    """Test the /api/health endpoint"""
    
    print("\n" + "=" * 60)
    print("Testing Health Endpoint")
    print("=" * 60)
    
    try:
        response = requests.get(f"{BASE_URL}/api/health")
        print(f"Status Code: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"\n✅ Server Healthy!")
            print(f"Service: {data['service']}")
            print(f"Version: {data['version']}")
            print(f"Gemini Configured: {data['gemini_configured']}")
            print(f"Firebase Initialized: {data['firebase_initialized']}")
        else:
            print(f"\n❌ Server Unhealthy!")
            print(f"Response: {response.text}")
    
    except Exception as e:
        print(f"\n❌ Cannot reach server: {e}")
        print(f"\nMake sure the server is running:")
        print(f"  1. Open terminal in serenique_cloud_server/")
        print(f"  2. Run: run.bat")
        return False
    
    return True

def test_get_persona():
    """Test retrieving user persona"""
    
    print("\n" + "=" * 60)
    print("Testing Get Persona Endpoint")
    print("=" * 60)
    
    try:
        response = requests.get(f"{BASE_URL}/api/persona/{TEST_USER_ID}")
        print(f"Status Code: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"\n✅ Persona Found!")
            
            persona = data['user_persona']
            profile = persona['personality_profile']
            state = persona['live_user_state']
            
            print(f"\nPersonality Profile:")
            print(f"  - Communication Style: {profile['communication_style']}")
            print(f"  - Primary Stressor: {profile['primary_stressor']}")
            print(f"  - Social Profile: {profile['social_profile']}")
            print(f"  - Stress Level: {profile['stress_level']}")
            
            print(f"\nLive State:")
            print(f"  - Current Mood: {state['current_mood']}")
            print(f"  - Chat Message Count: {state['chat_message_count']}")
            print(f"  - Tool Usage Count: {state['tool_usage_count']}")
            print(f"  - Needs Check-in: {state['needs_check_in']}")
            print(f"  - Coping Successes: {state['coping_successes']}")
            
            return True
        
        elif response.status_code == 404:
            print(f"\n⚠️  No Persona Found!")
            print(f"\nYou need to generate a persona first:")
            print(f"  POST {BASE_URL}/api/persona/generate")
            print(f"  Body: {{")
            print(f'    "user_id": "{TEST_USER_ID}",')
            print(f'    "quiz_data": {{1: "a", 2: "b", ... 10: "j"}}')
            print(f"  }}")
            return False
        
        else:
            print(f"\n❌ Error!")
            print(f"Response: {response.text}")
            return False
    
    except Exception as e:
        print(f"\n❌ Exception: {e}")
        return False

if __name__ == "__main__":
    print("\n" + "🕊️ Serenique Chat API Test Suite (Peaceful Tone) 🕊️".center(70))
    
    # Test 1: Health check
    if not test_health():
        print("\n❌ Server is not running. Please start it with run.bat")
        exit(1)
    
    # Test 2: Check persona exists
    if not test_get_persona():
        print("\n❌ Persona not found. Generate it first before testing chat.")
        exit(1)
    
    # Test 3: Chat endpoint
    test_chat_endpoint()
    
    print("\n" + "✅ All Tests Complete!".center(70))
    print("\nNext Steps:")
    print("  1. Check Firebase Console for:")
    print("     - chat_history/{user_id}/messages - Full conversation history")
    print("  2. Notice the peaceful, calming tone in responses")
    print("  3. Send more messages to build conversation context")
    print("  4. Test with emotional messages to see validation-first approach")
    print("  5. Integrate into your Flutter app for mental wellness support")
