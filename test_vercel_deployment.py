"""
Test Vercel Deployment Configuration

Run this locally to verify your setup is correct before deploying.
"""

import sys
import os

def test_imports():
    """Test that all required modules can be imported"""
    print("🔍 Testing imports...")
    try:
        from api.index import app
        print("✅ api.index.app imported successfully")
        
        from main import app as main_app
        print("✅ main.app imported successfully")
        
        from firebase_service import firebase_service
        print("✅ firebase_service imported successfully")
        
        from langchain_persona_architect import LangChainPersonaArchitect
        print("✅ LangChainPersonaArchitect imported successfully")
        
        from insight_extractor import InsightExtractor
        print("✅ InsightExtractor imported successfully")
        
        return True
    except ImportError as e:
        print(f"❌ Import failed: {e}")
        return False

def test_environment_variables():
    """Test that required environment variables are set"""
    print("\n🔍 Testing environment variables...")
    
    required_vars = {
        "GOOGLE_API_KEY": "Google Gemini API Key",
        "FIREBASE_CREDENTIALS": "Firebase Service Account JSON"
    }
    
    optional_vars = {
        "MODEL_NAME": "gemini-2.0-flash-exp",
        "MODEL_TEMPERATURE": "0.7"
    }
    
    all_set = True
    
    for var, description in required_vars.items():
        value = os.getenv(var)
        if value:
            # Show first 10 chars for security
            masked = value[:10] + "..." if len(value) > 10 else value
            print(f"✅ {var} is set: {masked}")
        else:
            print(f"❌ {var} is NOT set ({description})")
            all_set = False
    
    for var, default in optional_vars.items():
        value = os.getenv(var, default)
        print(f"ℹ️  {var} = {value} (default: {default})")
    
    return all_set

def test_app_creation():
    """Test that FastAPI app can be created"""
    print("\n🔍 Testing FastAPI app creation...")
    try:
        from api.index import app
        
        # Check app has routes
        routes = [route.path for route in app.routes]
        print(f"✅ FastAPI app created with {len(routes)} routes")
        
        # Check critical routes exist
        critical_routes = ["/api/health", "/api/chat", "/api/persona/generate"]
        for route in critical_routes:
            if route in routes:
                print(f"  ✅ {route}")
            else:
                print(f"  ❌ {route} not found")
        
        return True
    except Exception as e:
        print(f"❌ App creation failed: {e}")
        return False

def test_vercel_structure():
    """Test that Vercel deployment structure is correct"""
    print("\n🔍 Testing Vercel deployment structure...")
    
    required_files = {
        "api/index.py": "Vercel entry point",
        "main.py": "Main FastAPI app",
        "requirements.txt": "Python dependencies",
        "vercel.json": "Vercel configuration",
        ".vercelignore": "Files to exclude from deployment"
    }
    
    all_exist = True
    
    for file, description in required_files.items():
        if os.path.exists(file):
            print(f"✅ {file} exists ({description})")
        else:
            print(f"❌ {file} missing ({description})")
            all_exist = False
    
    return all_exist

def main():
    """Run all tests"""
    print("=" * 60)
    print("🚀 VERCEL DEPLOYMENT READINESS CHECK")
    print("=" * 60)
    
    tests = [
        ("Vercel Structure", test_vercel_structure),
        ("Python Imports", test_imports),
        ("Environment Variables", test_environment_variables),
        ("FastAPI App", test_app_creation)
    ]
    
    results = []
    
    for test_name, test_func in tests:
        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"❌ {test_name} test crashed: {e}")
            results.append((test_name, False))
    
    # Summary
    print("\n" + "=" * 60)
    print("📊 TEST SUMMARY")
    print("=" * 60)
    
    for test_name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status} - {test_name}")
    
    all_passed = all(result for _, result in results)
    
    print("\n" + "=" * 60)
    if all_passed:
        print("🎉 ALL TESTS PASSED - READY TO DEPLOY!")
        print("=" * 60)
        print("\nNext steps:")
        print("1. Commit your changes: git add . && git commit -m 'Ready for Vercel'")
        print("2. Push to GitHub: git push origin main")
        print("3. Deploy to Vercel: vercel --prod")
        print("   Or connect repository in Vercel Dashboard")
        return 0
    else:
        print("⚠️  SOME TESTS FAILED - FIX ISSUES BEFORE DEPLOYING")
        print("=" * 60)
        print("\nCheck the errors above and fix them.")
        return 1

if __name__ == "__main__":
    sys.exit(main())
