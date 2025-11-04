# 🚀 Deploying Serenique FastAPI to Vercel

## Quick Deploy

[![Deploy with Vercel](https://vercel.com/button)](https://vercel.com/new/clone?repository-url=https://github.com/avnisinghal001/serenique_cloud_server)

## Prerequisites

1. **Vercel Account** - [Sign up here](https://vercel.com/signup)
2. **Firebase Project** - Get your service account credentials
3. **Google AI API Key** - Get Gemini API key from [Google AI Studio](https://makersuite.google.com/app/apikey)

## Environment Variables

You need to set these environment variables in your Vercel project:

### Required Variables

1. **`GOOGLE_API_KEY`** - Your Google Gemini API key
   ```
   AIzaSy...
   ```

2. **`FIREBASE_CREDENTIALS`** - Your Firebase service account JSON (as a string)
   ```json
   {"type":"service_account","project_id":"serenique-avni",...}
   ```

### Optional Variables

3. **`MODEL_NAME`** (default: `gemini-2.0-flash-exp`)
   ```
   gemini-2.0-flash-exp
   ```

4. **`MODEL_TEMPERATURE`** (default: `0.7`)
   ```
   0.7
   ```

## Deployment Steps

### Option 1: Deploy via Vercel Dashboard

1. **Connect GitHub Repository**
   - Go to [Vercel Dashboard](https://vercel.com/dashboard)
   - Click "New Project"
   - Import your GitHub repository: `avnisinghal001/serenique_cloud_server`

2. **Configure Environment Variables**
   - Go to Project Settings → Environment Variables
   - Add `GOOGLE_API_KEY` and `FIREBASE_CREDENTIALS`
   - Set for Production, Preview, and Development

3. **Deploy**
   - Click "Deploy"
   - Wait for build to complete
   - Your API will be live at `https://your-project.vercel.app`

### Option 2: Deploy via Vercel CLI

```bash
# Install Vercel CLI
npm i -g vercel

# Login to Vercel
vercel login

# Deploy
cd serenique_cloud_server
vercel

# Set environment variables
vercel env add GOOGLE_API_KEY
vercel env add FIREBASE_CREDENTIALS

# Deploy to production
vercel --prod
```

## Local Development

```bash
# Create virtual environment
python -m venv .venv

# Activate virtual environment
# Windows:
.venv\Scripts\activate
# Mac/Linux:
source .venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Set environment variables
# Create .env file with:
# GOOGLE_API_KEY=your_key_here
# FIREBASE_CREDENTIALS={"type":"service_account",...}

# Run with Vercel CLI (recommended)
vercel dev

# Or run with uvicorn
uvicorn main:app --reload --port 5001
```

## API Endpoints

Once deployed, your API will be available at:

- **Health Check**: `GET /api/health`
- **Generate Persona**: `POST /api/persona/generate`
- **Get Persona**: `GET /api/persona/{user_id}`
- **Chat**: `POST /api/chat`
- **Get Insights**: `GET /api/insights/{user_id}`
- **Cache Stats**: `GET /api/cache/stats`

## Project Structure

```
serenique_cloud_server/
├── api/
│   └── index.py              # Vercel entry point
├── main.py                   # FastAPI app
├── firebase_service.py       # Firebase operations
├── langchain_persona_architect.py
├── insight_extractor.py
├── requirements.txt          # Python dependencies
├── vercel.json              # Vercel configuration
├── .vercelignore            # Files to exclude from deployment
└── .gitignore               # Git ignore rules
```

## Troubleshooting

### Build Fails

**Error**: `Module not found`
- Check `requirements.txt` has all dependencies
- Verify Python version compatibility

**Error**: `Firebase initialization failed`
- Ensure `FIREBASE_CREDENTIALS` is set correctly
- Check it's valid JSON string (not file path)

### Runtime Errors

**Error**: `GOOGLE_API_KEY not set`
- Add environment variable in Vercel dashboard
- Redeploy after adding variables

**Error**: `500 Internal Server Error`
- Check Vercel Function Logs in dashboard
- Look for Firebase connection issues

### Performance Issues

**Slow responses**
- Check Gemini API quotas
- Monitor Firebase usage
- Consider upgrading Vercel plan for more compute

## Vercel Configuration

The `vercel.json` uses automatic routing:

```json
{
  "version": 2,
  "rewrites": [
    {
      "source": "/(.*)",
      "destination": "/api/index"
    }
  ]
}
```

This follows Vercel's official FastAPI deployment pattern where:
- Entry point is at `api/index.py`
- Imports the FastAPI `app` instance from `main.py`
- All routes are automatically handled

## Limitations

- **Function Size**: Max 250MB (our app is well under this)
- **Execution Time**: Max 60s for Hobby, 300s for Pro
- **Memory**: 1024MB default (sufficient for our use case)

## Support

For issues:
1. Check [Vercel Logs](https://vercel.com/dashboard)
2. Review [FastAPI on Vercel docs](https://vercel.com/docs/frameworks/fastapi)
3. Contact support: avnisinghal001@gmail.com

## License

MIT License - See LICENSE file for details
