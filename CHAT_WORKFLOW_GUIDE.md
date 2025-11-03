# Complete Chat Integration Workflow

## Overview

This guide shows the complete workflow for integrating personalized AI chat into your Serenique app.

## Architecture

```
Flutter App
    ↓
1. User completes quiz
    ↓
2. POST /api/persona/generate → Saves to Firebase
    ↓
3. User interacts with app (wellness tools)
    ↓
4. POST /api/persona/update-state → Updates LiveUserState
    ↓
5. User sends chat message
    ↓
6. POST /api/chat → AI response with full context
    ↓
7. Response displayed in Flutter chat UI
```

## Step-by-Step Implementation

### Step 1: Generate Persona (Once per user)

**When:** After user completes onboarding quiz

**Request:**
```bash
curl -X POST http://localhost:5001/api/persona/generate \
  -H "Content-Type: application/json" \
  -d '{
    "user_id": "user123",
    "quiz_data": {
      "1": "b",
      "2": "b",
      "3": "a",
      "4": "b",
      "5": "d",
      "6": "a",
      "7": "a",
      "8": "b",
      "9": "a",
      "10": "b"
    }
  }'
```

**What It Does:**
- Analyzes quiz responses using Gemini AI
- Creates PersonalityProfile (static)
- Creates LiveUserState (dynamic)
- Saves to Firebase `user_persona` collection
- Returns complete persona object

**Response:**
```json
{
  "success": true,
  "user_persona": {
    "user_id": "user123",
    "personality_profile": {
      "communication_style": "logical",
      "primary_stressor": "academics",
      "social_profile": "introverted",
      "coping_mechanism": "analytical",
      "stress_level": "moderate",
      "chatbot_system_prompt": "You are Serenique...",
      ...
    },
    "live_user_state": {
      "current_mood": "neutral",
      "chat_message_count": 0,
      "tool_usage_count": 0,
      "recent_stressors": [],
      "coping_successes": [],
      "needs_check_in": false
    }
  },
  "message": "Persona generated successfully"
}
```

### Step 2: Update State (Throughout app usage)

**When:** User uses wellness tools, logs sleep, etc.

**Example: After Breathing Exercise**

```bash
curl -X POST http://localhost:5001/api/persona/update-state \
  -H "Content-Type: application/json" \
  -d '{
    "user_id": "user123",
    "action": {
      "type": "breathing_exercise",
      "content": {
        "afterMood": "Calm",
        "beforeMood": "Anxious",
        "technique": "Diaphragmatic Breathing",
        "moodImprovement": "Improved",
        "sessionQuality": "Excellent",
        "completed": true,
        "pausedTimes": 0,
        "roundsCompleted": 5
      }
    }
  }'
```

**What It Does:**
- Updates `current_mood` to "calm"
- Increments `tool_usage_count`
- Adds "Diaphragmatic Breathing - Improved mood" to `coping_successes`
- Sets `needs_check_in` to false (user is doing well)
- Updates timestamps

**Response:**
```json
{
  "success": true,
  "updated_state": {
    "current_mood": "calm",
    "chat_message_count": 0,
    "tool_usage_count": 1,
    "coping_successes": ["Diaphragmatic Breathing - Improved mood"],
    "needs_check_in": false,
    ...
  },
  "message": "State updated successfully"
}
```

### Step 3: Chat with AI (Anytime)

**When:** User sends message in chat screen

**Request:**
```bash
curl -X POST http://localhost:5001/api/chat \
  -H "Content-Type: application/json" \
  -d '{
    "user_id": "user123",
    "message": "I just did the breathing exercise and feel better!",
    "include_history": true
  }'
```

**What AI Sees:**
```
Personality Profile:
- Communication Style: logical
- Primary Stressor: academics
- Coping Mechanism: analytical

Live State:
- Current Mood: calm
- Tool Usage: 1 (Diaphragmatic Breathing)
- Coping Successes: ["Diaphragmatic Breathing - Improved mood"]
- Needs Check-in: false

User Message: "I just did the breathing exercise and feel better!"
```

**Response:**
```json
{
  "success": true,
  "response": "That's awesome! 🎉 I'm so glad the Diaphragmatic Breathing helped you feel calmer. It's great that you're building these coping strategies. The fact that you completed the exercise and your mood improved from anxious to calm is a real win. How are you feeling now - ready to tackle what's ahead, or do you want to talk about what was making you anxious?",
  "message": "Chat response generated successfully",
  "chat_history_saved": true
}
```

**What Happens:**
1. Retrieves user's persona from Firebase
2. Loads last 50 chat messages for context
3. Builds comprehensive system prompt with persona + state
4. Calls Gemini AI with full context
5. Saves user message to `chat_history/{user_id}/messages`
6. Saves AI response to `chat_history/{user_id}/messages`
7. Updates LiveUserState (increments `chat_message_count`)

### Step 4: Continue Conversation

**Next Message:**
```bash
curl -X POST http://localhost:5001/api/chat \
  -H "Content-Type: application/json" \
  -d '{
    "user_id": "user123",
    "message": "I have a big exam tomorrow and feeling nervous",
    "include_history": true
  }'
```

**Response (with context awareness):**
```json
{
  "success": true,
  "response": "I hear you - exam anxiety is really tough, especially with your academic pressures. Since the breathing exercise worked so well for you earlier, maybe we could use that technique again to help calm your nerves? Or would you prefer to talk through what's making you most nervous about the exam? Sometimes breaking it down helps.",
  "message": "Chat response generated successfully",
  "chat_history_saved": true
}
```

**Why This Response:**
- AI remembers previous breathing exercise success
- Knows academics is primary stressor
- References it working earlier in conversation
- Offers both logical (break it down) and affective (breathing) approaches
- Matches user's analytical coping mechanism

## Flutter Integration Example

### 1. Service Class

```dart
// lib/services/chat_service.dart

import 'dart:convert';
import 'package:http/http.dart' as http;

class ChatService {
  static const String baseUrl = 'http://localhost:5001';
  
  Future<String> sendMessage(String userId, String message) async {
    try {
      final response = await http.post(
        Uri.parse('$baseUrl/api/chat'),
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
        throw Exception('Failed to get response: ${response.body}');
      }
    } catch (e) {
      print('Error sending message: $e');
      rethrow;
    }
  }
  
  Future<void> updateState(String userId, String actionType, Map<String, dynamic> content) async {
    try {
      await http.post(
        Uri.parse('$baseUrl/api/persona/update-state'),
        headers: {'Content-Type': 'application/json'},
        body: jsonEncode({
          'user_id': userId,
          'action': {
            'type': actionType,
            'content': content,
          },
        }),
      );
    } catch (e) {
      print('Error updating state: $e');
    }
  }
}
```

### 2. Chat Screen

```dart
// lib/screens/chat_screen.dart

import 'package:flutter/material.dart';
import '../services/chat_service.dart';

class ChatScreen extends StatefulWidget {
  final String userId;
  
  const ChatScreen({required this.userId});
  
  @override
  _ChatScreenState createState() => _ChatScreenState();
}

class _ChatScreenState extends State<ChatScreen> {
  final ChatService _chatService = ChatService();
  final TextEditingController _messageController = TextEditingController();
  final List<ChatMessage> _messages = [];
  bool _isLoading = false;
  
  Future<void> _sendMessage() async {
    final message = _messageController.text.trim();
    if (message.isEmpty) return;
    
    setState(() {
      _messages.add(ChatMessage(text: message, isUser: true));
      _isLoading = true;
      _messageController.clear();
    });
    
    try {
      final response = await _chatService.sendMessage(widget.userId, message);
      
      setState(() {
        _messages.add(ChatMessage(text: response, isUser: false));
        _isLoading = false;
      });
    } catch (e) {
      setState(() {
        _messages.add(ChatMessage(
          text: "Sorry, I couldn't process that. Please try again.",
          isUser: false,
        ));
        _isLoading = false;
      });
    }
  }
  
  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(title: Text('Chat with Serenique')),
      body: Column(
        children: [
          Expanded(
            child: ListView.builder(
              itemCount: _messages.length,
              itemBuilder: (context, index) {
                return ChatBubble(message: _messages[index]);
              },
            ),
          ),
          if (_isLoading)
            Padding(
              padding: EdgeInsets.all(8.0),
              child: CircularProgressIndicator(),
            ),
          _buildMessageInput(),
        ],
      ),
    );
  }
  
  Widget _buildMessageInput() {
    return Padding(
      padding: EdgeInsets.all(8.0),
      child: Row(
        children: [
          Expanded(
            child: TextField(
              controller: _messageController,
              decoration: InputDecoration(
                hintText: 'Type a message...',
                border: OutlineInputBorder(),
              ),
              onSubmitted: (_) => _sendMessage(),
            ),
          ),
          SizedBox(width: 8),
          IconButton(
            icon: Icon(Icons.send),
            onPressed: _sendMessage,
          ),
        ],
      ),
    );
  }
}

class ChatMessage {
  final String text;
  final bool isUser;
  
  ChatMessage({required this.text, required this.isUser});
}

class ChatBubble extends StatelessWidget {
  final ChatMessage message;
  
  const ChatBubble({required this.message});
  
  @override
  Widget build(BuildContext context) {
    return Align(
      alignment: message.isUser ? Alignment.centerRight : Alignment.centerLeft,
      child: Container(
        margin: EdgeInsets.all(8),
        padding: EdgeInsets.all(12),
        decoration: BoxDecoration(
          color: message.isUser ? Colors.blue : Colors.grey[300],
          borderRadius: BorderRadius.circular(12),
        ),
        child: Text(
          message.text,
          style: TextStyle(
            color: message.isUser ? Colors.white : Colors.black,
          ),
        ),
      ),
    );
  }
}
```

### 3. Update State After Tool Usage

```dart
// After user completes breathing exercise
await _chatService.updateState(
  userId,
  'breathing_exercise',
  {
    'afterMood': 'Calm',
    'beforeMood': 'Anxious',
    'technique': 'Diaphragmatic Breathing',
    'moodImprovement': 'Improved',
    'sessionQuality': 'Excellent',
    'completed': true,
  },
);
```

## Testing Workflow

### 1. Start Server
```bash
cd serenique_cloud_server
run.bat
```

### 2. Run Test Script
```bash
python test_chat_api.py
```

### 3. Manual Testing with cURL

**Generate Persona:**
```bash
curl -X POST http://localhost:5001/api/persona/generate -H "Content-Type: application/json" -d "{\"user_id\":\"test123\",\"quiz_data\":{\"1\":\"b\",\"2\":\"b\",\"3\":\"a\",\"4\":\"b\",\"5\":\"d\",\"6\":\"a\",\"7\":\"a\",\"8\":\"b\",\"9\":\"a\",\"10\":\"b\"}}"
```

**Send Chat:**
```bash
curl -X POST http://localhost:5001/api/chat -H "Content-Type: application/json" -d "{\"user_id\":\"test123\",\"message\":\"Hi, I'm feeling stressed\",\"include_history\":true}"
```

### 4. Check Firebase Console

Navigate to:
- `user_persona/{user_id}` - See personality profile and live state
- `chat_history/{user_id}/messages` - See all chat messages

## Common Issues & Solutions

### Issue: "No persona found"
**Solution:** Generate persona first with `/api/persona/generate`

### Issue: "Google API key not configured"
**Solution:** Set `GOOGLE_API_KEY` in `.env` file or environment

### Issue: Chat responses are generic
**Solution:** Ensure you're calling `/api/persona/update-state` after tool usage

### Issue: AI doesn't remember previous messages
**Solution:** Set `include_history: true` in chat request

## Next Steps

1. ✅ Start the server: `run.bat`
2. ✅ Test with `test_chat_api.py`
3. ✅ Integrate chat screen in Flutter
4. ✅ Update state after each tool usage
5. ✅ Monitor Firebase for saved data
6. ✅ Customize system prompts if needed
7. ✅ Deploy to production (see deployment guide)

## Related Documentation

- [CHAT_API_DOCUMENTATION.md](CHAT_API_DOCUMENTATION.md) - Detailed API reference
- [GEMINI_MIGRATION.md](GEMINI_MIGRATION.md) - Gemini setup guide
- [SETUP_GUIDE.md](SETUP_GUIDE.md) - Server setup instructions
- [README.md](README.md) - Main documentation
