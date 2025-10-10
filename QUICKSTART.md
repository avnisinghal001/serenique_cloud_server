# 🚀 Quick Start Guide - Serenique LangChain Integration

## What Was Built

A complete **LangChain-powered persona generation system** that:

1. ✅ Analyzes quiz responses using AI (Claude 3.5 Sonnet via OpenRouter)
2. ✅ Generates personalized chatbot personas with custom system prompts
3. ✅ Stores personas in Firebase Firestore (`user_persona` collection)
4. ✅ Updates live user state based on app interactions
5. ✅ Provides RESTful API for Flutter integration

---

## 📁 New Files Created

### Backend (serenique_cloud_server/)

1. **`langchain_persona_architect.py`** (600+ lines)
   - Main LangChain integration with OpenRouter
   - `PersonalityProfile` and `LiveUserState` Pydantic models
   - `LangChainPersonaArchitect` class with AI-powered analysis
   - Structured output parser for consistent JSON

2. **`firebase_service.py`** (300+ lines)
   - Firebase Admin SDK integration
   - Firestore operations for `user_persona` collection
   - Methods: `save_user_persona()`, `get_user_persona()`, `update_live_state()`

3. **`main.py`** (Updated)
   - New endpoints:
     - `POST /api/persona/generate` - Generate persona from quiz
     - `GET /api/persona/{user_id}` - Retrieve existing persona
     - `POST /api/persona/update-state` - Update live state
     - `GET /api/health` - Health check
     - `GET /api/stats` - Statistics

4. **`requirements.txt`** (Updated)
   - Added: `langchain`, `langchain-openai`, `langchain-core`, `firebase-admin`

5. **`LANGCHAIN_INTEGRATION_README.md`** (2000+ lines)
   - Complete documentation
   - Architecture diagrams
   - API reference
   - Setup instructions
   - Deployment guide

6. **`.env.example`**
   - Template for environment variables
   - Instructions for OpenRouter and Firebase setup

### Frontend (serenique/lib/)

7. **`services/persona_service.dart`** (New)
   - Flutter service to call LangChain server
   - Methods: `generatePersona()`, `getPersona()`, `updateUserState()`
   - Health checks and error handling

8. **`screens/quiz_screen.dart`** (Updated)
   - Now calls `PersonaService.generatePersona()` after quiz completion
   - Integrated with existing Firebase save flow

---

## ⚡ Setup in 5 Minutes

### Backend Setup

1. **Get API Keys:**
   ```bash
   # OpenRouter (for AI)
   # Sign up at: https://openrouter.ai/
   # Get API key from: https://openrouter.ai/keys
   
   # Firebase Service Account
   # Firebase Console → Project Settings → Service Accounts
   # → Generate new private key
   ```

2. **Configure Environment:**
   ```bash
   cd serenique_cloud_server
   
   # Copy example env file
   cp .env.example .env
   
   # Edit .env and add your keys
   # OPENROUTER_API_KEY=sk-or-v1-...
   # FIREBASE_CREDENTIALS='{"type":"service_account",...}'
   ```

3. **Install Dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

4. **Run Server:**
   ```bash
   uvicorn main:app --reload
   ```

5. **Test:**
   ```bash
   curl http://localhost:8000/api/health
   ```

### Flutter Setup

1. **Update Server URL:**
   ```dart
   // In lib/services/persona_service.dart
   static const String _baseUrl = 'http://localhost:8000';
   
   // For Android emulator, use:
   // static const String _baseUrl = 'http://10.0.2.2:8000';
   ```

2. **Run Flutter App:**
   ```bash
   cd serenique
   flutter pub get
   flutter run
   ```

3. **Test Flow:**
   - Sign in with test account
   - Complete quiz (all 10 questions)
   - Check console for: `✅ Persona generated successfully!`
   - Check Firestore for `user_persona/{user_id}` document

---

## 🔄 How It Works

```
User completes quiz
         ↓
Flutter sends quiz data to server
         ↓
LangChain + Claude analyzes responses
         ↓
Server generates personalityProfile:
  - communication_style (logical/emotional/balanced)
  - primary_stressor (academics/social/sleep)
  - chatbot_system_prompt (custom AI instructions)
  - strengths, vulnerabilities, coping strategies
         ↓
Server saves to Firestore: user_persona/{user_id}
         ↓
Flutter receives persona
         ↓
Chat screen loads persona's system_prompt
         ↓
AI chatbot uses personalized instructions
         ↓
User interacts → Flutter updates live_user_state
```

---

## 📊 Data Flow

### Quiz Completion
```dart
// quiz_screen.dart
await _personaService.generatePersona(_answers);
```
↓
```python
# main.py
POST /api/persona/generate
```
↓
```python
# langchain_persona_architect.py
persona = persona_architect.generate_persona(user_id, quiz_data)
```
↓
```python
# firebase_service.py
firebase_service.save_user_persona(persona)
```
↓
```
Firestore: user_persona/{user_id}
{
  personality_profile: { ... },
  live_user_state: { ... }
}
```

### Chat Initialization
```dart
// chat_screen.dart (you need to implement this)
final persona = await PersonaService().getPersona();
final systemPrompt = persona['personality_profile']['chatbot_system_prompt'];

// Use systemPrompt when calling OpenAI/Anthropic/etc.
```

### State Updates
```dart
// After user sends message
await PersonaService().updateUserState({
  'type': 'chat_message',
  'mood': 'anxious',
  'stressor_detected': 'exam stress'
});
```

---

## 🎯 Next Steps

### 1. Deploy Backend to Vercel

```bash
cd serenique_cloud_server
vercel

# Add environment variables in Vercel dashboard:
# - OPENROUTER_API_KEY
# - FIREBASE_CREDENTIALS
```

### 2. Update Flutter with Production URL

```dart
// lib/services/persona_service.dart
static const String _baseUrl = 'https://your-app.vercel.app';
```

### 3. Implement Chat Integration

In your chat screen:
```dart
import 'package:serenique/services/persona_service.dart';

class ChatScreen extends StatefulWidget {
  // ...
}

class _ChatScreenState extends State<ChatScreen> {
  Map<String, dynamic>? _persona;
  final _personaService = PersonaService();
  
  @override
  void initState() {
    super.initState();
    _loadPersona();
  }
  
  Future<void> _loadPersona() async {
    final persona = await _personaService.getPersona();
    setState(() {
      _persona = persona;
    });
    
    if (persona != null) {
      // Initialize your AI chatbot with:
      final systemPrompt = persona['personality_profile']['chatbot_system_prompt'];
      
      // Example with OpenAI:
      // _chatService.initialize(systemPrompt: systemPrompt);
    }
  }
  
  Future<void> _sendMessage(String message) async {
    // Send message to AI...
    
    // Update state
    await _personaService.updateUserState({
      'type': 'chat_message',
      'content': message,
      // Optionally detect mood from message
    });
  }
}
```

### 4. Add State Updates Throughout App

```dart
// After user uses breathing exercise
await PersonaService().updateUserState({
  'type': 'tool_use',
  'tool_name': 'breathing_exercise'
});

// After sleep log
await PersonaService().updateUserState({
  'type': 'sleep_log',
  'hours': sleepHours,
  'quality': sleepQuality
});
```

---

## 🐛 Troubleshooting

### Server won't start
```bash
# Check Python version (need 3.9+)
python --version

# Reinstall dependencies
pip install -r requirements.txt
```

### "OpenRouter API key not configured"
```bash
# Make sure .env file exists
cat .env

# Should see: OPENROUTER_API_KEY=sk-or-v1-...
```

### "Could not initialize Firebase"
```bash
# Check Firebase credentials
# Either set FIREBASE_CREDENTIALS or GOOGLE_APPLICATION_CREDENTIALS

# Test Firebase connection
python -c "from firebase_service import firebase_service; print('Firebase OK')"
```

### Flutter can't reach server
```dart
// For Android emulator:
static const String _baseUrl = 'http://10.0.2.2:8000';

// For iOS simulator:
static const String _baseUrl = 'http://localhost:8000';

// Check server is running:
// curl http://localhost:8000/api/health
```

---

## 📝 Key Concepts

### PersonalityProfile (Static)
- Generated once from quiz
- Contains:
  - Personality dimensions (communication style, stressor, etc.)
  - Chatbot system prompt (300-500 words of AI instructions)
  - Therapeutic approach recommendation
  - Proactive triggers

### LiveUserState (Dynamic)
- Updated continuously during app usage
- Contains:
  - Current mood
  - Recent stressors
  - Coping successes
  - Engagement metrics
  - Check-in flags

### System Prompt
- Custom instructions for AI chatbot
- Tailored to each user's personality
- Examples:
  - Logical user → "Use structured CBT approach, help identify thought patterns"
  - Emotional user → "Lead with empathy, validate feelings, then problem-solve"

---

## 📚 Documentation

- **Full Documentation:** `LANGCHAIN_INTEGRATION_README.md`
- **Architecture Details:** See Architecture section in README
- **API Reference:** See API Endpoints section in README
- **Deployment Guide:** See Deployment section in README

---

## ✅ Testing Checklist

- [ ] Backend server starts without errors
- [ ] Health check returns `status: healthy`
- [ ] Flutter app connects to server
- [ ] Quiz completion triggers persona generation
- [ ] Persona appears in Firestore `user_persona/{user_id}`
- [ ] Persona contains `chatbot_system_prompt`
- [ ] State updates work (test with debug action)

---

## 🎉 You're Ready!

Your Serenique app now has:
- ✅ AI-powered personality analysis
- ✅ Personalized chatbot system prompts
- ✅ Firebase storage for personas
- ✅ Live state tracking
- ✅ RESTful API for all operations

Next: Integrate the `chatbot_system_prompt` into your AI chat service!

---

**Questions? Check `LANGCHAIN_INTEGRATION_README.md` for detailed docs.**
