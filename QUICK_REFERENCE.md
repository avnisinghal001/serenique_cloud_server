# 🚀 Chat Endpoint Quick Reference

## API Endpoint
```
POST http://localhost:5001/api/chat
Content-Type: application/json
```

## Minimal Request
```json
{
  "user_id": "your_user_id",
  "message": "Your message here"
}
```

## Full Request
```json
{
  "user_id": "your_user_id",
  "message": "Your message here",
  "include_history": true
}
```

## Response
```json
{
  "success": true,
  "response": "AI's personalized response",
  "message": "Chat response generated successfully",
  "chat_history_saved": true
}
```

## cURL Example
```bash
curl -X POST http://localhost:5001/api/chat \
  -H "Content-Type: application/json" \
  -d '{"user_id":"test123","message":"Hi, how are you?"}'
```

## Python Example
```python
import requests

response = requests.post(
    "http://localhost:5001/api/chat",
    json={
        "user_id": "test123",
        "message": "I'm feeling stressed",
        "include_history": True
    }
)
print(response.json()["response"])
```

## Flutter Example
```dart
import 'package:http/http.dart' as http;
import 'dart:convert';

Future<String> sendChatMessage(String userId, String message) async {
  final response = await http.post(
    Uri.parse('http://localhost:5001/api/chat'),
    headers: {'Content-Type': 'application/json'},
    body: jsonEncode({
      'user_id': userId,
      'message': message,
      'include_history': true,
    }),
  );
  
  if (response.statusCode == 200) {
    final data = jsonDecode(response.body);
    return data['response'];
  } else {
    throw Exception('Chat failed');
  }
}
```

## Before First Chat

**1. Start Server:**
```bash
cd serenique_cloud_server
run.bat
```

**2. Generate Persona (once per user):**
```bash
curl -X POST http://localhost:5001/api/persona/generate \
  -H "Content-Type: application/json" \
  -d '{
    "user_id": "test123",
    "quiz_data": {
      "1": "b", "2": "b", "3": "a", "4": "b", "5": "d",
      "6": "a", "7": "a", "8": "b", "9": "a", "10": "b"
    }
  }'
```

## Update State After Tool Usage

**Example: After Breathing Exercise**
```bash
curl -X POST http://localhost:5001/api/persona/update-state \
  -H "Content-Type: application/json" \
  -d '{
    "user_id": "test123",
    "action": {
      "type": "breathing_exercise",
      "content": {
        "afterMood": "Calm",
        "beforeMood": "Anxious",
        "technique": "Diaphragmatic Breathing",
        "moodImprovement": "Improved"
      }
    }
  }'
```

## Test Everything
```bash
python test_chat_api.py
```

## Error Codes

| Code | Error | Fix |
|------|-------|-----|
| 400 | Empty message | Send non-empty message |
| 404 | No persona | Generate persona first |
| 500 | No API key | Set GOOGLE_API_KEY in .env |

## What Makes Response Personalized?

✅ Quiz answers (communication style, stressors, etc.)  
✅ Current mood (from wellness tools)  
✅ Recent coping successes (what worked before)  
✅ Recent stressors (what user struggles with)  
✅ Previous conversation (last 50 messages)  
✅ Tool usage count (how engaged user is)  
✅ Needs check-in flag (if user struggling)  

## Firebase Data Saved

```
chat_history/
  {user_id}/
    messages/
      - User messages with timestamps
      - AI responses with timestamps
```

## Full Documentation

📄 **CHAT_API_DOCUMENTATION.md** - Complete API reference  
📄 **CHAT_WORKFLOW_GUIDE.md** - Step-by-step implementation  
📄 **CHAT_IMPLEMENTATION_SUMMARY.md** - What was added  
📄 **README.md** - All API endpoints  

## Quick Start

```bash
# 1. Start server
cd serenique_cloud_server
run.bat

# 2. Test health
curl http://localhost:5001/api/health

# 3. Generate persona
curl -X POST http://localhost:5001/api/persona/generate \
  -H "Content-Type: application/json" \
  -d '{"user_id":"test","quiz_data":{...}}'

# 4. Chat!
curl -X POST http://localhost:5001/api/chat \
  -H "Content-Type: application/json" \
  -d '{"user_id":"test","message":"Hello!"}'
```

## That's It! 🎉

Your AI chatbot is ready with:
- ✅ Personalized responses
- ✅ Conversation history
- ✅ Mood awareness
- ✅ Context retention
- ✅ Firebase storage

Now integrate it into your Flutter app! 🚀
