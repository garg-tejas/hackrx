# 🚀 Fly.io Deployment Guide for HackRx 6.0

## Step 1: Install Fly CLI

```bash
# Windows
powershell -Command "iwr https://fly.io/install.ps1 -useb | iex"

# macOS
curl -L https://fly.io/install.sh | sh

# Linux
curl -L https://fly.io/install.sh | sh
```

## Step 2: Login to Fly

```bash
fly auth login
```

## Step 3: Create fly.toml

```bash
fly launch
```

Choose:

- **App name**: `hackrx-query-system`
- **Region**: Choose closest to you
- **Postgres**: No (we don't need it for this demo)

## Step 4: Deploy

```bash
fly deploy
```

## Step 5: Set Environment Variables

```bash
fly secrets set GOOGLE_API_KEY=your_google_api_key_here
fly secrets set PINECONE_API_KEY=your_pinecone_api_key_here
fly secrets set PINECONE_ENVIRONMENT=your_pinecone_environment_here
fly secrets set HACKRX_API_TOKEN=018fbf34e584c6effc325d2b54ba468383140299330b71b644cb73775d410be5
```

## Step 6: Get Your Webhook URL

Your webhook URL will be:

```
https://hackrx-query-system.fly.dev/api/v1/hackrx/run
```

## 🎉 Done!

Submit this URL for the hackathon!
