# 🚀 Vercel Deployment Guide for Serenique API

## ✅ Pre-Deployment Checklist

### 1. **Files Created**
- ✅ `api/index.py` - Vercel serverless entry point
- ✅ `.vercelignore` - Excludes sensitive files from deployment
- ✅ `.gitignore` - Prevents credentials from being committed
- ✅ `vercel.json` - Vercel configuration
- ✅ `requirements.txt` - Pinned Python dependencies

### 2. **Security Setup**
- ✅ Firebase credentials excluded from deployment
- ✅ Environment variable support configured
- ⚠️ **ACTION REQUIRED**: Set up Vercel environment variables (see below)

---

## 🔐 Environment Variables Setup

Before deploying, you **MUST** configure these environment variables in Vercel:

### Step 1: Get Your Firebase Credentials JSON

Open your Firebase service account file:
```
serenique-avni-firebase-adminsdk-fbsvc-99c2461c94.json
```

Copy the **ENTIRE** contents (it's a JSON object).

### Step 2: Add to Vercel Dashboard

1. Go to: https://vercel.com/dashboard
2. Select your project (or import it first)
3. Go to: **Settings** → **Environment Variables**
4. Add the following variables:

| Variable Name | Value | Environment |
|--------------|-------|-------------|
| `FIREBASE_CREDENTIALS` | *[Paste entire JSON from your credentials file]* | Production, Preview, Development |
| `GOOGLE_API_KEY` | *[Your Gemini API key]* | Production, Preview, Development |
| `MODEL_NAME` | `gemini-2.0-flash-exp` | Production, Preview, Development |
| `MODEL_TEMPERATURE` | `0.7` | Production, Preview, Development |

**Important Notes:**
- For `FIREBASE_CREDENTIALS`, paste the **entire JSON content** (starts with `{` and ends with `}`)
- Make sure to select all three environments (Production, Preview, Development)
- Don't add quotes around the JSON - paste it directly

---

## 📦 Deployment Steps

### Option 1: Deploy via Vercel CLI (Recommended)

```bash
# Install Vercel CLI globally
npm install -g vercel

# Navigate to project directory
cd serenique_cloud_server

# Login to Vercel
vercel login

# Deploy to production
vercel --prod
```

### Option 2: Deploy via GitHub Integration

1. Push your code to GitHub:
   ```bash
   git add .
   git commit -m "Prepare for Vercel deployment"
   git push origin main
   ```

2. Go to [Vercel Dashboard](https://vercel.com/dashboard)
3. Click **"Add New Project"**
4. Import your GitHub repository
5. Vercel will auto-detect settings from `vercel.json`
6. Add environment variables (see section above)
7. Click **"Deploy"**

### Option 3: Deploy via Vercel Dashboard (Manual Upload)

1. Go to [Vercel Dashboard](https://vercel.com/dashboard)
2. Click **"Add New Project"**
3. Click **"Browse"** and select your `serenique_cloud_server` folder
4. Add environment variables (see section above)
5. Click **"Deploy"**

---

## 🧪 Testing Your Deployment

Once deployed, Vercel will give you a URL like:
```
https://serenique-cloud-server.vercel.app
```

### Test Endpoints

1. **Health Check**
   ```bash
   curl https://your-app.vercel.app/api/health
   ```
   Expected: `{"status": "healthy", ...}`

2. **API Documentation**
   Visit: `https://your-app.vercel.app/docs`
   
3. **Test Persona Generation**
   ```bash
   curl -X POST https://your-app.vercel.app/api/persona/generate \
     -H "Content-Type: application/json" \
     -d '{
       "user_id": "test_user_123",
       "quiz_data": {
         "1": "a", "2": "b", "3": "a", "4": "c", "5": "b",
         "6": "a", "7": "b", "8": "c", "9": "a", "10": "b"
       }
     }'
   ```

---

## ⚠️ Known Issues & Limitations

### 1. **In-Memory Cache Won't Work**

**Problem:** The current caching system uses in-memory dictionaries:
```python
self._chat_cache: Dict[str, Dict] = {}
```

This won't work on Vercel because each serverless function invocation is stateless.

**Impact:**
- Cache won't persist between requests
- Performance will be slower than local development
- Each request will query Firebase directly

**Solutions:**
1. **Remove caching** (simple but slower):
   - Change `use_cache=False` in all calls
   
2. **Implement Vercel KV** (recommended):
   - Use Vercel's built-in key-value store
   - Requires Vercel Pro plan
   
3. **Use Redis/Upstash** (best for production):
   - External Redis instance
   - Works with any serverless platform

**Quick Fix for Now:**
Update `firebase_service.py` to disable cache on serverless:
```python
import os

# Detect if running on Vercel
IS_SERVERLESS = os.getenv("VERCEL") == "1"

def get_chat_history_optimized(self, user_id: str, limit: int = 10, use_cache: bool = True):
    # Disable cache on serverless platforms
    if IS_SERVERLESS:
        use_cache = False
    # ... rest of code
```

### 2. **Cold Start Latency**

First request after inactivity may take 5-10 seconds due to:
- Python runtime initialization
- Firebase connection setup
- LangChain model loading

**Mitigation:**
- Use Vercel Pro for faster cold starts
- Implement warming function (ping endpoint every 5 minutes)
- Consider switching to Edge Runtime for critical paths

### 3. **Function Timeout**

Vercel has a 10-second timeout on Hobby plan, 60 seconds on Pro.

**If you get timeouts:**
- Upgrade to Pro plan
- Optimize Gemini API calls
- Reduce chat history context

---

## 🔒 Security Best Practices

### ✅ Already Implemented
- Firebase credentials excluded from Git and Vercel deployment
- Environment variables for sensitive data
- CORS configured (currently allows all origins)

### ⚠️ To Do Before Production
1. **Restrict CORS origins** in `main.py`:
   ```python
   app.add_middleware(
       CORSMiddleware,
       allow_origins=["https://your-flutter-app.com"],  # ← Update this
       allow_credentials=True,
       allow_methods=["*"],
       allow_headers=["*"],
   )
   ```

2. **Add rate limiting** (prevent API abuse):
   ```bash
   pip install slowapi
   ```

3. **Add request validation** (prevent malicious input)

4. **Enable HTTPS only** (Vercel does this by default)

5. **Add API key authentication** (optional but recommended)

---

## 🎯 Flutter App Configuration

Update your Flutter app to use the Vercel URL:

```dart
// lib/services/api_service.dart
class ApiService {
  static const String baseUrl = "https://your-app.vercel.app";
  
  // Rest of your API calls
}
```

---

## 📊 Monitoring & Logs

### View Logs in Vercel
1. Go to your project dashboard
2. Click **"Deployments"**
3. Select a deployment
4. Click **"Functions"** tab
5. View logs for each function invocation

### View Firebase Usage
1. Go to [Firebase Console](https://console.firebase.google.com)
2. Check Firestore read/write counts
3. Monitor usage to stay within free tier limits

---

## 🆘 Troubleshooting

### Error: "GOOGLE_API_KEY not set"
**Solution:** Add `GOOGLE_API_KEY` environment variable in Vercel dashboard

### Error: "Could not initialize Firebase Admin SDK"
**Solution:** Add `FIREBASE_CREDENTIALS` environment variable (entire JSON content)

### Error: "Function timeout"
**Solution:** Upgrade to Vercel Pro or optimize code to run faster

### Error: "Module not found"
**Solution:** Make sure all dependencies are in `requirements.txt` and redeployed

### Cache not working
**Expected:** This is normal on serverless. See "Known Issues" section above.

---

## 🎉 Success Indicators

Your deployment is successful when:
- ✅ Health check endpoint returns `{"status": "healthy"}`
- ✅ API docs are accessible at `/docs`
- ✅ Persona generation works (test with Postman/curl)
- ✅ Firebase queries execute successfully
- ✅ Gemini API responses are generated
- ✅ No errors in Vercel function logs

---

## 📞 Support

If you encounter issues:
1. Check Vercel function logs
2. Verify environment variables are set correctly
3. Test locally with `vercel dev` before production deployment
4. Check Firebase and Gemini API quotas

---

## 🚀 Next Steps After Deployment

1. **Test all endpoints** with real Flutter app
2. **Monitor Firebase usage** (Firestore read/write counts)
3. **Monitor Gemini API costs** (check Google Cloud billing)
4. **Implement rate limiting** (prevent abuse)
5. **Add analytics** (track usage patterns)
6. **Set up monitoring alerts** (for errors and downtime)
7. **Consider caching solution** (Vercel KV or Redis)
8. **Optimize cold start time** (if needed)

---

**Deployment Date:** November 4, 2025  
**Version:** 4.0.0  
**Platform:** Vercel Serverless Functions  
**Runtime:** Python 3.9+
