# How to View Logs on Vercel

## Method 1: Vercel Dashboard (Easiest)

1. **Go to your Vercel project:**
   - Visit https://vercel.com/dashboard
   - Click on your project (e.g., "ThanksgivingV2")

2. **View Function Logs:**
   - Click on the **"Functions"** tab (or "Deployments" → select a deployment)
   - Click on a specific function (e.g., `app.py`)
   - You'll see all `stdout` and `stderr` output here

3. **View Deployment Logs:**
   - Go to **"Deployments"** tab
   - Click on the latest deployment
   - Scroll down to see build logs and function invocation logs
   - Look for sections labeled "Function Logs" or "Runtime Logs"

4. **Real-time Logs:**
   - In the deployment view, you can see real-time logs as requests come in
   - Errors will be highlighted in red

## Method 2: Vercel CLI (More Detailed)

1. **Install Vercel CLI** (if not already installed):
   ```bash
   npm install -g vercel
   ```

2. **Login:**
   ```bash
   vercel login
   ```

3. **View logs:**
   ```bash
   # View logs for your project
   vercel logs [your-project-url]
   
   # Follow logs in real-time
   vercel logs [your-project-url] --follow
   
   # Filter by function
   vercel logs [your-project-url] --function=app.py
   ```

## Method 3: Check Function Invocation Logs

When you see a 500 error:

1. **In the Vercel Dashboard:**
   - Go to **"Functions"** tab
   - Click on the function that failed (usually `app.py`)
   - Look for the specific invocation ID (e.g., `cle1::kdqw4-1763387961225-77d04428f430`)
   - Click on it to see detailed logs for that specific request

2. **What to look for:**
   - Lines starting with timestamps (our logging format)
   - Error messages with `✗` prefix
   - Full tracebacks
   - Environment variable status
   - Import errors
   - Credential loading errors

## What Our Logs Show

Our verbose logging outputs to `stderr`, which Vercel captures. You'll see:

- `INFO` messages: Normal operation (imports, data loading, etc.)
- `ERROR` messages: Problems (failed imports, credential errors, etc.)
- Tracebacks: Full Python stack traces for errors

## Quick Access

**Direct link format:**
```
https://vercel.com/[your-team]/[your-project]/functions
```

Or navigate:
```
Dashboard → Your Project → Functions → app.py → View Logs
```

## Troubleshooting

If you don't see logs:
1. Make sure the deployment completed successfully
2. Try triggering a request to generate logs
3. Check that the function is actually being invoked (not a routing issue)
4. Look in the "Deployments" tab for build-time errors

