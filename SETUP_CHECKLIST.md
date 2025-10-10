# ✅ Serenique Setup Checklist

## Current Status: 🟡 Partially Configured

---

## ✅ Completed

- [x] **OpenRouter API Key** - Configured in `.env`
  - Key: `sk-or-v1-d731...6da2`
  - Model: `openai/gpt-4o-mini` (cost-effective)

- [x] **Firebase Project Info** - From `google-services.json`
  - Project ID: `serenique-avni`
  - Project Number: `2957169306`
  - Storage Bucket: `serenique-avni.firebasestorage.app`

- [x] **LangChain Integration** - All code ready
  - `langchain_persona_architect.py` ✓
  - `firebase_service.py` ✓
  - `main.py` with API endpoints ✓
  - Flutter `persona_service.dart` ✓

- [x] **Dependencies** - Listed in `requirements.txt`
  - FastAPI, Uvicorn
  - LangChain, LangChain-OpenAI
  - Firebase Admin SDK
  - Pydantic

---

## ⏳ Next Steps

### 1. Get Firebase Admin SDK Credentials

**Why:** Server needs this to save personas to Firestore

**How:** See `FIREBASE_SETUP.md` for detailed instructions

**Quick steps:**
```bash
# 1. Visit Firebase Console
https://console.firebase.google.com/project/serenique-avni/settings/serviceaccounts/adminsdk

# 2. Click "Generate new private key"

# 3. Save downloaded JSON as:
serenique_cloud_server/firebase-service-account.json

# 4. Update .env:
GOOGLE_APPLICATION_CREDENTIALS=./firebase-service-account.json
```

**Status:** ⏳ **TODO - Critical for production**

---

### 2. Install Python Dependencies

```bash
cd serenique_cloud_server
pip install -r requirements.txt
```

**Expected output:**
```
Successfully installed fastapi uvicorn langchain langchain-openai langchain-core firebase-admin pydantic python-dateutil
```

**Status:** ⏳ **TODO**

---

### 3. Start the Server

```bash
cd serenique_cloud_server
uvicorn main:app --reload
```

**Expected output:**
```
✅ Firebase initialized from ./firebase-service-account.json
✅ OpenRouter configured with model: openai/gpt-4o-mini
INFO:     Uvicorn running on http://127.0.0.1:8000
INFO:     Application startup complete.
```

**Status:** ⏳ **TODO - After step 1 & 2**

---

### 4. Test Backend (Health Check)

```bash
curl http://localhost:8000/api/health
```

**Expected response:**
```json
{
  "status": "healthy",
  "service": "Serenique LangChain Persona Service",
  "version": "3.0.0",
  "openrouter_configured": true,
  "firebase_initialized": true
}
```

**Status:** ⏳ **TODO - After step 3**

---

### 5. Test Persona Generation

```bash
curl -X POST http://localhost:8000/api/persona/generate \
  -H "Content-Type: application/json" \
  -d '{
    "user_id": "test_user_123",
    "quiz_data": {
      "1": "b", "2": "d", "3": "a", "4": "b", "5": "d",
      "6": "a", "7": "a", "8": "b", "9": "a", "10": "b"
    }
  }'
```

**What should happen:**
1. Takes 5-15 seconds (AI processing)
2. Returns JSON with `"success": true`
3. Creates Firestore document: `user_persona/test_user_123`

**Check Firestore:**
1. Go to Firebase Console → Firestore Database
2. Look for collection: `user_persona`
3. Document ID: `test_user_123`
4. Should contain: `personality_profile` and `live_user_state`

**Status:** ⏳ **TODO - After step 4**

---

### 6. Update Flutter App

**Update server URL:**

Edit: `serenique/lib/services/persona_service.dart`

```dart
// Line 10: Change this
static const String _baseUrl = 'http://localhost:8000';

// For Android emulator, use:
static const String _baseUrl = 'http://10.0.2.2:8000';

// For iOS simulator, use:
static const String _baseUrl = 'http://localhost:8000';
```

**Status:** ⏳ **TODO**

---

### 7. Test Flutter Integration

```bash
cd serenique
flutter pub get
flutter run
```

**Test flow:**
1. Sign in with test account
2. Complete all 10 quiz questions
3. Watch console for logs:
   ```
   ✅ Quiz responses saved to Firebase
   🔄 Generating AI persona...
   ✅ Persona generated successfully!
      Your Communication Style: logical
      Your Primary Stressor: academics
   ```

**Check Firestore:**
- Collection: `user_persona`
- Document: `{your_user_id}`
- Should have complete persona with `chatbot_system_prompt`

**Status:** ⏳ **TODO - After step 6**

---

### 8. Deploy to Vercel (Production)

```bash
cd serenique_cloud_server
vercel
```

**Configure environment variables in Vercel:**
1. Go to Vercel dashboard → Your project → Settings
2. Add environment variables:
   - `OPENROUTER_API_KEY`: `sk-or-v1-d731...6da2`
   - `FIREBASE_CREDENTIALS`: Paste entire service account JSON
   - `MODEL_NAME`: `openai/gpt-4o-mini`

**Update Flutter for production:**
```dart
static const String _baseUrl = 'https://your-app.vercel.app';
```

**Status:** ⏳ **TODO - When ready for production**

---

## 🎯 Priority Order

### Immediate (Required for testing):
1. ⏳ Get Firebase Admin SDK key
2. ⏳ Install Python dependencies
3. ⏳ Start server
4. ⏳ Test health check

### Soon (Required for Flutter integration):
5. ⏳ Test persona generation
6. ⏳ Update Flutter server URL
7. ⏳ Test end-to-end flow

### Later (Production deployment):
8. ⏳ Deploy to Vercel

---

## 📝 Notes

### Model Choice: `openai/gpt-4o-mini`

**Pros:**
- ✅ Very cost-effective (~$0.15 per 1M input tokens)
- ✅ Fast response times (2-5 seconds)
- ✅ Good quality for personality analysis
- ✅ Available on OpenRouter

**Alternative models you can use:**
```bash
# In .env, change MODEL_NAME to:

# More powerful (slower, more expensive):
MODEL_NAME=anthropic/claude-3.5-sonnet
MODEL_NAME=openai/gpt-4-turbo

# Even cheaper (faster, lower quality):
MODEL_NAME=openai/gpt-3.5-turbo

# Free tier options (with rate limits):
MODEL_NAME=google/gemini-flash-1.5
MODEL_NAME=meta-llama/llama-3-8b-instruct
```

### OpenRouter Credits

Check your balance at: https://openrouter.ai/credits

Estimated costs:
- Per persona generation: ~$0.01-0.02
- For 100 users: ~$1-2
- For 1000 users: ~$10-20

---

## 🐛 Troubleshooting

### Can't start server: "Module not found"
```bash
# Make sure you're in the right directory
cd serenique_cloud_server

# Install dependencies
pip install -r requirements.txt
```

### Firebase error: "Could not initialize"
- Follow `FIREBASE_SETUP.md` to get service account key
- Make sure file is named `firebase-service-account.json`
- Check file is in `serenique_cloud_server/` directory

### Flutter can't connect to server
- Make sure server is running (`uvicorn main:app --reload`)
- Check `_baseUrl` in `persona_service.dart`
- For Android emulator, use `http://10.0.2.2:8000`
- For physical device, use your computer's IP address

### Persona generation fails
- Check OpenRouter API key is valid
- Check you have credits at https://openrouter.ai/credits
- Try a free model: `MODEL_NAME=google/gemini-flash-1.5`

---

## 📚 Documentation

- **Quick Start:** `QUICKSTART.md`
- **Firebase Setup:** `FIREBASE_SETUP.md`
- **Complete Guide:** `LANGCHAIN_INTEGRATION_README.md`
- **Environment Template:** `.env.example`

---

## ✨ Ready to Start?

Run these commands:

```bash
# 1. Get Firebase credentials (follow FIREBASE_SETUP.md)

# 2. Install dependencies
cd serenique_cloud_server
pip install -r requirements.txt

# 3. Start server
uvicorn main:app --reload

# 4. Test in new terminal
curl http://localhost:8000/api/health

# 5. If health check passes, test persona generation
curl -X POST http://localhost:8000/api/persona/generate \
  -H "Content-Type: application/json" \
  -d '{"user_id":"test_123","quiz_data":{"1":"b","2":"d","3":"a","4":"b","5":"d","6":"a","7":"a","8":"b","9":"a","10":"b"}}'

# 6. Run Flutter app
cd ../serenique
flutter run
```

---

**Your configuration is 80% complete! Just need Firebase Admin SDK key to go live! 🚀**
