# Chat API Documentation

## Overview

The Chat API enables personalized AI conversations based on the user's quiz responses (personality profile) and live app interactions (wellness tool usage, mood tracking, etc.).

## Endpoint

```
POST /api/chat
```

## How It Works

1. **Retrieves User Persona**: Loads personality profile (from quiz) + live state (from app usage)
2. **Loads Chat History**: Optional - retrieves previous conversation for context
3. **Generates AI Response**: Uses Google Gemini 2.0 Flash with full personalization
4. **Saves to Firebase**: Stores both user message and AI response in `chat_history` collection
5. **Updates State**: Increments `chat_message_count` and updates `last_interaction`

## Personalization Factors

The AI response is tailored based on:

### From Quiz (Personality Profile)
- **Communication Style**: Logical, Emotional, or Balanced
- **Primary Stressor**: Academics, Social, Sleep, or General
- **Social Profile**: Introverted, Extroverted, or Ambiverted
- **Coping Mechanism**: Analytical, Affective, or Mixed
- **Stress Level**: Low, Moderate, or High

### From Live State (App Usage)
- **Current Mood**: Happy, Anxious, Stressed, Sad, Neutral, etc.
- **Recent Stressors**: Last 5 stressors identified (e.g., "Difficulty with Breathing Exercise")
- **Coping Successes**: Last 5 successful strategies (e.g., "Diaphragmatic Breathing - Improved mood")
- **Wellness Tools Used**: Count of breathing, grounding, mindfulness, body relaxation sessions
- **Needs Check-in**: Boolean flag if user is struggling
- **Last Interaction**: What user did most recently

### From Chat History
- Previous 50 messages for conversation continuity
- Context awareness of ongoing discussions

## Request Format

### Body Parameters

```json
{
  "user_id": "string (required)",
  "message": "string (required)",
  "include_history": "boolean (optional, default: true)"
}
```

### Example Request

```json
{
  "user_id": "OwJgNZVyzMgi9f9uSIpN6LXC57P2",
  "message": "I've been feeling really anxious about my upcoming exams",
  "include_history": true
}
```

## Response Format

### Success Response

```json
{
  "success": true,
  "response": "I hear you - exam anxiety is really tough, especially with your academic pressures. I noticed you tried Diaphragmatic Breathing earlier and it helped improve your mood. Maybe we could use that technique again before your study session? Would you like to try it now, or would you prefer to talk through what's making you most anxious about the exams?",
  "message": "Chat response generated successfully",
  "chat_history_saved": true
}
```

### Error Response

```json
{
  "success": false,
  "response": null,
  "message": "Error description",
  "chat_history_saved": false
}
```

## Example Usage Scenarios

### 1. First Chat Message

**Request:**
```json
{
  "user_id": "user123",
  "message": "Hey, I just finished the quiz",
  "include_history": false
}
```

**Response:**
```json
{
  "success": true,
  "response": "Hey there! Thanks for completing the quiz - I've learned a lot about what you're going through. I can see you're dealing with some academic stress and sometimes struggle with anxiety. I'm here to support you through that. What's on your mind right now?",
  "message": "Chat response generated successfully",
  "chat_history_saved": true
}
```

### 2. After Using Breathing Exercise

**Request:**
```json
{
  "user_id": "user123",
  "message": "I just did the breathing exercise and feel a bit better",
  "include_history": true
}
```

**Context:** User just completed Diaphragmatic Breathing with mood improvement.

**Response:**
```json
{
  "success": true,
  "response": "That's awesome! 🎉 I'm so glad the Diaphragmatic Breathing helped you feel calmer. It's great that you're building these coping strategies - using breathing exercises is one of your strengths. How are you feeling now compared to before?",
  "message": "Chat response generated successfully",
  "chat_history_saved": true
}
```

### 3. When User Needs Support

**Request:**
```json
{
  "user_id": "user123",
  "message": "Everything feels overwhelming today",
  "include_history": true
}
```

**Context:** Live state shows `needs_check_in: true`, recent stressor: "High stress in academic situation"

**Response:**
```json
{
  "success": true,
  "response": "I can tell things are feeling really heavy right now, and I want you to know that's completely valid. I noticed you've been dealing with some academic stress lately. You don't have to handle this alone. Would it help to break down what's feeling most overwhelming? Or would you prefer to try one of the grounding techniques that have helped you before?",
  "message": "Chat response generated successfully",
  "chat_history_saved": true
}
```

### 4. Crisis Situation

**Request:**
```json
{
  "user_id": "user123",
  "message": "I don't think I can do this anymore",
  "include_history": true
}
```

**Response:**
```json
{
  "success": true,
  "response": "I'm really concerned about what you're going through. Please know that you're not alone, and there are people who care about you and want to help. If you're thinking about harming yourself, please reach out immediately:\n\n🆘 National Suicide Prevention Lifeline: 988\n📱 Crisis Text Line: Text HOME to 741741\n🏥 Or go to your nearest emergency room\n\nI'm here to support you, but these trained professionals can provide the immediate help you need right now. Can you reach out to one of these resources?",
  "message": "Chat response generated successfully",
  "chat_history_saved": true
}
```

## Integration with State Updates

The chat endpoint automatically updates the user's live state:

```json
{
  "type": "chat_message",
  "content": "user's message",
  "mood": "current_mood_value"
}
```

This means:
- `chat_message_count` increments
- `last_interaction` set to "chat"
- `last_interaction_timestamp` updated
- If message contains stress keywords, added to `recent_stressors`

## Chat History Storage

Messages are stored in Firebase Firestore:

```
chat_history/
  {user_id}/
    last_message_at: timestamp
    user_id: string
    messages/
      {message_id_1}/
        role: "user"
        content: "message text"
        timestamp: timestamp
        created_at: ISO string
        metadata: { mood, etc. }
      {message_id_2}/
        role: "assistant"
        content: "AI response"
        timestamp: timestamp
        created_at: ISO string
        metadata: { model: "gemini-2.0-flash-exp" }
```

## Error Codes

| Status Code | Error | Solution |
|-------------|-------|----------|
| 400 | Message cannot be empty | Send non-empty message |
| 404 | No persona found | Call `/api/persona/generate` first |
| 500 | Google API key not configured | Set `GOOGLE_API_KEY` in `.env` |
| 500 | Failed to process chat | Check server logs for details |

## Performance

- **Average Response Time**: 2-5 seconds (Gemini API call)
- **Context Window**: Last 50 messages + full persona context
- **Token Usage**: ~500-2000 tokens per request (depends on history)

## Best Practices

1. **Generate Persona First**: Always call `/api/persona/generate` before chatting
2. **Include History**: Set `include_history: true` for better conversation flow
3. **Update State Regularly**: Call `/api/persona/update-state` when user uses wellness tools
4. **Handle Errors Gracefully**: Show friendly error messages to users
5. **Monitor Response Time**: Add loading indicators in UI

## Testing with cURL

```bash
# Test chat endpoint
curl -X POST http://localhost:5001/api/chat \
  -H "Content-Type: application/json" \
  -d '{
    "user_id": "test_user_123",
    "message": "I am feeling stressed today",
    "include_history": true
  }'
```

## Testing with Python

```python
import requests

response = requests.post(
    "http://localhost:5001/api/chat",
    json={
        "user_id": "test_user_123",
        "message": "I am feeling stressed today",
        "include_history": True
    }
)

print(response.json())
```

## Flutter Integration Example

```dart
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
    return data['response'] as String;
  } else {
    throw Exception('Failed to get chat response');
  }
}
```

## Next Steps

1. **Test the Endpoint**: Run `run.bat` and test with sample requests
2. **Integrate in Flutter**: Add chat screen that calls this endpoint
3. **Monitor Responses**: Check Firebase Console for saved chat history
4. **Customize Prompts**: Adjust system prompts in `langchain_persona_architect.py` if needed
5. **Add Features**: Consider adding typing indicators, message reactions, etc.

---

For more information, see:
- [GEMINI_MIGRATION.md](GEMINI_MIGRATION.md) - Gemini setup details
- [SETUP_GUIDE.md](SETUP_GUIDE.md) - Server setup instructions
- [README.md](README.md) - Complete API documentation
