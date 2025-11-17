# Vercel Deployment Setup

## Current Configuration

The app is configured to deploy on Vercel using their native Python/Flask support.

### Key Files:
- `app.py` - Main Flask application (auto-detected by Vercel)
- `vercel.json` - Vercel configuration
- `requirements.txt` - Python dependencies
- `public/` - Static files (automatically served by Vercel)

### Environment Variables Required:

1. **GOOGLE_CREDENTIALS_BASE64** - Base64-encoded Google Service Account credentials

   To get this value:
   ```bash
   # On Mac/Linux:
   cat long-canto-360620-6858c5a01c13.json | base64 | pbcopy
   
   # Or manually encode and copy the entire output
   ```

### Deployment Steps:

1. **Push to GitHub:**
   ```bash
   git push thanksgivingv2 main
   ```

2. **In Vercel Dashboard:**
   - Go to your project settings
   - Navigate to "Environment Variables"
   - Add: `GOOGLE_CREDENTIALS_BASE64` = (paste base64-encoded credentials)
   - Save

3. **Redeploy:**
   - Vercel will automatically redeploy when you push to GitHub
   - Or manually trigger a deployment from the Vercel dashboard

### How It Works:

- Vercel auto-detects Flask apps with an `app` instance in `app.py`
- Uses `@vercel/python` builder to create serverless functions
- All routes (`/` and `/api/*`) are handled by the Flask app
- Static files in `public/` are served automatically
- The Flask app serves `index.html` for the root route and handles API routes

### Troubleshooting:

If you see "Function Invocation Failed":
1. **Check Vercel logs** (see VERCEL_LOGS.md for details):
   - Go to Vercel Dashboard → Your Project → Functions → app.py
   - Or: Deployments → Latest Deployment → Function Logs
   - Look for detailed error messages and tracebacks
2. Verify `GOOGLE_CREDENTIALS_BASE64` is set correctly
3. Ensure all dependencies in `requirements.txt` are compatible
4. Check that `app.py` exports `app` or `handler` (it does)

**Where to find logs:**
- **Dashboard:** https://vercel.com/dashboard → Your Project → Functions
- **CLI:** `vercel logs [your-project-url] --follow`
- **Function Logs:** Click on a specific function invocation to see detailed logs

### Testing Locally:

```bash
# Install Vercel CLI
npm install -g vercel

# Run locally with Vercel environment
vercel dev
```

This will simulate the Vercel environment locally.

