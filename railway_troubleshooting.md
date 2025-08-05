# 🔧 Railway 502 Bad Gateway - Troubleshooting Guide

## The Problem

502 Bad Gateway error means Railway can't reach your application.

## The Solution

### 1. **Fix Host Binding**

The app must bind to `0.0.0.0` (not `127.0.0.1`) for Railway.

**Updated files:**

- ✅ `app/config.py` - Changed API_HOST to "0.0.0.0"
- ✅ `env.example` - Updated API_HOST
- ✅ `app/main.py` - Disabled reload for production

### 2. **Redeploy to Railway**

1. **Push your changes to GitHub**
2. **Go to Railway dashboard**
3. **Click "Deploy" again**
4. **Wait for deployment to complete**

### 3. **Check Railway Logs**

After redeployment, check the logs for:

- ✅ `INFO: Application startup complete`
- ✅ `INFO: Uvicorn running on http://0.0.0.0:8000`
- ❌ No binding errors

### 4. **Test Your Endpoints**

**Health Check:**

```bash
curl https://your-app.railway.app/health
```

**Root Endpoint:**

```bash
curl https://your-app.railway.app/
```

**Main API:**

```bash
curl -X POST "https://your-app.railway.app/api/v1/hackrx/run" \
  -H "Content-Type: application/json" \
  -d '{
    "documents": "https://example.com/test.pdf",
    "questions": ["What is the grace period?"]
  }'
```

### 5. **Common Issues & Fixes**

**Issue**: Still getting 502
**Fix**: Check Railway logs for binding errors

**Issue**: App not starting
**Fix**: Ensure all environment variables are set

**Issue**: Timeout errors
**Fix**: The first request might be slow (downloading models)

### 6. **Environment Variables**

Make sure these are set in Railway:

```
GOOGLE_API_KEY=your_google_api_key
PINECONE_API_KEY=your_pinecone_api_key
PINECONE_ENVIRONMENT=your_pinecone_environment
HACKRX_API_TOKEN=018fbf34e584c6effc325d2b54ba468383140299330b71b644cb73775d410be5
API_HOST=0.0.0.0
API_PORT=8000
```

## 🎯 **Expected Result**

After fixing, you should see:

- ✅ Health check returns `{"status": "healthy"}`
- ✅ Root endpoint returns system info
- ✅ Main API accepts POST requests
- ✅ No 502 errors

## 🚀 **For Hackathon Submission**

Once working, submit your webhook URL:

```
https://your-app.railway.app/api/v1/hackrx/run
```
