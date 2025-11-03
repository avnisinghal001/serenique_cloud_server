# Gemini Migration Guide

## ✅ Completed Migration

The Serenique server has been successfully migrated from OpenRouter to **Google Gemini 2.0 Flash**.

## 🔄 Changes Made

### 1. **Dependencies Updated** (`requirements.txt`)
- ❌ Removed: `langchain-openai`
- ✅ Added: `langchain-google-genai`
- ✅ Added: `google-generativeai`

### 2. **LangChain Persona Architect** (`langchain_persona_architect.py`)
- Changed from `ChatOpenAI` to `ChatGoogleGenerativeAI`
- Updated initialization parameters:
  ```python
  # OLD (OpenRouter)
  ChatOpenAI(
      model=model_name,
      openai_api_key=openrouter_api_key,
      openai_api_base="https://openrouter.ai/api/v1"
  )
  
  # NEW (Gemini)
  ChatGoogleGenerativeAI(
      model=model_name,
      google_api_key=google_api_key,
      convert_system_message_to_human=True
  )
  ```

### 3. **Main API** (`main.py`)
- Updated to load credentials from `credentials.json`
- Changed environment variable from `OPENROUTER_API_KEY` to `GOOGLE_API_KEY`
- Updated default model to `gemini-2.0-flash-exp`
- Updated health check endpoint
- Refreshed HTML homepage

### 4. **Documentation** (`README.md`)
- Complete rewrite for Gemini integration
- Updated setup instructions
- Added API key acquisition guide

## 🚀 How to Use

### Step 1: Install Dependencies
```bash
pip install -r requirements.txt
```

### Step 2: Get Gemini API Key
1. Visit [Google AI Studio](https://makersuite.google.com/app/apikey)
2. Click "Create API Key"
3. Copy your API key

### Step 3: Set Environment Variable
**Windows PowerShell:**
```powershell
$env:GOOGLE_API_KEY="AIza..."
```

**Linux/Mac/Git Bash:**
```bash
export GOOGLE_API_KEY="AIza..."
```

### Step 4: Run Server
```bash
uvicorn main:app --reload --port 5001
```

### Step 5: Test
Visit http://localhost:5001/api/health

Expected response:
```json
{
  "status": "healthy",
  "service": "Serenique Gemini Persona Service",
  "version": "4.0.0",
  "gemini_configured": true,
  "firebase_initialized": true
}
```

## 🔑 Environment Variables

| Variable | Required | Default | Description |
|----------|----------|---------|-------------|
| `GOOGLE_API_KEY` | ✅ Yes | None | Your Gemini API key |
| `MODEL_NAME` | ❌ No | `gemini-2.0-flash-exp` | Gemini model to use |
| `MODEL_TEMPERATURE` | ❌ No | `0.7` | Model creativity (0.0-1.0) |

## 📊 Model Options

Available Gemini models:
- `gemini-2.0-flash-exp` (Recommended - Fast & efficient)
- `gemini-1.5-flash` (Stable release)
- `gemini-1.5-pro` (More capable, slower)

## 🎯 Benefits of Gemini

1. **Faster Response Times**: Gemini 2.0 Flash is optimized for speed
2. **Better Integration**: Direct Google Cloud integration
3. **Cost Effective**: Competitive pricing with generous free tier
4. **Reliable**: No intermediary services (was using OpenRouter)
5. **Latest AI**: Access to Google's newest models

## 🔧 Troubleshooting

### "GOOGLE_API_KEY not set"
- Make sure to set the environment variable before running the server
- Use `echo $env:GOOGLE_API_KEY` (PowerShell) or `echo $GOOGLE_API_KEY` (Bash) to verify

### Import errors
- Run `pip install -r requirements.txt` to ensure all dependencies are installed
- May need to restart terminal after installation

### "gemini_configured": false
- Check that environment variable is properly set
- Restart the server after setting the variable

## 📝 Code Examples

### Generating a Persona
```python
from langchain_google_genai import ChatGoogleGenerativeAI

llm = ChatGoogleGenerativeAI(
    model="gemini-2.0-flash-exp",
    temperature=0.7,
    google_api_key=os.getenv("GOOGLE_API_KEY")
)

response = llm.invoke("Analyze this quiz data...")
```

### Testing via API
```bash
curl -X POST "http://localhost:5001/api/persona/generate" \
  -H "Content-Type: application/json" \
  -d '{
    "user_id": "test123",
    "quiz_data": {
      "1": "a",
      "2": "b",
      "3": "c"
    }
  }'
```

## 🎉 Migration Complete!

Your Serenique server is now powered by Google Gemini 2.0 Flash. The migration maintains all existing functionality while providing better performance and reliability.

**Next Steps:**
1. Set your `GOOGLE_API_KEY` environment variable
2. Run `pip install -r requirements.txt`
3. Start the server with `uvicorn main:app --reload --port 5001`
4. Test the `/api/health` endpoint
5. Generate your first persona!

## 📞 Support

If you encounter any issues:
1. Check the server logs for error messages
2. Verify environment variables are set correctly
3. Ensure Firebase credentials are properly configured
4. Check the Swagger docs at `/docs` for API details
