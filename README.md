# Serenique Cloud Server - Vercel Deployment Ready# Serenique Mental Wellness API - Gemini Edition



This is the **production-ready** FastAPI backend for Serenique Mental Wellness App.AI-powered mental wellness chatbot with **Google Gemini 2.0 Flash** based personalized personas using LangChain.



## 📁 Project Structure## 🚀 Features



```- **Gemini 2.0 Flash Integration**: Lightning-fast AI-powered persona generation

serenique_cloud_server/          ← ROOT (deploy this folder to Vercel)- **Peaceful Mental Health Tone**: Calm, validating, supportive communication style

├── main.py                       ← FastAPI app with all endpoints- **Long-Term Memory System**: Saves all conversations for context across sessions

├── firebase_service.py           ← Firebase Firestore operations- **LangChain Framework**: Structured output parsing and prompt engineering

├── langchain_persona_architect.py ← Gemini AI + LangChain integration- **Firebase Firestore**: Dual storage (chat_history + memories)

├── insight_extractor.py          ← Key insights for long-term memory- **FastAPI Backend**: High-performance async API

├── serenique-avni-firebase-adminsdk-*.json ← Firebase credentials- **Personalized Analysis**: Quiz-based psychological profiling

├── .env                          ← Environment variables (LOCAL ONLY)- **Live State Tracking**: Real-time mood and wellness tool usage awareness

├── .gitignore                    ← Git ignore rules

├── .vercelignore                 ← Vercel ignore rules## 🔧 Setup

├── requirements.txt              ← Python dependencies

├── vercel.json                   ← Vercel configuration### 1. Install Dependencies

├── VERCEL_DEPLOYMENT_CHECKLIST.md ← Complete deployment guide

│```bash

├── api/pip install -r requirements.txt

│   └── index.py                  ← Vercel serverless entry point```

│

└── public/                       ← Static files (if any)### 2. Configure Google API Key

```

Set your Google Gemini API key as an environment variable:

## 🚀 Quick Start (Local Development)

**Windows PowerShell:**

```bash```powershell

# 1. Install dependencies$env:GOOGLE_API_KEY="your-gemini-api-key-here"

pip install -r requirements.txt```



# 2. Set up environment variables**Linux/Mac:**

# Copy .env.example to .env and fill in your keys```bash

export GOOGLE_API_KEY="your-gemini-api-key-here"

# 3. Run the server```

python -m uvicorn main:app --reload --port 5001

**Optional Configuration:**

# 4. Open browser```bash

# http://localhost:5001       - Home pageexport MODEL_NAME="gemini-2.5-flash"  # Default model

# http://localhost:5001/docs  - API documentationexport MODEL_TEMPERATURE="0.7"            # Default temperature

``````



## 📡 API Endpoints### 3. Get Google Gemini API Key



- `POST /api/persona/generate` - Generate AI persona from quiz1. Go to [Google AI Studio](https://makersuite.google.com/app/apikey)

- `GET /api/persona/{user_id}` - Get user's persona2. Create a new API key

- `POST /api/persona/update-state` - Update user's live state3. Copy and set it as `GOOGLE_API_KEY`

- `POST /api/chat` - Chat with AI (uses persona + history + insights)

- `GET /api/insights/{user_id}` - Get key insights## 🏃 Running Locally

- `DELETE /api/insights/{user_id}/{insight_id}` - Delete insight

- `GET /api/health` - Health checkStart the development server:

- `GET /api/stats` - Statistics

- `GET /` - Home page```bash

uvicorn main:app --reload --port 5001

## 🔧 Environment Variables```



Required in `.env` (local) or Vercel Dashboard (production):Server will be available at:

- **API**: http://localhost:5001

```env- **Swagger Docs**: http://localhost:5001/docs

GOOGLE_API_KEY=your_gemini_api_key_here- **Health Check**: http://localhost:5001/api/health

MODEL_NAME=gemini-2.5-flash

MODEL_TEMPERATURE=0.7## 📡 API Endpoints

FIREBASE_PROJECT_ID=serenique-avni

```### 1. Generate Persona

Create personalized chatbot persona from quiz responses.

## 📦 Dependencies

```http

- **FastAPI** - Web frameworkPOST /api/persona/generate

- **LangChain + Google Generative AI** - Gemini 2.0 Flash integrationContent-Type: application/json

- **Firebase Admin** - Firestore database

- **Pydantic** - Data validation{

- **Python-dotenv** - Environment variables  "user_id": "user123",

  "quiz_data": {

## 🚀 Deploying to Vercel    "1": "a",

    "2": "b",

### Prerequisites    ...

- Vercel account    "10": "j"

- Vercel CLI installed: `npm install -g vercel`  }

- Firebase credentials JSON file}

- Google Gemini API key```



### Deployment Steps**Response:**

```json

1. **Login to Vercel**{

   ```bash  "success": true,

   vercel login  "user_persona": {

   ```    "user_id": "user123",

    "personality_profile": {...},

2. **Deploy**    "live_user_state": {...}

   ```bash  },

   cd serenique_cloud_server  "message": "Persona generated successfully"

   vercel --prod}

   ``````



3. **Set Environment Variables** (in Vercel Dashboard)### 2. Chat with AI

   - `GOOGLE_API_KEY` - Your Gemini API keySend message and get personalized response based on persona and history.

   - `FIREBASE_CREDENTIALS` - Entire JSON from credentials file (optional, file is included)

```http

4. **Test**POST /api/chat

   ```bashContent-Type: application/json

   curl https://your-deployment-url.vercel.app/api/health

   ```{

  "user_id": "user123",

## ⚠️ Important Notes  "message": "I'm feeling stressed about exams",

  "include_history": true

### For Vercel Deployment:}

```

1. **In-Memory Cache**: The `_chat_cache` in `firebase_service.py` won't work on serverless. See `VERCEL_DEPLOYMENT_CHECKLIST.md` for solutions.

**Response:**

2. **Firebase Credentials**: The JSON file is included in the repo for easier deployment. Make sure your repository is **PRIVATE**!```json

{

3. **Cold Starts**: First request after idle may take 3-5 seconds due to serverless cold start.  "success": true,

  "response": "I hear you - exam anxiety is really tough...",

4. **Timeouts**: Vercel Hobby plan has 10s timeout. Optimize or upgrade to Pro for 60s.  "message": "Chat response generated successfully",

  "chat_history_saved": true

## 🗂️ Migration from vc/fastapi}

```

All files have been copied from `vc/fastapi/` to root. You can safely delete the `vc/` folder:

**See [CHAT_API_DOCUMENTATION.md](CHAT_API_DOCUMENTATION.md) for detailed examples and integration guide.**

```bash

# After verifying everything works:### 3. Update User State

rm -rf vc/Update live state based on app interactions (wellness tools, mood, etc.).

```

```http

## 📚 DocumentationPOST /api/persona/update-state

Content-Type: application/json

- **Full Deployment Guide**: See `VERCEL_DEPLOYMENT_CHECKLIST.md`

- **API Documentation**: Visit `/docs` when server is running{

- **Firebase Collections**: See `FIREBASE_COLLECTIONS_DOCUMENTATION.md`  "user_id": "user123",

  "action": {

## 🧪 Testing    "type": "breathing_exercise",

    "content": {

```bash      "afterMood": "Calm",

# Health check      "beforeMood": "Anxious",

curl http://localhost:5001/api/health      "technique": "Diaphragmatic Breathing",

      "moodImprovement": "Improved"

# Generate persona (requires user_id and quiz_data)    }

curl -X POST http://localhost:5001/api/persona/generate \  }

  -H "Content-Type: application/json" \}

  -d '{"user_id": "test123", "quiz_data": {"1": "a", "2": "b", ...}}'```

```

**Supported Action Types:**

## 🐛 Troubleshooting- `chat_message` - General chat

- `breathing_exercise` - From breathing_service

### "Module not found" error- `grounding_technique` - From grounding_service

- Run `pip install -r requirements.txt`- `mindfulness_meditation` - From mindfulness_service

- `body_relaxation` - From body_relaxation_service

### "Firebase initialization failed"- `tool_use` - Generic tool usage

- Check if `serenique-avni-firebase-adminsdk-*.json` exists- `sleep_log` - Sleep tracking

- Or set `FIREBASE_CREDENTIALS` environment variable

### 4. Get Persona

### "GOOGLE_API_KEY not set"Retrieve existing persona for a user.

- Add to `.env` file locally

- Or set in Vercel environment variables```http

GET /api/persona/{user_id}

### "Timeout error"```

- Firebase queries taking too long

- Check Firebase console for issues### 5. Health Check

- Consider upgrading Vercel plan for longer timeoutCheck server status and configuration.



## 📊 Monitoring```http

GET /api/health

After deployment:```

- **Vercel Analytics**: https://vercel.com/dashboard/analytics

- **Firebase Console**: https://console.firebase.google.com## 🧠 How It Works

- **Gemini API Usage**: https://aistudio.google.com/app/apikey

1. **Quiz Analysis**: User completes mental wellness quiz in Flutter app

## 🔐 Security Notes2. **Gemini Processing**: Quiz responses sent to Gemini 2.0 Flash via LangChain

3. **Persona Generation**: AI generates personalized psychological profile

- Repository should be **PRIVATE** (Firebase credentials are included)4. **Firebase Storage**: Persona saved to Firestore

- CORS is currently set to allow all origins - restrict in production5. **Chatbot Configuration**: Profile used to personalize AI chatbot responses

- Add rate limiting before public launch

- Consider adding authentication to endpoints## 📦 Project Structure



## 📝 Version```

serenique_cloud_server/

- **Version**: 4.0.0├── main.py                          # FastAPI application

- **Last Updated**: November 6, 2025├── langchain_persona_architect.py   # Gemini + LangChain integration

- **AI Model**: Gemini 2.0 Flash├── firebase_service.py              # Firestore operations

- **Framework**: FastAPI + LangChain├── credentials.json                 # Google service account credentials

- **Database**: Firebase Firestore├── requirements.txt                 # Python dependencies

└── vercel.json                      # Vercel deployment config

## 📧 Support```



For issues or questions, refer to:## 🔑 Credentials

- `VERCEL_DEPLOYMENT_CHECKLIST.md` - Deployment troubleshooting

- FastAPI Docs: https://fastapi.tiangolo.comThe server uses `credentials.json` for Firebase Admin SDK authentication. Ensure this file is properly configured with your Firebase service account credentials.

- Vercel Docs: https://vercel.com/docs

## 🚀 Deploying to Vercel

---

```bash

**Ready for Deployment** ✅npm install -g vercel

vercel --prod

All files are in the root directory. Just run `vercel --prod` and you're live!```


Set environment variables in Vercel dashboard:
- `GOOGLE_API_KEY`: Your Gemini API key

## 🧪 Testing

Test the API using the interactive Swagger UI:
```
http://localhost:5001/docs
```

Or use curl:
```bash
curl -X POST "http://localhost:5001/api/persona/generate" \
  -H "Content-Type: application/json" \
  -d '{"user_id": "test123", "quiz_data": {"1": "a", "2": "b"}}'
```

## 📊 Monitoring

Check system health:
```bash
curl http://localhost:5001/api/health
```

Response includes:
- Service status
- Gemini configuration status
- Firebase initialization status

## 🔄 Migration from OpenRouter

This version has been migrated from OpenRouter to Google Gemini:
- **Old**: `langchain-openai` + OpenRouter
- **New**: `langchain-google-genai` + Gemini 2.0 Flash
- **Benefits**: Faster responses, better integration, cost-effective

## 📝 License

Part of the Serenique Mental Wellness platform.
