# Understanding Vercel Python Function Handlers

## 1. The Fix

**Problem**: `FUNCTION_INVOCATION_FAILED` occurs because Vercel's Python runtime couldn't properly invoke your function.

**Solution**: Export the Flask app as `handler` (not just `app`). Vercel's Python runtime specifically looks for a variable named `handler` in your serverless function.

```python
# ✅ CORRECT - Vercel looks for 'handler'
handler = app

# ❌ WRONG - Vercel won't find this
app = Flask(__name__)
# (missing handler export)
```

## 2. Root Cause Analysis

### What Was Happening vs. What Should Happen

**What was happening:**
- Flask app was created correctly
- Routes were defined correctly  
- But Vercel's runtime couldn't find the handler to invoke

**What should happen:**
- Flask app is created
- Routes are defined
- Flask app is exported as `handler` variable
- Vercel runtime finds `handler` and invokes it with incoming requests

### Why This Error Occurred

Vercel's Python runtime uses a specific protocol:
1. It imports your Python file (`api/index.py`)
2. It looks for a `handler` variable (or `app` as fallback for Flask)
3. It wraps your handler in a WSGI adapter
4. It invokes the handler with each HTTP request

If `handler` doesn't exist or isn't a valid WSGI application, the function invocation fails.

### The Misconception

**Misconception**: "Flask apps work automatically on Vercel"
**Reality**: Flask apps need to be explicitly exported as `handler` for Vercel's Python runtime to find and invoke them.

## 3. Understanding the Concept

### Why This Error Exists

Vercel's serverless architecture:
- **Isolation**: Each function runs in its own isolated environment
- **Discovery**: The runtime needs to know what to invoke
- **Protocol**: Uses WSGI (Web Server Gateway Interface) for Python web apps

The `handler` export tells Vercel:
- "This is the entry point for HTTP requests"
- "This object implements the WSGI protocol"
- "Invoke this when a request comes in"

### Mental Model

Think of it like this:
```
HTTP Request → Vercel Runtime → Looks for 'handler' → Invokes handler(request) → Response
```

If `handler` doesn't exist or crashes, you get `FUNCTION_INVOCATION_FAILED`.

### Framework Design

Flask is a WSGI application. Vercel's Python runtime:
1. Detects Python files in `api/` directory
2. Imports the module
3. Looks for `handler` (or `app` for Flask auto-detection)
4. Wraps it in a request adapter
5. Invokes it per request

## 4. Warning Signs

### Red Flags to Watch For

1. **Missing handler export**
   ```python
   app = Flask(__name__)
   # ❌ No handler = app
   ```

2. **Handler points to wrong object**
   ```python
   handler = "not a WSGI app"  # ❌ Wrong type
   ```

3. **Handler crashes on import**
   ```python
   import nonexistent_module  # ❌ Crashes before handler is set
   handler = app
   ```

4. **Handler not callable**
   ```python
   handler = None  # ❌ Not callable
   ```

### Code Smells

- No `handler = app` at module level
- Handler defined inside a function (not at module level)
- Handler depends on runtime state that might not exist
- Import errors that prevent handler from being set

### Similar Mistakes

- Forgetting to export `handler` in other serverless platforms (AWS Lambda, Google Cloud Functions)
- Not understanding WSGI protocol requirements
- Assuming auto-detection will always work

## 5. Alternatives and Trade-offs

### Option 1: Export as `handler` (Recommended)
```python
app = Flask(__name__)
handler = app  # Explicit export
```
**Pros**: Works reliably, clear intent
**Cons**: None

### Option 2: Use Flask auto-detection
```python
app = Flask(__name__)
# Vercel can auto-detect Flask apps
```
**Pros**: Less code
**Cons**: Less reliable, might not work in all cases

### Option 3: Custom WSGI handler function
```python
def handler(request):
    # Custom request handling
    return response
```
**Pros**: More control
**Cons**: More complex, need to handle WSGI protocol manually

### Option 4: Use `api/index.py` with proper structure
```python
# api/index.py
from flask import Flask
app = Flask(__name__)
handler = app
```
**Pros**: Standard Vercel structure, reliable
**Cons**: Requires `api/` directory

## Best Practices

1. **Always export handler explicitly**
   ```python
   handler = app
   ```

2. **Use try/except around imports**
   ```python
   try:
       from flask import Flask
       app = Flask(__name__)
       handler = app
   except Exception as e:
       # Handle error
   ```

3. **Test locally with Vercel CLI**
   ```bash
   vercel dev
   ```

4. **Check logs for import errors**
   - Look for `[EMERGENCY]` messages
   - Check if handler is being set

5. **Keep handler at module level**
   - Not inside a function
   - Not conditional (unless with fallback)

## Summary

The fix is simple: **export your Flask app as `handler`**. The root cause was Vercel's runtime couldn't find the entry point. Understanding WSGI and serverless function protocols helps prevent similar issues in the future.

