# 🌿 Serenique Cloud Server: AI-Powered Mental Wellness Companion# Serenique Cloud Server - Vercel Deployment Ready# Serenique Mental Wellness API - Gemini Edition

**Built by Avni Singhal** | [LinkedIn](https://www.linkedin.com/in/avnisinghal001) | [GitHub](https://github.com/avnisinghal001)



**Built With:** FastAPI ⚡ | LangChain 🧠 | Google Gemini 2.5 Flash 🤖 | Firebase 🔥 | Flutter 📱 | Vercel 🚀

This is the **production-ready** FastAPI backend for Serenique Mental Wellness App.AI-powered mental wellness chatbot with **Google Gemini 2.0 Flash** based personalized personas using LangChain.

---



## 🌸 Overview

## 📁 Project Structure## 🚀 Features

**Serenique Cloud Server** is the intelligent backend powering **Serebot** — a calm, wise, and compassionate AI mental wellness mentor designed specifically for college students. 



This isn't just another chatbot. Serenique creates a **personalized mental health companion** that:

- 🧘 Understands your unique personality through an adaptive quiz system```- **Gemini 2.0 Flash Integration**: Lightning-fast AI-powered persona generation

- 💬 Responds with empathy, grounded advice, and evidence-based therapeutic techniques

- 🎯 Recommends **context-aware wellness tools** (breathing exercises, grounding techniques, mindfulness practices)serenique_cloud_server/          ← ROOT (deploy this folder to Vercel)- **Peaceful Mental Health Tone**: Calm, validating, supportive communication style

- 📊 Tracks your emotional state and adapts its responses in real-time

- 🌙 Provides crisis support resources when detecting distress signals├── main.py                       ← FastAPI app with all endpoints- **Long-Term Memory System**: Saves all conversations for context across sessions



**Mission:** To be the calm in someone's storm — helping students move from *"I'm overwhelmed"* → *"I can handle this."*├── firebase_service.py           ← Firebase Firestore operations- **LangChain Framework**: Structured output parsing and prompt engineering



---├── langchain_persona_architect.py ← Gemini AI + LangChain integration- **Firebase Firestore**: Dual storage (chat_history + memories)



## 🛠️ Tech Stack├── insight_extractor.py          ← Key insights for long-term memory- **FastAPI Backend**: High-performance async API



| Layer | Technology |├── serenique-avni-firebase-adminsdk-*.json ← Firebase credentials- **Personalized Analysis**: Quiz-based psychological profiling

|-------|-----------|

| **Backend Framework** | FastAPI (Python 3.9+) |├── .env                          ← Environment variables (LOCAL ONLY)- **Live State Tracking**: Real-time mood and wellness tool usage awareness

| **AI Engine** | LangChain + Google Gemini 2.5 Flash |

| **Vector Intelligence** | Custom Tool Recommendation Engine |├── .gitignore                    ← Git ignore rules

| **Database** | Firebase Firestore (NoSQL) |

| **Authentication** | Firebase Auth |├── .vercelignore                 ← Vercel ignore rules## 🔧 Setup

| **Frontend** | Flutter (Dart) |

| **Deployment** | Vercel Serverless Functions |├── requirements.txt              ← Python dependencies

| **API Architecture** | RESTful with async support |

├── vercel.json                   ← Vercel configuration### 1. Install Dependencies

---

├── VERCEL_DEPLOYMENT_CHECKLIST.md ← Complete deployment guide

## ⚡️ Core Features

│```bash

✅ **AI Persona Generation** — Analyzes quiz responses to create deeply personalized mental health profiles  

✅ **Dynamic State Tracking** — Monitors mood, stress levels, and engagement in real-time  ├── api/pip install -r requirements.txt

✅ **Intelligent Tool Recommendations** — 95%+ confidence threshold for suggesting wellness exercises  

✅ **Context-Aware Conversations** — Remembers chat history and adapts tone based on emotional state  │   └── index.py                  ← Vercel serverless entry point```

✅ **13 Evidence-Based Wellness Tools** — Breathing exercises, body relaxation, grounding techniques, mindfulness meditations  

✅ **Crisis Detection & Resources** — Identifies distress signals and provides helpline information  │

✅ **Chat History Management** — Date-wise storage and retrieval with pagination support  

✅ **Insight Extraction** — Long-term memory system that identifies emotional patterns  └── public/                       ← Static files (if any)### 2. Configure Google API Key

✅ **CORS-Enabled** — Seamless Flutter app integration  

✅ **Production-Ready** — Deployed on Vercel with environment-based configuration  ```



---Set your Google Gemini API key as an environment variable:



## 📂 Project Structure## 🚀 Quick Start (Local Development)



```**Windows PowerShell:**

serenique_cloud_server/

│```bash```powershell

├── main.py                          # FastAPI application entrypoint

├── langchain_persona_architect.py   # AI persona generation & chat logic# 1. Install dependencies$env:GOOGLE_API_KEY="your-gemini-api-key-here"

├── firebase_service.py              # Firebase Firestore operations

├── insight_extractor.py             # Long-term emotional pattern analysispip install -r requirements.txt```

├── vercel.json                      # Vercel deployment config

├── requirements.txt                 # Python dependencies

├── .env                            # Environment variables (not in repo)

│# 2. Set up environment variables**Linux/Mac:**

├── api/

│   └── index.py                    # Vercel serverless handler# Copy .env.example to .env and fill in your keys```bash

│

└── vc/fastapi/                     # Vercel compatibility layerexport GOOGLE_API_KEY="your-gemini-api-key-here"

```

# 3. Run the server```

---

python -m uvicorn main:app --reload --port 5001

## 🌐 API Endpoints

**Optional Configuration:**

### 🏥 Health Check

```http# 4. Open browser```bash

GET /api/health

```# http://localhost:5001       - Home pageexport MODEL_NAME="gemini-2.5-flash"  # Default model

**Response:**

```json# http://localhost:5001/docs  - API documentationexport MODEL_TEMPERATURE="0.7"            # Default temperature

{

  "status": "healthy",``````

  "gemini_configured": true,

  "firebase_initialized": true

}

```## 📡 API Endpoints### 3. Get Google Gemini API Key



---



### 🧠 Generate Persona- `POST /api/persona/generate` - Generate AI persona from quiz1. Go to [Google AI Studio](https://makersuite.google.com/app/apikey)

```http

POST /api/persona/generate- `GET /api/persona/{user_id}` - Get user's persona2. Create a new API key

```

**Description:** Analyzes quiz responses to create a personalized mental wellness profile.- `POST /api/persona/update-state` - Update user's live state3. Copy and set it as `GOOGLE_API_KEY`



**Request Body:**- `POST /api/chat` - Chat with AI (uses persona + history + insights)

```json

{- `GET /api/insights/{user_id}` - Get key insights## 🏃 Running Locally

  "user_id": "firebase_user_id",

  "quiz_data": {- `DELETE /api/insights/{user_id}/{insight_id}` - Delete insight

    "1": "a",

    "2": "c",- `GET /api/health` - Health checkStart the development server:

    "3": "b"

  }- `GET /api/stats` - Statistics

}

```- `GET /` - Home page```bash



**Response:**uvicorn main:app --reload --port 5001

```json

{## 🔧 Environment Variables```

  "success": true,

  "user_persona": {

    "personality_profile": {

      "communication_style": "direct",Required in `.env` (local) or Vercel Dashboard (production):Server will be available at:

      "primary_stressor": "academic_pressure",

      "coping_mechanism": "problem_solving",- **API**: http://localhost:5001

      "energy_level": "moderate",

      "social_preference": "balanced"```env- **Swagger Docs**: http://localhost:5001/docs

    },

    "live_user_state": {GOOGLE_API_KEY=your_gemini_api_key_here- **Health Check**: http://localhost:5001/api/health

      "current_mood": "neutral",

      "stress_level": 5,MODEL_NAME=gemini-2.5-flash

      "engagement_level": "active"

    }MODEL_TEMPERATURE=0.7## 📡 API Endpoints

  }

}FIREBASE_PROJECT_ID=serenique-avni

```

```### 1. Generate Persona

---

Create personalized chatbot persona from quiz responses.

### 💬 Chat with Serebot

```http## 📦 Dependencies

POST /api/chat

``````http

**Description:** Send messages to Serebot and receive personalized, empathetic responses with tool recommendations.

- **FastAPI** - Web frameworkPOST /api/persona/generate

**Request Body:**

```json- **LangChain + Google Generative AI** - Gemini 2.0 Flash integrationContent-Type: application/json

{

  "user_id": "firebase_user_id",- **Firebase Admin** - Firestore database

  "message": "I'm feeling really anxious about my exams tomorrow",

  "include_history": true- **Pydantic** - Data validation{

}

```- **Python-dotenv** - Environment variables  "user_id": "user123",



**Response:**  "quiz_data": {

```json

{## 🚀 Deploying to Vercel    "1": "a",

  "success": true,

  "response": "I hear how stressful this feels right now. Exam anxiety is really common, and it's okay to feel this way...",    "2": "b",

  "recommended_tools": {

    "box_breathing": 98.5,### Prerequisites    ...

    "four_seven_eight_breathing": 96.2,

    "mental_grounding": 95.8- Vercel account    "10": "j"

  },

  "chat_history_saved": true- Vercel CLI installed: `npm install -g vercel`  }

}

```- Firebase credentials JSON file}



---- Google Gemini API key```



### 📜 Get Chat History

```http

GET /api/chat/history/{user_id}?limit=50### Deployment Steps**Response:**

```

**Description:** Retrieve paginated chat history for a user.```json



**Response:**1. **Login to Vercel**{

```json

{   ```bash  "success": true,

  "success": true,

  "user_id": "firebase_user_id",   vercel login  "user_persona": {

  "message_count": 24,

  "messages": [   ```    "user_id": "user123",

    {

      "role": "user",    "personality_profile": {...},

      "content": "I'm feeling anxious",

      "timestamp": "2025-11-12T14:30:00Z"2. **Deploy**    "live_user_state": {...}

    },

    {   ```bash  },

      "role": "assistant",

      "content": "I hear you...",   cd serenique_cloud_server  "message": "Persona generated successfully"

      "timestamp": "2025-11-12T14:30:05Z",

      "recommended_tools": {   vercel --prod}

        "box_breathing": 98.5

      }   ``````

    }

  ]

}

```3. **Set Environment Variables** (in Vercel Dashboard)### 2. Chat with AI



---   - `GOOGLE_API_KEY` - Your Gemini API keySend message and get personalized response based on persona and history.



### 📅 Get Chat History by Date   - `FIREBASE_CREDENTIALS` - Entire JSON from credentials file (optional, file is included)

```http

GET /api/chat/history/{user_id}/date?date=2025-11-12&limit=50```http

```

**Description:** Retrieve chat history for a specific date.4. **Test**POST /api/chat



---   ```bashContent-Type: application/json



### 🔄 Update User State   curl https://your-deployment-url.vercel.app/api/health

```http

POST /api/persona/update-state   ```{

```

**Description:** Update live emotional state based on user interactions.  "user_id": "user123",



**Request Body:**## ⚠️ Important Notes  "message": "I'm feeling stressed about exams",

```json

{  "include_history": true

  "user_id": "firebase_user_id",

  "action": {### For Vercel Deployment:}

    "type": "tool_use",

    "tool_name": "box_breathing",```

    "duration": 5

  }1. **In-Memory Cache**: The `_chat_cache` in `firebase_service.py` won't work on serverless. See `VERCEL_DEPLOYMENT_CHECKLIST.md` for solutions.

}

```**Response:**



---2. **Firebase Credentials**: The JSON file is included in the repo for easier deployment. Make sure your repository is **PRIVATE**!```json



## 🛡️ Environment Variables{



Create a `.env` file in the project root:3. **Cold Starts**: First request after idle may take 3-5 seconds due to serverless cold start.  "success": true,



```env  "response": "I hear you - exam anxiety is really tough...",

# Google Gemini API

GOOGLE_API_KEY=your_gemini_api_key_here4. **Timeouts**: Vercel Hobby plan has 10s timeout. Optimize or upgrade to Pro for 60s.  "message": "Chat response generated successfully",

MODEL_NAME=gemini-2.5-flash

MODEL_TEMPERATURE=0.7  "chat_history_saved": true



# Firebase Configuration## 🗂️ Migration from vc/fastapi}

FIREBASE_PROJECT_ID=your_firebase_project_id

FIREBASE_PRIVATE_KEY=your_firebase_private_key```

FIREBASE_CLIENT_EMAIL=your_firebase_client_email

All files have been copied from `vc/fastapi/` to root. You can safely delete the `vc/` folder:

# LangSmith (Optional - for AI observability)

LANGSMITH_API_KEY=your_langsmith_api_key**See [CHAT_API_DOCUMENTATION.md](CHAT_API_DOCUMENTATION.md) for detailed examples and integration guide.**

LANGSMITH_ENDPOINT=https://api.smith.langchain.com

LANGSMITH_PROJECT=serenique```bash



# Server Configuration# After verifying everything works:### 3. Update User State

PORT=8000

ENVIRONMENT=productionrm -rf vc/Update live state based on app interactions (wellness tools, mood, etc.).

```

```

---

```http

## 🚀 Local Setup

## 📚 DocumentationPOST /api/persona/update-state

### 1️⃣ Clone the Repository

```bashContent-Type: application/json

git clone https://github.com/avnisinghal001/serenique_cloud_server.git

cd serenique_cloud_server- **Full Deployment Guide**: See `VERCEL_DEPLOYMENT_CHECKLIST.md`

```

- **API Documentation**: Visit `/docs` when server is running{

### 2️⃣ Create Virtual Environment

```bash- **Firebase Collections**: See `FIREBASE_COLLECTIONS_DOCUMENTATION.md`  "user_id": "user123",

python -m venv venv

source venv/bin/activate  # On Windows: venv\Scripts\activate  "action": {

```

## 🧪 Testing    "type": "breathing_exercise",

### 3️⃣ Install Dependencies

```bash    "content": {

pip install -r requirements.txt

``````bash      "afterMood": "Calm",



### 4️⃣ Set Up Environment Variables# Health check      "beforeMood": "Anxious",

```bash

cp .env.example .envcurl http://localhost:5001/api/health      "technique": "Diaphragmatic Breathing",

# Edit .env with your actual credentials

```      "moodImprovement": "Improved"



### 5️⃣ Run the Server# Generate persona (requires user_id and quiz_data)    }

```bash

uvicorn main:app --reload --host 0.0.0.0 --port 8000curl -X POST http://localhost:5001/api/persona/generate \  }

```

  -H "Content-Type: application/json" \}

### 6️⃣ Access API Documentation

Open your browser and navigate to:  -d '{"user_id": "test123", "quiz_data": {"1": "a", "2": "b", ...}}'```

- 📄 Swagger UI: `http://localhost:8000/docs`

- 📘 ReDoc: `http://localhost:8000/redoc````



---**Supported Action Types:**



## 🐳 Docker Deployment## 🐛 Troubleshooting- `chat_message` - General chat



```bash- `breathing_exercise` - From breathing_service

# Build Docker image

docker build -t serenique-server .### "Module not found" error- `grounding_technique` - From grounding_service



# Run container- Run `pip install -r requirements.txt`- `mindfulness_meditation` - From mindfulness_service

docker run -d -p 8000:8000 --env-file .env --name serenique-container serenique-server

```- `body_relaxation` - From body_relaxation_service



Server will be available at: `http://localhost:8000`### "Firebase initialization failed"- `tool_use` - Generic tool usage



---- Check if `serenique-avni-firebase-adminsdk-*.json` exists- `sleep_log` - Sleep tracking



## ☁️ Vercel Deployment- Or set `FIREBASE_CREDENTIALS` environment variable



This project is configured for **Vercel Serverless Deployment**.### 4. Get Persona



### Deploy Steps:### "GOOGLE_API_KEY not set"Retrieve existing persona for a user.

1. Push code to GitHub

2. Import project in Vercel Dashboard- Add to `.env` file locally

3. Add environment variables in Vercel settings

4. Deploy! 🚀- Or set in Vercel environment variables```http



**Live API:** `https://sereniquecloudserver.vercel.app`GET /api/persona/{user_id}



---### "Timeout error"```



## 🧠 System Architecture- Firebase queries taking too long



```- Check Firebase console for issues### 5. Health Check

┌─────────────────────┐

│  Flutter Mobile App │- Consider upgrading Vercel plan for longer timeoutCheck server status and configuration.

│    (Frontend UI)    │

└──────────┬──────────┘

           │

           ↓## 📊 Monitoring```http

┌─────────────────────┐

│   FastAPI Server    │GET /api/health

│  (Vercel Serverless)│

└──────────┬──────────┘After deployment:```

           │

    ┌──────┴───────┐- **Vercel Analytics**: https://vercel.com/dashboard/analytics

    │              │

    ↓              ↓- **Firebase Console**: https://console.firebase.google.com## 🧠 How It Works

┌─────────┐  ┌──────────────┐

│Firebase │  │ Google Gemini│- **Gemini API Usage**: https://aistudio.google.com/app/apikey

│Firestore│  │  2.5 Flash   │

└─────────┘  └──────────────┘1. **Quiz Analysis**: User completes mental wellness quiz in Flutter app

    │              │

    └──────┬───────┘## 🔐 Security Notes2. **Gemini Processing**: Quiz responses sent to Gemini 2.0 Flash via LangChain

           │

           ↓3. **Persona Generation**: AI generates personalized psychological profile

    ┌──────────────┐

    │  LangChain   │- Repository should be **PRIVATE** (Firebase credentials are included)4. **Firebase Storage**: Persona saved to Firestore

    │ Orchestration│

    └──────────────┘- CORS is currently set to allow all origins - restrict in production5. **Chatbot Configuration**: Profile used to personalize AI chatbot responses

           │

           ↓- Add rate limiting before public launch

    ┌──────────────────────┐

    │ Tool Recommendation  │- Consider adding authentication to endpoints## 📦 Project Structure

    │  Engine (95%+ conf)  │

    └──────────────────────┘

```

## 📝 Version```

---

serenique_cloud_server/

## 🎯 Key Algorithms

- **Version**: 4.0.0├── main.py                          # FastAPI application

### 1. **Persona Generation**

Uses LangChain + Gemini to analyze quiz responses and generate:- **Last Updated**: November 6, 2025├── langchain_persona_architect.py   # Gemini + LangChain integration

- **Personality Profile** (static traits)

- **Live User State** (dynamic emotional state)- **AI Model**: Gemini 2.0 Flash├── firebase_service.py              # Firestore operations

- **Therapeutic Approach** recommendations

- **Custom System Prompt** for personalized interactions- **Framework**: FastAPI + LangChain├── credentials.json                 # Google service account credentials



### 2. **Tool Recommendation Engine**- **Database**: Firebase Firestore├── requirements.txt                 # Python dependencies

- **Primary Method:** LLM-based intelligent scoring (0-100 scale)

- **Fallback Method:** Enhanced keyword matching with context boosting└── vercel.json                      # Vercel deployment config

- **Threshold:** 95%+ confidence for display

- **13 Wellness Tools** across 4 categories## 📧 Support```



### 3. **Context-Aware Chat**

- Loads last 10 messages for context

- Analyzes sentiment and emotional stateFor issues or questions, refer to:## 🔑 Credentials

- Adapts tone based on user's current mood

- Remembers key insights from past conversations- `VERCEL_DEPLOYMENT_CHECKLIST.md` - Deployment troubleshooting



### 4. **Crisis Detection**- FastAPI Docs: https://fastapi.tiangolo.comThe server uses `credentials.json` for Firebase Admin SDK authentication. Ensure this file is properly configured with your Firebase service account credentials.

Identifies keywords related to:

- Self-harm- Vercel Docs: https://vercel.com/docs

- Suicidal ideation

- Severe distress## 🚀 Deploying to Vercel



Responds with immediate compassion and crisis resources.---



---```bash



## 🧘 Wellness Tools (13 Total)**Ready for Deployment** ✅npm install -g vercel



### 🌬️ Breathing Exercisesvercel --prod

1. **Diaphragmatic Breathing** — Deep belly relaxation

2. **Box Breathing** — Mental clarity & focusAll files are in the root directory. Just run `vercel --prod` and you're live!```

3. **4-7-8 Breathing** — Sleep & deep relaxation

4. **Pursed-Lip Breathing** — Quick anxiety relief

Set environment variables in Vercel dashboard:

### 🧘 Body Relaxation- `GOOGLE_API_KEY`: Your Gemini API key

5. **Body Mapping** — Visual tension identification

6. **Wave Breathing** — Rhythmic calm with visual guide## 🧪 Testing

7. **Self-Hug** — Self-compassion technique

Test the API using the interactive Swagger UI:

### 🌍 Grounding Techniques```

8. **5-4-3-2-1 Method** — Sensory groundinghttp://localhost:5001/docs

9. **Texture Focus** — Tactile grounding```

10. **Mental Grounding** — Cognitive prompts

Or use curl:

### 🧘‍♀️ Mindfulness Meditation```bash

11. **Body Scan Meditation** — Progressive relaxationcurl -X POST "http://localhost:5001/api/persona/generate" \

12. **Mindful Walking** — Moving meditation  -H "Content-Type: application/json" \

13. **Mindful Eating** — Sensory awareness  -d '{"user_id": "test123", "quiz_data": {"1": "a", "2": "b"}}'

```

---

## 📊 Monitoring

## 📊 Database Schema (Firebase Firestore)

Check system health:

### Collection: `user_personas````bash

```jsoncurl http://localhost:5001/api/health

{```

  "user_id": "string",

  "personality_profile": {Response includes:

    "communication_style": "string",- Service status

    "primary_stressor": "string",- Gemini configuration status

    "coping_mechanism": "string"- Firebase initialization status

  },

  "live_user_state": {## 🔄 Migration from OpenRouter

    "current_mood": "string",

    "stress_level": "number",This version has been migrated from OpenRouter to Google Gemini:

    "engagement_level": "string"- **Old**: `langchain-openai` + OpenRouter

  },- **New**: `langchain-google-genai` + Gemini 2.0 Flash

  "created_at": "timestamp",- **Benefits**: Faster responses, better integration, cost-effective

  "updated_at": "timestamp"

}## 📝 License

```

Part of the Serenique Mental Wellness platform.

### Collection: `chat_history/{user_id}/messages`
```json
{
  "role": "user|assistant",
  "content": "string",
  "created_at": "timestamp",
  "recommended_tools": {
    "tool_name": "score (0-100)"
  }
}
```

### Collection: `users/{user_id}/saved_chats`
```json
{
  "date": "YYYY-MM-DD",
  "saved_at": "timestamp",
  "message_count": "number"
}
```

---

## 🚀 Future Roadmap

- [ ] **Voice Integration** — Speech-to-text for easier interaction
- [ ] **Multilingual Support** — Hindi, Spanish, French translations
- [ ] **Mood Tracking Visualization** — Charts and graphs for emotional trends
- [ ] **Group Therapy Sessions** — Anonymous peer support groups
- [ ] **Integration with Wearables** — Heart rate, sleep data from smartwatches
- [ ] **Advanced Analytics Dashboard** — For mental health professionals
- [ ] **Push Notifications** — Gentle check-ins and reminders
- [ ] **Offline Mode** — Core features without internet
- [ ] **Journaling Feature** — Reflective writing prompts
- [ ] **Emergency Contact System** — Quick access to trusted friends/family

---

## 🤝 Contributing

Contributions are welcome! Please follow these steps:

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

---

## 📄 License

This project is licensed under the **MIT License** — see the [LICENSE](LICENSE) file for details.

---

## 🙏 Acknowledgments

- **LangChain** — For the powerful AI orchestration framework
- **Google Gemini** — For the intelligent language model
- **Firebase** — For the scalable backend infrastructure
- **FastAPI** — For the lightning-fast API framework
- **Vercel** — For seamless serverless deployment
- **Flutter** — For the beautiful cross-platform mobile app
- **Open Source Community** — For inspiration and support

---

## ✨ Built with ❤️ by [Avni Singhal](https://github.com/avnisinghal001)

> *"Creating safe harbors in the digital world. One calm conversation at a time."* 🌿

---

## 🌟 Star this repo if you believe in accessible mental health support!

[![GitHub stars](https://img.shields.io/github/stars/avnisinghal001/serenique_cloud_server?style=social)](https://github.com/avnisinghal001/serenique_cloud_server)
[![GitHub forks](https://img.shields.io/github/forks/avnisinghal001/serenique_cloud_server?style=social)](https://github.com/avnisinghal001/serenique_cloud_server/fork)
[![GitHub issues](https://img.shields.io/github/issues/avnisinghal001/serenique_cloud_server)](https://github.com/avnisinghal001/serenique_cloud_server/issues)

---

### 📬 Connect with Me

- **LinkedIn:** [Avni Singhal](https://www.linkedin.com/in/avnisinghal001)
- **GitHub:** [@avnisinghal001](https://github.com/avnisinghal001)

---

*Made with peace, purpose, and Python* 🐍🌿
