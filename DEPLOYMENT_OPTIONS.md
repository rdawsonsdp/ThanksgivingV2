# Deployment Options (Non-Serverless)

Since Vercel uses serverless functions which can be complex, here are alternative deployment options:

## Option 1: Railway.app (Recommended - Easiest)

**Pros:**
- Easy Python/Flask deployment
- Free tier available
- Automatic deployments from GitHub
- Simple environment variable setup

**Steps:**
1. Go to https://railway.app
2. Sign up/login with GitHub
3. Click "New Project" → "Deploy from GitHub repo"
4. Select `rdawsonsdp/ThanksgivingV2`
5. Railway will auto-detect Python
6. Add environment variable: `GOOGLE_CREDENTIALS_BASE64` (from your .env file)
7. Deploy!

**Configuration:**
- Railway auto-detects `requirements.txt`
- Runs `app.py` automatically
- Port is set via `PORT` environment variable (Railway sets this)

## Option 2: Render.com

**Pros:**
- Free tier available
- Easy Flask deployment
- Automatic GitHub deployments

**Steps:**
1. Go to https://render.com
2. Sign up/login
3. Click "New" → "Web Service"
4. Connect GitHub repo: `rdawsonsdp/ThanksgivingV2`
5. Settings:
   - **Build Command:** `pip install -r requirements.txt`
   - **Start Command:** `gunicorn app:app`
   - **Environment:** Python 3
6. Add environment variable: `GOOGLE_CREDENTIALS_BASE64`
7. Deploy!

**Note:** You'll need to add `gunicorn` to `requirements.txt`

## Option 3: Fly.io

**Pros:**
- Good free tier
- Global deployment
- Docker-based (but can auto-detect Python)

**Steps:**
1. Install Fly CLI: `curl -L https://fly.io/install.sh | sh`
2. Run: `fly launch`
3. Follow prompts
4. Add secrets: `fly secrets set GOOGLE_CREDENTIALS_BASE64="<value>"`
5. Deploy: `fly deploy`

## Option 4: Heroku

**Pros:**
- Well-established platform
- Good documentation

**Cons:**
- Paid (no free tier anymore)

**Steps:**
1. Install Heroku CLI
2. `heroku create your-app-name`
3. `git push heroku main`
4. `heroku config:set GOOGLE_CREDENTIALS_BASE64="<value>"`
5. Add `Procfile` with: `web: gunicorn app:app`

## Option 5: DigitalOcean App Platform

**Pros:**
- Reliable
- Good performance

**Steps:**
1. Go to DigitalOcean App Platform
2. Create app from GitHub
3. Select Python
4. Add environment variables
5. Deploy

## Recommended: Railway.app

Railway is the easiest option - it auto-detects everything and you just need to:
1. Connect GitHub repo
2. Add the environment variable
3. Deploy

No Procfile, no build commands, no complex configuration needed!

