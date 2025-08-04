# 🚀 Render Deployment Guide for HackRx 6.0

## Step 1: Prepare Your Repository

1. **Push your code to GitHub**
2. **Ensure `render.yaml` is in your repository**

## Step 2: Deploy to Render

1. **Go to [render.com](https://render.com)**
2. **Sign up/Login** with your GitHub account
3. **Click "New +" → "Web Service"**
4. **Connect your GitHub repository**
5. **Configure the service**:
   - **Name**: `hackrx-query-system`
   - **Environment**: `Python 3`
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `python -m app.main`
6. **Click "Create Web Service"**

## Step 3: Configure Environment Variables

1. **Go to your service dashboard**
2. **Click "Environment" tab**
3. **Add these variables**:

```
GOOGLE_API_KEY=your_google_api_key_here
PINECONE_API_KEY=your_pinecone_api_key_here
PINECONE_ENVIRONMENT=your_pinecone_environment_here
HACKRX_API_TOKEN=018fbf34e584c6effc325d2b54ba468383140299330b71b644cb73775d410be5
```

## Step 4: Get Your Webhook URL

Your webhook URL will be:

```
https://your-app-name.onrender.com/api/v1/hackrx/run
```

## 🎉 Done!

Submit this URL for the hackathon!
