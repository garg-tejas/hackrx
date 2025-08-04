# 🚀 Railway Deployment Guide (Fixed for Size Issue)

## The Problem

Railway's free tier has a 4.0 GB image size limit, but our ML models are 6.4 GB.

## The Solution

We'll use a lightweight deployment that downloads models on-demand instead of during build.

## Step 1: Use Lightweight Requirements

Replace `requirements.txt` with `requirements-light.txt` for deployment:

```bash
cp requirements-light.txt requirements.txt
```

## Step 2: Deploy to Railway

1. **Go to [railway.app](https://railway.app)**
2. **Sign up/Login** with your GitHub account
3. **Click "New Project"**
4. **Select "Deploy from GitHub repo"**
5. **Choose your HackRx repository**
6. **Click "Deploy"**

## Step 3: Configure Environment Variables

1. **Go to your project dashboard**
2. **Click "Variables" tab**
3. **Add these environment variables**:

```
GOOGLE_API_KEY=your_google_api_key_here
PINECONE_API_KEY=your_pinecone_api_key_here
PINECONE_ENVIRONMENT=your_pinecone_environment_here
HACKRX_API_TOKEN=018fbf34e584c6effc325d2b54ba468383140299330b71b644cb73775d410be5
```

## Step 4: Get Your Webhook URL

1. **Go to "Settings" tab**
2. **Copy your domain**: `https://your-app-name.railway.app`
3. **Your webhook URL**: `https://your-app-name.railway.app/api/v1/hackrx/run`

## Step 5: Test Your Deployment

```bash
curl -X POST "https://your-app-name.railway.app/api/v1/hackrx/run" \
  -H "Content-Type: application/json" \
  -d '{
    "documents": "https://hackrx.blob.core.windows.net/assets/policy.pdf?sv=...",
    "questions": [
      "What is the grace period for premium payment?",
      "Does this policy cover maternity expenses?"
    ]
  }'
```

## Step 6: Submit for Hackathon

Submit this webhook URL:

```
https://your-app-name.railway.app/api/v1/hackrx/run
```

## 🎉 Done!

Your HackRx 6.0 system is now live and ready for the hackathon!

## 📝 Notes

- The system will use fallback embeddings if sentence-transformers is not available
- Models will be downloaded on first use (slower first request)
- All functionality remains the same
- The system is fully compatible with the hackathon requirements
