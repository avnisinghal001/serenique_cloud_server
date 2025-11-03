# Serenique Mental Wellness API - Gemini Edition

AI-powered mental wellness chatbot with **Google Gemini 2.0 Flash** based personalized personas using LangChain.

## 🚀 Features

- **Gemini 2.0 Flash Integration**: Lightning-fast AI-powered persona generation
- **Peaceful Mental Health Tone**: Calm, validating, supportive communication style
- **Long-Term Memory System**: Saves all conversations for context across sessions
- **LangChain Framework**: Structured output parsing and prompt engineering
- **Firebase Firestore**: Dual storage (chat_history + memories)
- **FastAPI Backend**: High-performance async API
- **Personalized Analysis**: Quiz-based psychological profiling
- **Live State Tracking**: Real-time mood and wellness tool usage awareness

## 🔧 Setup

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Configure Google API Key

Set your Google Gemini API key as an environment variable:

**Windows PowerShell:**
```powershell
$env:GOOGLE_API_KEY="your-gemini-api-key-here"
```

**Linux/Mac:**
```bash
export GOOGLE_API_KEY="your-gemini-api-key-here"
```

**Optional Configuration:**
```bash
export MODEL_NAME="gemini-2.0-flash-exp"  # Default model
export MODEL_TEMPERATURE="0.7"            # Default temperature
```

### 3. Get Google Gemini API Key

1. Go to [Google AI Studio](https://makersuite.google.com/app/apikey)
2. Create a new API key
3. Copy and set it as `GOOGLE_API_KEY`

## 🏃 Running Locally

Start the development server:

```bash
uvicorn main:app --reload --port 5001
```

Server will be available at:
- **API**: http://localhost:5001
- **Swagger Docs**: http://localhost:5001/docs
- **Health Check**: http://localhost:5001/api/health

## 📡 API Endpoints

### 1. Generate Persona
Create personalized chatbot persona from quiz responses.

```http
POST /api/persona/generate
Content-Type: application/json

{
  "user_id": "user123",
  "quiz_data": {
    "1": "a",
    "2": "b",
    ...
    "10": "j"
  }
}
```

**Response:**
```json
{
  "success": true,
  "user_persona": {
    "user_id": "user123",
    "personality_profile": {...},
    "live_user_state": {...}
  },
  "message": "Persona generated successfully"
}
```

### 2. Chat with AI
Send message and get personalized response based on persona and history.

```http
POST /api/chat
Content-Type: application/json

{
  "user_id": "user123",
  "message": "I'm feeling stressed about exams",
  "include_history": true
}
```

**Response:**
```json
{
  "success": true,
  "response": "I hear you - exam anxiety is really tough...",
  "message": "Chat response generated successfully",
  "chat_history_saved": true
}
```

**See [CHAT_API_DOCUMENTATION.md](CHAT_API_DOCUMENTATION.md) for detailed examples and integration guide.**

### 3. Update User State
Update live state based on app interactions (wellness tools, mood, etc.).

```http
POST /api/persona/update-state
Content-Type: application/json

{
  "user_id": "user123",
  "action": {
    "type": "breathing_exercise",
    "content": {
      "afterMood": "Calm",
      "beforeMood": "Anxious",
      "technique": "Diaphragmatic Breathing",
      "moodImprovement": "Improved"
    }
  }
}
```

**Supported Action Types:**
- `chat_message` - General chat
- `breathing_exercise` - From breathing_service
- `grounding_technique` - From grounding_service
- `mindfulness_meditation` - From mindfulness_service
- `body_relaxation` - From body_relaxation_service
- `tool_use` - Generic tool usage
- `sleep_log` - Sleep tracking

### 4. Get Persona
Retrieve existing persona for a user.

```http
GET /api/persona/{user_id}
```

### 5. Health Check
Check server status and configuration.

```http
GET /api/health
```

## 🧠 How It Works

1. **Quiz Analysis**: User completes mental wellness quiz in Flutter app
2. **Gemini Processing**: Quiz responses sent to Gemini 2.0 Flash via LangChain
3. **Persona Generation**: AI generates personalized psychological profile
4. **Firebase Storage**: Persona saved to Firestore
5. **Chatbot Configuration**: Profile used to personalize AI chatbot responses

## 📦 Project Structure

```
serenique_cloud_server/
├── main.py                          # FastAPI application
├── langchain_persona_architect.py   # Gemini + LangChain integration
├── firebase_service.py              # Firestore operations
├── credentials.json                 # Google service account credentials
├── requirements.txt                 # Python dependencies
└── vercel.json                      # Vercel deployment config
```

## 🔑 Credentials

The server uses `credentials.json` for Firebase Admin SDK authentication. Ensure this file is properly configured with your Firebase service account credentials.

## 🚀 Deploying to Vercel

```bash
npm install -g vercel
vercel --prod
```

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
