# Serenique Persona Architect System

## Overview

The Persona Architect is an AI-powered system that analyzes user quiz responses and interaction history to create highly personalized chatbot personas for the Serenique mental wellness application. Each persona defines how the chatbot communicates, provides support, and proactively assists users based on their unique psychological profile.

## System Architecture

```
User Quiz Responses → Persona Architect → Personalized System Prompt → Serenique Chatbot
                            ↓
                    Interaction History
                            ↓
                    Persona Refinement
```

## Key Features

### 1. Deep Psychological Analysis
- **Communication Style Detection**: Identifies whether users prefer logical, structured advice or emotional, empathetic support
- **Stressor Identification**: Pinpoints primary sources of stress (academics, social, sleep, general)
- **Social Profile Assessment**: Determines introversion/extroversion to guide social recommendations
- **Coping Mechanism Analysis**: Understands how users naturally process stress (analytical vs. affective)
- **Burnout Risk Assessment**: Evaluates current stress levels and burnout indicators

### 2. Dynamic Persona Generation
Each generated persona includes:
- **Analysis Summary**: Human-readable personality overview
- **Key Dimensions**: Structured personality metrics
- **Custom System Prompt**: Detailed instructions for chatbot behavior
- **Live User State**: Current mood, stress level, and interaction tracking

### 3. Behavioral Refinement
The system evolves personas based on actual user behavior:
- Tool usage patterns (e.g., preference for Pomodoro Timer vs. Journal)
- Sleep quality tracking over time
- Conversation engagement patterns
- Feature utilization metrics

## API Endpoints

### 1. Generate Persona
**Endpoint**: `POST /api/persona/generate`

**Request Body**:
```json
{
  "quiz_data": {
    "1": "b",
    "2": "c",
    "3": "c",
    "4": "c",
    "5": "b",
    "6": "c",
    "7": "a",
    "8": "b",
    "9": "c",
    "10": "a"
  },
  "past_interaction_summary": null
}
```

**Response**:
```json
{
  "personalityProfile": {
    "analysisSummary": "This user is logically-minded and solution-oriented and introverted, valuing alone time to recharge...",
    "keyDimensions": {
      "communicationStyle": "Logical",
      "primaryStressor": "Academics",
      "socialProfile": "Introverted",
      "copingMechanism": "Analytical"
    },
    "chatbotSystemPrompt": "You are Serenique, a personalized mental wellness mentor..."
  },
  "liveUserState": {
    "currentMood": "Neutral",
    "stressLevel": "High",
    "lastInteractionType": "onboarding",
    "lastUpdated": "2025-10-10T12:00:00Z",
    "lastUserInteractionSummary": null
  }
}
```

### 2. Refine Persona
**Endpoint**: `POST /api/persona/refine`

**Request Body**:
```json
{
  "quiz_data": { ... },
  "past_interaction_summary": {
    "tool_usage": {
      "pomodoro_timer": 15,
      "journal": 5,
      "meditation": 8
    },
    "sleep_logs": {
      "poor_quality_count": 7,
      "avg_hours": 5.5
    },
    "chat_metrics": {
      "avg_user_message_length": 120,
      "total_sessions": 20
    }
  }
}
```

### 3. Health Check
**Endpoint**: `GET /api/persona/health`

**Response**:
```json
{
  "status": "healthy",
  "service": "Serenique Persona Architect",
  "version": "2.0.0",
  "ready": true
}
```

## Quiz Question Mapping

The system analyzes 10 core questions to build the persona:

| Question | Purpose | Key Insights |
|----------|---------|--------------|
| Q1: Stress help preference | Communication style | Logical vs. Emotional support preference |
| Q2: Social media feelings | Social stressors | Comparison anxiety, digital wellness |
| Q3: Social battery | Social profile | Introversion/Extroversion assessment |
| Q4: Academic overwhelm | Academic stress | Burnout risk, academic pressure |
| Q5: Help value | Support needs | Validation vs. Structure preference |
| Q6: Sleep-mood connection | Sleep priority | Sleep hygiene importance |
| Q7: Problem response | Coping mechanism | Analytical vs. Affective processing |
| Q8: Screen time habits | Digital wellness | Digital overload indicators |
| Q9: Social initiation | Social comfort | Social anxiety, connection needs |
| Q10: Negative self-talk | Self-regulation | Cognitive restructuring ability |

## Personality Dimensions

### Communication Style
- **Logical**: Prefers structured, step-by-step advice and problem-solving approaches
- **Emotional**: Values empathetic listening, validation, and emotional support
- **Balanced**: Adapts between logical and emotional support as needed

### Primary Stressor
- **Academics**: Overwhelmed by exams, assignments, deadlines
- **Social**: Struggles with relationships, comparison, loneliness
- **Sleep**: Impacted by poor sleep quality and habits
- **General**: Mixed or undefined stressors

### Social Profile
- **Introverted**: Recharges through alone time, needs low-stakes social suggestions
- **Extroverted**: Energized by connection, benefits from social engagement prompts
- **Ambiverted**: Flexible social needs, context-dependent

### Coping Mechanism
- **Analytical**: Processes stress through logic, analysis, problem-solving
- **Affective**: Copes through emotional expression, connection, validation
- **Mixed**: Combines both analytical and emotional strategies

## System Prompt Structure

Each generated system prompt includes:

1. **Core Identity**: "You are Serenique, a personalized mental wellness mentor"
2. **Tone Specification**: Descriptive adjectives defining communication style
3. **Methodology**: Primary approach (CBT-based, emotion-focused, or balanced)
4. **Proactive Triggers**: Specific "if-then" conditions for offering help
5. **General Guidelines**: Best practices for student-friendly communication

Example proactive triggers:
- Academic stress → Suggest task breakdown, Pomodoro Timer
- Social anxiety → Normalize feelings, suggest gradual exposure
- Sleep issues → Prioritize sleep hygiene education
- Burnout signs → Encourage rest and self-compassion

## Integration with Flutter App

### 1. After Quiz Completion
```dart
// In quiz_screen.dart after final answer
final response = await http.post(
  Uri.parse('https://your-api.com/api/persona/generate'),
  headers: {'Content-Type': 'application/json'},
  body: jsonEncode({
    'quiz_data': quizAnswers,
    'past_interaction_summary': null
  }),
);

final persona = jsonDecode(response.body);
// Save persona to Firestore under user document
await FirebaseFirestore.instance
  .collection('users')
  .doc(userId)
  .update({'persona': persona});
```

### 2. Periodic Refinement
```dart
// After significant interaction milestones (e.g., 2 weeks of use)
final interactionSummary = {
  'tool_usage': await getToolUsageMetrics(),
  'sleep_logs': await getSleepQualityData(),
  'chat_metrics': await getChatEngagementMetrics()
};

final response = await http.post(
  Uri.parse('https://your-api.com/api/persona/refine'),
  body: jsonEncode({
    'quiz_data': originalQuizAnswers,
    'past_interaction_summary': interactionSummary
  }),
);

// Update persona in Firestore
```

### 3. Using Persona in Chat
```dart
// When initializing chat with AI
final persona = await getPersonaFromFirestore(userId);
final systemPrompt = persona['personalityProfile']['chatbotSystemPrompt'];

// Send to your AI provider (e.g., OpenAI, Anthropic)
final chatResponse = await openai.chat.completions.create(
  model: "gpt-4",
  messages: [
    {"role": "system", "content": systemPrompt},
    {"role": "user", "content": userMessage}
  ]
);
```

## Deployment

### Local Development
```bash
cd serenique_cloud_server
pip install -r requirements.txt
uvicorn main:app --reload
```

### Production (Vercel)
The system is configured for Vercel deployment with:
- FastAPI backend
- Automatic API documentation at `/docs`
- CORS enabled for Flutter app integration

## Dependencies

```txt
fastapi>=0.104.0
uvicorn>=0.24.0
pydantic>=2.4.0
python-dateutil>=2.8.2
```

## Security Considerations

1. **Data Privacy**: Quiz responses contain sensitive mental health information
   - Use HTTPS for all API calls
   - Implement proper authentication
   - Encrypt persona data at rest

2. **Rate Limiting**: Implement rate limiting to prevent abuse
   - Max 10 persona generations per user per day
   - Max 100 refinements per user per month

3. **Input Validation**: Validate all quiz responses before processing
   - Check for valid question IDs (1-10)
   - Verify answer options (a, b, c, d)

## Future Enhancements

- [ ] Multi-language support for personas
- [ ] A/B testing of different prompt structures
- [ ] Machine learning model for improved refinement
- [ ] Real-time persona adaptation based on conversation sentiment
- [ ] Integration with therapist feedback for clinical accuracy
- [ ] Persona versioning and rollback capability

## Testing

```python
# Run the example in persona_architect.py
python persona_architect.py

# Test API endpoints
curl -X POST "http://localhost:8000/api/persona/generate" \
  -H "Content-Type: application/json" \
  -d '{"quiz_data": {"1": "b", "2": "c", ...}}'
```

## Support

For questions or issues:
- GitHub Issues: [Your Repo]
- Email: [Your Email]
- Documentation: `/docs` endpoint

---

Built with ❤️ for college student mental wellness
