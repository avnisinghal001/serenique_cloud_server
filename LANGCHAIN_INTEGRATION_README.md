# Serenique LangChain Persona Architecture

## 🎯 Overview

This document describes the **LangChain-powered persona generation system** for Serenique, a mental wellness chatbot for college students. The system analyzes quiz responses using AI (OpenRouter + Claude) to create personalized chatbot personas with custom system prompts, therapeutic approaches, and behavioral patterns.

---

## 🏗️ Architecture

```
┌─────────────────┐
│  Flutter App    │
│  (Quiz Screen)  │
└────────┬────────┘
         │ 1. Quiz Data
         ▼
┌─────────────────────────────────────┐
│  Serenique Cloud Server             │
│  (FastAPI + LangChain)              │
│                                     │
│  ┌──────────────────────────────┐  │
│  │ LangChain Persona Architect  │  │
│  │                              │  │
│  │  • OpenRouter API            │  │
│  │  • Claude 3.5 Sonnet         │  │
│  │  • Structured Output Parser  │  │
│  └──────────────────────────────┘  │
│           │                         │
│           ▼                         │
│  ┌──────────────────────────────┐  │
│  │ Firebase Admin SDK           │  │
│  │ (Firestore Storage)          │  │
│  └──────────────────────────────┘  │
└────────┬────────────────────────────┘
         │ 2. User Persona
         ▼
┌─────────────────────────────────────┐
│  Firestore Database                 │
│                                     │
│  user_persona/{user_id}             │
│  ├─ personality_profile             │
│  │  ├─ communication_style          │
│  │  ├─ primary_stressor             │
│  │  ├─ social_profile               │
│  │  ├─ coping_mechanism             │
│  │  ├─ stress_level                 │
│  │  ├─ chatbot_system_prompt        │
│  │  └─ ...                          │
│  └─ live_user_state                 │
│     ├─ current_mood                 │
│     ├─ last_interaction             │
│     ├─ recent_stressors             │
│     └─ ...                          │
└─────────────────────────────────────┘
         │
         ▼
┌─────────────────┐
│  Flutter App    │
│  (Chat Screen)  │
│  Uses persona   │
│  system prompt  │
└─────────────────┘
```

---

## 📊 Data Models

### PersonalityProfile (Static - Generated from Quiz)

```json
{
  "communication_style": "logical|emotional|balanced",
  "primary_stressor": "academics|social|sleep|general",
  "social_profile": "introverted|extroverted|ambiverted",
  "coping_mechanism": "analytical|affective|mixed",
  "stress_level": "low|moderate|high",
  
  "strengths": [
    "Self-aware and reflective",
    "Proactive help-seeker",
    "Strong analytical skills"
  ],
  
  "vulnerabilities": [
    "Academic pressure sensitivity",
    "Sleep-mood connection",
    "Occasional negative self-talk"
  ],
  
  "recommended_approach": "CBT-based cognitive restructuring",
  
  "chatbot_tone": "warm yet logical, supportive but practical",
  
  "chatbot_methodology": "CBT-based: help user identify thought patterns, challenge distortions, develop action plans",
  
  "proactive_triggers": [
    "User mentions exam/deadline stress",
    "Poor sleep quality logged",
    "Negative self-talk detected"
  ],
  
  "chatbot_system_prompt": "You are Serenique, a personalized mental wellness mentor...",
  
  "generated_at": "2025-10-10T12:00:00.000Z",
  "quiz_version": "1.0"
}
```

### LiveUserState (Dynamic - Updated through App Usage)

```json
{
  "current_mood": "neutral|happy|anxious|stressed|sad|motivated|tired",
  "last_interaction": "onboarding|chat|tool_use|sleep_log",
  "last_interaction_timestamp": "2025-10-10T14:30:00.000Z",
  
  "chat_message_count": 42,
  "tool_usage_count": 8,
  "sleep_logs_count": 5,
  
  "recent_stressors": [
    "midterm exams",
    "group project deadline",
    "social anxiety"
  ],
  
  "coping_successes": [
    "Used breathing exercise",
    "Practiced journaling",
    "Reached out to friend"
  ],
  
  "needs_check_in": false,
  "last_updated": "2025-10-10T14:30:00.000Z"
}
```

---

## 🔌 API Endpoints

### 1. Generate Persona

**Endpoint:** `POST /api/persona/generate`

**Request:**
```json
{
  "user_id": "firebase_auth_uid",
  "quiz_data": {
    1: "b",
    2: "d",
    3: "a",
    4: "b",
    5: "d",
    6: "a",
    7: "a",
    8: "b",
    9: "a",
    10: "b"
  }
}
```

**Response:**
```json
{
  "success": true,
  "user_persona": {
    "user_id": "firebase_auth_uid",
    "personality_profile": { /* PersonalityProfile object */ },
    "live_user_state": { /* LiveUserState object */ }
  },
  "message": "Persona generated successfully"
}
```

**What it does:**
1. Receives quiz data from Flutter app
2. Sends to LangChain with Claude 3.5 Sonnet via OpenRouter
3. AI analyzes responses using psychological frameworks
4. Generates comprehensive personality profile with system prompt
5. Saves to Firebase Firestore `user_persona/{user_id}`
6. Returns complete persona to Flutter app

---

### 2. Get Persona

**Endpoint:** `GET /api/persona/{user_id}`

**Response:**
```json
{
  "success": true,
  "user_persona": { /* Complete UserPersona */ },
  "message": "Persona retrieved successfully"
}
```

**What it does:**
- Retrieves existing persona from Firestore
- Used by chat screen to load user's personality profile
- Returns both personality_profile and live_user_state

---

### 3. Update Live State

**Endpoint:** `POST /api/persona/update-state`

**Request:**
```json
{
  "user_id": "firebase_auth_uid",
  "action": {
    "type": "chat_message",
    "content": "I'm feeling really anxious about my exam tomorrow",
    "mood": "anxious",
    "stressor_detected": "academic stress"
  }
}
```

**Action Types:**
- `chat_message` - User sent a message
- `tool_use` - User used a mental wellness tool
- `sleep_log` - User logged sleep data

**Response:**
```json
{
  "success": true,
  "updated_state": { /* Updated LiveUserState */ },
  "message": "State updated successfully"
}
```

**What it does:**
1. Receives user action from Flutter app
2. Updates live_user_state in persona
3. Tracks engagement metrics (message count, tool usage)
4. Identifies recent stressors and coping successes
5. Sets `needs_check_in` flag if concerning patterns detected
6. Saves to Firestore and returns updated state

---

### 4. Health Check

**Endpoint:** `GET /api/health`

**Response:**
```json
{
  "status": "healthy",
  "service": "Serenique LangChain Persona Service",
  "version": "3.0.0",
  "openrouter_configured": true,
  "firebase_initialized": true
}
```

---

### 5. Statistics

**Endpoint:** `GET /api/stats`

**Response:**
```json
{
  "success": true,
  "stats": {
    "total_personas": 142,
    "recent_24h": 8,
    "timestamp": "2025-10-10T15:00:00.000Z"
  }
}
```

---

## 🚀 Setup Instructions

### Backend Setup (serenique_cloud_server)

1. **Install Dependencies:**
```bash
cd serenique_cloud_server
pip install -r requirements.txt
```

2. **Set Environment Variables:**

Create a `.env` file:
```bash
# OpenRouter API Key (required)
OPENROUTER_API_KEY=your_openrouter_api_key_here

# Firebase Service Account (choose one method)
# Method 1: JSON string
FIREBASE_CREDENTIALS='{"type":"service_account","project_id":"..."}'

# Method 2: File path
GOOGLE_APPLICATION_CREDENTIALS=/path/to/serviceAccountKey.json
```

3. **Get Firebase Service Account:**
   - Go to Firebase Console → Project Settings → Service Accounts
   - Click "Generate new private key"
   - Save as `firebase-service-account.json` in project root
   - OR copy JSON and set as `FIREBASE_CREDENTIALS` env variable

4. **Run Server:**
```bash
# Development
uvicorn main:app --reload --port 8000

# Production (Vercel will handle this automatically)
```

---

### Flutter Setup (serenique)

1. **Add HTTP Package:**

In `pubspec.yaml`:
```yaml
dependencies:
  http: ^1.1.0
```

Run:
```bash
flutter pub get
```

2. **Update Server URL:**

In `lib/services/persona_service.dart`, update:
```dart
// For local testing
static const String _baseUrl = 'http://localhost:8000';

// For production (after Vercel deployment)
static const String _baseUrl = 'https://your-app.vercel.app';
```

3. **Quiz Flow is Already Integrated:**

The `quiz_screen.dart` already calls `PersonaService` after quiz completion:
```dart
// After quiz completion:
final persona = await _personaService.generatePersona(_answers);
```

4. **Use Persona in Chat:**

In your chat screen initialization:
```dart
import 'package:serenique/services/persona_service.dart';

// Load persona when chat starts
final personaService = PersonaService();
final persona = await personaService.getPersona();

if (persona != null) {
  final systemPrompt = persona['personality_profile']['chatbot_system_prompt'];
  
  // Use this system prompt when initializing your AI chatbot
  // (OpenAI, Anthropic, or other provider)
}
```

5. **Update State During Interactions:**

```dart
// After user sends a message
await personaService.updateUserState({
  'type': 'chat_message',
  'mood': 'anxious',  // Detect from message content
  'stressor_detected': 'academic stress'
});

// After user uses a tool
await personaService.updateUserState({
  'type': 'tool_use',
  'tool_name': 'breathing_exercise'
});

// After sleep log
await personaService.updateUserState({
  'type': 'sleep_log',
  'hours': 6,
  'quality': 'poor'
});
```

---

## 📦 Deployment

### Deploy to Vercel

1. **Install Vercel CLI:**
```bash
npm install -g vercel
```

2. **Login to Vercel:**
```bash
vercel login
```

3. **Deploy:**
```bash
cd serenique_cloud_server
vercel
```

4. **Set Environment Variables in Vercel Dashboard:**
   - Go to project settings → Environment Variables
   - Add `OPENROUTER_API_KEY`
   - Add `FIREBASE_CREDENTIALS` (paste entire JSON)

5. **Update Flutter App:**
   - Update `_baseUrl` in `persona_service.dart` to your Vercel URL
   - Rebuild and deploy Flutter app

---

## 🧪 Testing

### Test Backend Locally

1. **Start Server:**
```bash
cd serenique_cloud_server
uvicorn main:app --reload
```

2. **Test Health Check:**
```bash
curl http://localhost:8000/api/health
```

3. **Test Persona Generation:**
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

### Test Flutter Integration

1. **Run Flutter App:**
```bash
cd serenique
flutter run
```

2. **Complete Quiz:**
   - Sign in with test account
   - Complete all 10 quiz questions
   - Check console logs for:
     - `✅ Quiz responses saved to Firebase`
     - `🔄 Generating AI persona...`
     - `✅ Persona generated successfully!`

3. **Check Firestore:**
   - Open Firebase Console
   - Go to Firestore Database
   - Look for `user_persona/{user_id}` document
   - Verify `personality_profile` and `live_user_state` exist

---

## 🔐 Security Considerations

1. **API Key Protection:**
   - Never commit API keys to Git
   - Use environment variables only
   - Rotate keys regularly

2. **Authentication:**
   - All requests should validate Firebase Auth tokens
   - Add middleware to verify user_id matches authenticated user

3. **Rate Limiting:**
   - Implement rate limiting on persona generation (expensive AI calls)
   - Suggested: 3 persona generations per user per day

4. **Input Validation:**
   - Quiz data must have exactly 10 questions
   - Answers must be 'a', 'b', 'c', or 'd'
   - User IDs must match Firebase Auth UIDs

---

## 📈 Monitoring

### Key Metrics to Track

1. **Persona Generation:**
   - Total personas generated
   - Success/failure rate
   - Average generation time
   - OpenRouter API usage

2. **State Updates:**
   - Update frequency per user
   - Most common action types
   - Mood distribution

3. **System Health:**
   - API response times
   - Error rates
   - Firebase connection status

---

## 🛠️ Troubleshooting

### "OpenRouter API key not configured"
- Set `OPENROUTER_API_KEY` environment variable
- Restart server after setting env variables

### "Could not initialize Firebase Admin SDK"
- Verify service account JSON is valid
- Check `FIREBASE_CREDENTIALS` or `GOOGLE_APPLICATION_CREDENTIALS` is set
- Ensure Firebase project has Firestore enabled

### "Import errors" (pydantic, langchain, etc.)
```bash
pip install -r requirements.txt
```

### Flutter "Cannot reach server"
- Check `_baseUrl` in `persona_service.dart`
- Verify server is running (`uvicorn main:app --reload`)
- For Android emulator, use `http://10.0.2.2:8000` instead of `localhost`

### Persona generation takes too long
- Claude 3.5 Sonnet typically takes 5-15 seconds
- Add loading indicator in Flutter UI
- Consider caching personas

---

## 🎨 Customization

### Change AI Model

In `main.py`:
```python
persona_architect = LangChainPersonaArchitect(
    openrouter_api_key=OPENROUTER_API_KEY,
    model_name="anthropic/claude-3-opus",  # More powerful
    # or "openai/gpt-4-turbo"
    # or "google/gemini-pro-1.5"
    temperature=0.7
)
```

### Modify Personality Dimensions

In `langchain_persona_architect.py`:
- Add new enums for additional dimensions
- Update `PersonalityProfile` model
- Modify system prompt template

### Extend Live State Tracking

In `LiveUserState` model:
- Add new fields (e.g., `therapy_goals`, `crisis_history`)
- Update `update_user_state()` logic
- Implement new action types

---

## 📚 Additional Resources

- [LangChain Documentation](https://python.langchain.com/)
- [OpenRouter API](https://openrouter.ai/docs)
- [Firebase Admin SDK](https://firebase.google.com/docs/admin/setup)
- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [Pydantic Documentation](https://docs.pydantic.dev/)

---

## 🤝 Support

For issues or questions:
1. Check Firestore for `user_persona` documents
2. Check server logs: `uvicorn main:app --reload --log-level debug`
3. Test health endpoint: `curl http://localhost:8000/api/health`
4. Verify OpenRouter API key has credits

---

**Built with ❤️ for college student mental wellness**
