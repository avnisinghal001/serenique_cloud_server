# 🔑 Firebase Admin SDK Setup Guide

## Why You Need This

Your server needs **Firebase Admin SDK credentials** to:
- Store user personas in Firestore (`user_persona` collection)
- Read quiz data from the `users` collection
- Update user documents with persona generation status

Currently, the `.env` file only has basic Firebase project info (project ID, storage bucket), which is **NOT enough** for server-side Firestore operations.

---

## 📥 Step-by-Step: Get Your Service Account Key

### 1. Go to Firebase Console

Visit: https://console.firebase.google.com/project/serenique-avni/settings/serviceaccounts/adminsdk

Or manually:
1. Go to https://console.firebase.google.com/
2. Select your project: **serenique-avni**
3. Click the ⚙️ gear icon (Project Settings)
4. Click **Service Accounts** tab

### 2. Generate New Private Key

1. You'll see a section called **Firebase Admin SDK**
2. Click the button: **"Generate new private key"**
3. A popup will warn you about keeping it secure
4. Click **"Generate key"**

### 3. Download the JSON File

- A file named something like `serenique-avni-firebase-adminsdk-xxxxx-xxxxxxxxxx.json` will download
- This file contains your private key - **NEVER commit it to Git!**

### 4. Save the File

**Option A: Local Development (Recommended)**

Save the downloaded file as:
```
serenique_cloud_server/firebase-service-account.json
```

Then update your `.env`:
```bash
GOOGLE_APPLICATION_CREDENTIALS=./firebase-service-account.json
```

**Option B: Production/Vercel (Recommended for deployment)**

1. Open the downloaded JSON file in a text editor
2. Copy the **entire contents** (should start with `{"type":"service_account",...`)
3. Update your `.env`:
```bash
FIREBASE_CREDENTIALS='{"type":"service_account","project_id":"serenique-avni","private_key_id":"...","private_key":"-----BEGIN PRIVATE KEY-----\n...\n-----END PRIVATE KEY-----\n","client_email":"firebase-adminsdk-xxxxx@serenique-avni.iam.gserviceaccount.com",...}'
```

---

## ✅ Verify Setup

### Test 1: Start Server

```bash
cd serenique_cloud_server
uvicorn main:app --reload
```

You should see:
```
✅ Firebase initialized from ...
✅ OpenRouter configured with model: openai/gpt-4o-mini
INFO:     Uvicorn running on http://127.0.0.1:8000
```

### Test 2: Health Check

Open a new terminal:
```bash
curl http://localhost:8000/api/health
```

Expected response:
```json
{
  "status": "healthy",
  "service": "Serenique LangChain Persona Service",
  "version": "3.0.0",
  "openrouter_configured": true,
  "firebase_initialized": true
}
```

### Test 3: Generate Test Persona

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

This should:
1. Take 5-15 seconds (AI analysis)
2. Return a JSON response with `"success": true`
3. Create a document in Firestore: `user_persona/test_user_123`

---

## 🔐 Security Notes

### ⚠️ IMPORTANT: Never Commit Private Keys!

The `.gitignore` already includes:
```
firebase-service-account.json
serviceAccountKey.json
*-firebase-adminsdk-*.json
.env
```

But always double-check before committing:
```bash
git status
# Make sure no service account files are listed
```

### For Production (Vercel):

1. **Never** put service account JSON in your code
2. Use Vercel's environment variables:
   - Go to Vercel dashboard → Project Settings → Environment Variables
   - Add `FIREBASE_CREDENTIALS` with the full JSON as value
   - Or add `GOOGLE_APPLICATION_CREDENTIALS` with file path (if using Vercel's file system)

---

## 🐛 Troubleshooting

### Error: "Could not initialize Firebase Admin SDK"

**Cause:** No valid credentials found

**Solution:**
1. Check that `firebase-service-account.json` exists in `serenique_cloud_server/`
2. Or check that `FIREBASE_CREDENTIALS` is set in `.env`
3. Verify the JSON is valid (no syntax errors)

### Error: "Permission denied" when accessing Firestore

**Cause:** Service account doesn't have proper permissions

**Solution:**
1. Go to Firebase Console → Firestore Database
2. Make sure Firestore is initialized (not in "locked mode")
3. Check Firestore Rules allow server-side access
4. Verify service account has "Firebase Admin" role

### Error: "Invalid credentials"

**Cause:** Wrong project or expired key

**Solution:**
1. Generate a **new** private key from Firebase Console
2. Delete the old `firebase-service-account.json`
3. Save the new one and restart the server

---

## 📋 Current Configuration Status

### ✅ Already Configured:
- OpenRouter API Key: `sk-or-v1-d731...6da2`
- Model: `openai/gpt-4o-mini` (cost-effective, fast)
- Firebase Project: `serenique-avni`

### ⏳ Needs Configuration:
- Firebase Admin SDK service account key

---

## 🚀 Quick Commands

```bash
# Install dependencies
cd serenique_cloud_server
pip install -r requirements.txt

# Start server
uvicorn main:app --reload

# Test in another terminal
curl http://localhost:8000/api/health

# Check logs
# Look for: "✅ Firebase initialized from..."
```

---

## 📞 Support

If you encounter issues:
1. Check server logs for error messages
2. Verify all steps above were completed
3. Try generating a new service account key
4. Make sure Firestore is enabled in Firebase Console

---

**Once Firebase is configured, your server will be fully operational! 🎉**
