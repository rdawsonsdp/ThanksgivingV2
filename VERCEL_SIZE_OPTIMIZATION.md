# Vercel Size Optimization Guide

## Problem
Vercel has a 250 MB unzipped size limit for serverless functions. The current deployment exceeds this limit due to large Python dependencies, particularly pandas.

## Solutions Applied

### 1. Removed Unused Dependencies ✅
- Removed `matplotlib` (not used in api.py)
- Removed `plotly` (not used in api.py)  
- Removed `streamlit` (not used in api.py)

### 2. Updated .vercelignore ✅
- Excluded unnecessary files from deployment
- Added build artifacts, cache files, and documentation

### 3. Current Dependencies
The following are required and cannot be removed:
- `pandas` - Core data manipulation (large, ~100MB+)
- `numpy` - Pandas dependency (large, ~50MB+)
- `reportlab` - PDF generation (~20MB)
- `openpyxl` - Excel export (~10MB)
- `gspread` - Google Sheets API (~5MB)
- `flask` - Web framework (~5MB)
- `google-auth` - Authentication (~5MB)

**Total estimated size: ~200MB+** (close to limit)

## Alternative Solutions

### Option 1: Use Vercel's Python 3.11 Runtime (Recommended)
Vercel's newer Python runtime may have better optimization. Update `vercel.json`:

```json
{
  "functions": {
    "api.py": {
      "runtime": "python3.11"
    }
  }
}
```

### Option 2: Split into Multiple Functions
Break the API into smaller functions:
- `/api/data` → data.py
- `/api/export/pdf` → pdf_export.py
- `/api/export/xls` → xls_export.py

### Option 3: Use Lighter Alternatives
- Replace pandas with `polars` (faster, smaller) - requires code changes
- Use `csv` module instead of pandas for simple operations
- Consider serverless-optimized libraries

### Option 4: Upgrade Vercel Plan
Vercel Pro plan has higher limits (1GB unzipped)

## Recommended Next Steps

1. **Try deploying with current optimizations** (removed unused deps)
2. **If still too large**, consider Option 1 (Python 3.11 runtime)
3. **If still failing**, consider Option 2 (split functions)

## Current Status
✅ Removed unused dependencies
✅ Optimized .vercelignore
⏳ Ready to test deployment

