# Vercel Environment Variables

## Required Environment Variables

### 1. GOOGLE_CREDENTIALS_BASE64 (Required)
**Description**: Base64-encoded Google Service Account credentials JSON file

**How to get it**:
```bash
cat long-canto-360620-6858c5a01c13.json | base64
```

**Value**: Paste the entire base64-encoded string

**Purpose**: Authenticates with Google Sheets API to read data

---

## Optional Environment Variables (Currently Hardcoded)

These are currently hardcoded in `api.py` but could be made configurable:

### 2. GOOGLE_SPREADSHEET_ID (Optional)
**Current Value**: `1YAHO5rHhFVEReyAuxa7r2SDnoH7BnDfsmSEZ1LyjB8A`

**Purpose**: Google Sheets spreadsheet ID

**Note**: Currently hardcoded in `api.py` line 26

---

### 3. CUSTOMER_ORDERS_SHEET_NAME (Optional)
**Current Value**: `Customer Orders`

**Purpose**: Name of the customer orders sheet

**Note**: Currently hardcoded in `api.py` line 27

---

### 4. BAKERY_PRODUCTS_SHEET_NAME (Optional)
**Current Value**: `Bakery Products Ordered ` (note the trailing space)

**Purpose**: Name of the bakery products sheet

**Note**: Currently hardcoded in `api.py` line 28

---

## How to Set Environment Variables in Vercel

### Via Vercel Dashboard:
1. Go to your project: https://vercel.com/dashboard
2. Select your project: `thanksgiving`
3. Go to **Settings** → **Environment Variables**
4. Click **Add New**
5. Enter the variable name and value
6. Select environments (Production, Preview, Development)
7. Click **Save**

### Via Vercel CLI:
```bash
# Add environment variable
vercel env add GOOGLE_CREDENTIALS_BASE64

# List all environment variables
vercel env ls

# Pull environment variables to local .env file
vercel env pull .env.local
```

---

## Minimum Required Setup

**For the application to work, you MUST set:**
- `GOOGLE_CREDENTIALS_BASE64` - The base64-encoded credentials JSON

**All other values are currently hardcoded and work as-is.**

---

## Important Notes

⚠️ **Security**: Never commit the credentials file or base64 value to git. Always use environment variables for sensitive data.

⚠️ **File Size**: The credentials JSON file is small enough to be stored as an environment variable. If you encounter size limits, contact Vercel support.

⚠️ **After Adding Variables**: You may need to redeploy for environment variables to take effect:
```bash
vercel --prod
```

