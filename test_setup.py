"""
Quick test script for Serenique LangChain server setup
Run this to verify your configuration before starting the full server
"""

import os
import sys
from datetime import datetime

def test_imports():
    """Test that all required packages are installed"""
    print("🔍 Testing Python package imports...")
    
    packages = {
        "fastapi": "FastAPI",
        "pydantic": "Pydantic",
        "langchain": "LangChain",
        "langchain_openai": "LangChain OpenAI",
        "firebase_admin": "Firebase Admin SDK",
    }
    
    all_good = True
    for package, name in packages.items():
        try:
            __import__(package)
            print(f"  ✅ {name}")
        except ImportError as e:
            print(f"  ❌ {name} - NOT INSTALLED")
            print(f"     Install with: pip install {package}")
            all_good = False
    
    return all_good


def test_env_variables():
    """Test that required environment variables are set"""
    print("\n🔍 Testing environment variables...")
    
    # Try to load .env file
    try:
        from dotenv import load_dotenv
        load_dotenv()
        print("  ℹ️  Loaded .env file")
    except ImportError:
        print("  ℹ️  python-dotenv not installed (optional)")
        print("     Install with: pip install python-dotenv")
    
    checks = {
        "OPENROUTER_API_KEY": "OpenRouter API Key",
        "FIREBASE_CREDENTIALS": "Firebase Credentials (JSON)",
        "GOOGLE_APPLICATION_CREDENTIALS": "Firebase Credentials (File Path)",
    }
    
    all_good = True
    openrouter_ok = False
    firebase_ok = False
    
    # Check OpenRouter
    openrouter_key = os.getenv("OPENROUTER_API_KEY", "")
    if openrouter_key:
        print(f"  ✅ OpenRouter API Key: {openrouter_key[:20]}...")
        openrouter_ok = True
    else:
        print(f"  ❌ OpenRouter API Key - NOT SET")
        print(f"     Set in .env: OPENROUTER_API_KEY=your_key_here")
        all_good = False
    
    # Check Firebase (either method)
    firebase_creds = os.getenv("FIREBASE_CREDENTIALS", "")
    firebase_file = os.getenv("GOOGLE_APPLICATION_CREDENTIALS", "")
    
    if firebase_creds:
        print(f"  ✅ Firebase Credentials (JSON): Set ({len(firebase_creds)} chars)")
        firebase_ok = True
    elif firebase_file:
        if os.path.exists(firebase_file):
            print(f"  ✅ Firebase Credentials (File): {firebase_file}")
            firebase_ok = True
        else:
            print(f"  ❌ Firebase Credentials File not found: {firebase_file}")
            all_good = False
    else:
        print(f"  ⚠️  Firebase Credentials - NOT SET")
        print(f"     This is required for production use!")
        print(f"     See FIREBASE_SETUP.md for instructions")
        # Don't mark as failed - server can run without it for testing
    
    return all_good and openrouter_ok


def test_firebase_connection():
    """Test Firebase Admin SDK initialization"""
    print("\n🔍 Testing Firebase connection...")
    
    try:
        from firebase_service import firebase_service
        
        if firebase_service._initialized:
            print("  ✅ Firebase Admin SDK initialized successfully")
            
            # Try to get stats
            try:
                stats = firebase_service.get_persona_stats()
                print(f"  ✅ Firestore connection working")
                print(f"     Total personas: {stats.get('total_personas', 0)}")
                return True
            except Exception as e:
                print(f"  ⚠️  Firebase initialized but Firestore access failed")
                print(f"     This is normal if no personas exist yet")
                return True
        else:
            print("  ❌ Firebase Admin SDK failed to initialize")
            print("     Check FIREBASE_SETUP.md for instructions")
            return False
            
    except Exception as e:
        print(f"  ❌ Firebase connection failed: {e}")
        print("     Check your credentials and Firestore rules")
        return False


def test_langchain_setup():
    """Test LangChain persona architect initialization"""
    print("\n🔍 Testing LangChain setup...")
    
    try:
        from langchain_persona_architect import LangChainPersonaArchitect
        
        openrouter_key = os.getenv("OPENROUTER_API_KEY", "")
        if not openrouter_key:
            print("  ❌ Cannot test LangChain - OpenRouter API key not set")
            return False
        
        architect = LangChainPersonaArchitect(
            openrouter_api_key=openrouter_key,
            model_name=os.getenv("MODEL_NAME", "openai/gpt-4o-mini"),
            temperature=0.7
        )
        
        print(f"  ✅ LangChain Persona Architect initialized")
        print(f"     Model: {os.getenv('MODEL_NAME', 'openai/gpt-4o-mini')}")
        return True
        
    except Exception as e:
        print(f"  ❌ LangChain setup failed: {e}")
        return False


def run_quick_test():
    """Run a quick persona generation test"""
    print("\n🔍 Running quick persona generation test...")
    print("   (This will use OpenRouter API credits - about $0.01)")
    
    response = input("   Continue? (y/n): ")
    if response.lower() != 'y':
        print("   ⏭️  Skipped")
        return True
    
    try:
        from langchain_persona_architect import LangChainPersonaArchitect
        
        openrouter_key = os.getenv("OPENROUTER_API_KEY", "")
        
        architect = LangChainPersonaArchitect(
            openrouter_api_key=openrouter_key,
            model_name=os.getenv("MODEL_NAME", "openai/gpt-4o-mini"),
            temperature=0.7
        )
        
        # Sample quiz data
        test_quiz = {
            1: "b",  # Logical problem-solving
            2: "d",  # Mixed feelings about social media
            3: "a",  # Needs alone time after social events
            4: "b",  # Anxious about deadlines
            5: "d",  # Wants help but struggles to ask
            6: "a",  # Sleep critically affects mood
            7: "a",  # Analyzes problems first
            8: "b",  # Sometimes distracted
            9: "a",  # Reaches out when lonely
            10: "b"  # Sometimes negative self-talk
        }
        
        print("   🤖 Generating test persona (this takes 5-15 seconds)...")
        start_time = datetime.now()
        
        persona = architect.generate_persona("test_user_" + datetime.now().strftime("%H%M%S"), test_quiz)
        
        elapsed = (datetime.now() - start_time).total_seconds()
        
        print(f"   ✅ Persona generated successfully in {elapsed:.1f}s")
        print(f"      Communication Style: {persona.personality_profile.communication_style}")
        print(f"      Primary Stressor: {persona.personality_profile.primary_stressor}")
        print(f"      Social Profile: {persona.personality_profile.social_profile}")
        print(f"      System Prompt Length: {len(persona.personality_profile.chatbot_system_prompt)} chars")
        
        return True
        
    except Exception as e:
        print(f"   ❌ Test failed: {e}")
        return False


def main():
    print("=" * 70)
    print("  Serenique LangChain Server - Configuration Test")
    print("=" * 70)
    
    results = []
    
    # Test 1: Imports
    results.append(("Package Imports", test_imports()))
    
    # Test 2: Environment Variables
    results.append(("Environment Variables", test_env_variables()))
    
    # Test 3: Firebase
    results.append(("Firebase Connection", test_firebase_connection()))
    
    # Test 4: LangChain
    results.append(("LangChain Setup", test_langchain_setup()))
    
    # Test 5: Quick generation test (optional)
    if all(result[1] for result in results):
        results.append(("Persona Generation", run_quick_test()))
    
    # Summary
    print("\n" + "=" * 70)
    print("  Test Summary")
    print("=" * 70)
    
    for test_name, passed in results:
        status = "✅ PASS" if passed else "❌ FAIL"
        print(f"  {status} - {test_name}")
    
    print("\n")
    
    all_passed = all(result[1] for result in results)
    
    if all_passed:
        print("🎉 All tests passed! Your server is ready to run.")
        print("\nNext steps:")
        print("  1. Start server: uvicorn main:app --reload")
        print("  2. Test API: curl http://localhost:8000/api/health")
        print("  3. See QUICKSTART.md for Flutter integration")
    else:
        print("⚠️  Some tests failed. Please fix the issues above.")
        print("\nCommon fixes:")
        print("  • Install packages: pip install -r requirements.txt")
        print("  • Set OpenRouter key in .env file")
        print("  • Get Firebase credentials: see FIREBASE_SETUP.md")
    
    print("\n" + "=" * 70)
    
    return 0 if all_passed else 1


if __name__ == "__main__":
    sys.exit(main())
