"""
Vercel serverless function entry point
Proper Flask handler for Vercel Python runtime
"""
import sys
import traceback
import os

# Print to stderr immediately - this will show in Vercel logs
def emergency_log(message):
    print(f"[EMERGENCY] {message}", file=sys.stderr, flush=True)

emergency_log("=" * 80)
emergency_log("api/index.py: Module loading...")
emergency_log(f"Python version: {sys.version}")
emergency_log(f"Working directory: {os.getcwd()}")
emergency_log(f"Python path: {sys.path[:3]}")

# Wrap everything in try/except to catch import errors
try:
    emergency_log("Importing Flask...")
    from flask import Flask, jsonify
    
    emergency_log("Creating Flask app...")
    app = Flask(__name__)
    
    # Simple routes
    @app.route('/api/health', methods=['GET'])
    def health():
        emergency_log("Health endpoint called")
        return jsonify({
            "status": "ok",
            "message": "API is running",
            "handler": "Flask app"
        })
    
    @app.route('/', methods=['GET'])
    def index():
        emergency_log("Root endpoint called")
        return jsonify({
            "status": "ok",
            "message": "Flask app is running on Vercel",
            "endpoints": ["/api/health"]
        })
    
    @app.route('/test', methods=['GET'])
    def test():
        emergency_log("Test endpoint called")
        return jsonify({
            "status": "ok",
            "message": "Test endpoint working"
        })
    
    # Catch-all route
    @app.route('/<path:path>', methods=['GET', 'POST', 'PUT', 'DELETE', 'PATCH', 'OPTIONS'])
    def catch_all(path):
        emergency_log(f"Catch-all route called with path: {path}")
        return jsonify({
            "status": "ok",
            "path": path,
            "message": "Route handled by Flask"
        })
    
    emergency_log("✓ Flask app created successfully")
    emergency_log(f"✓ Routes registered: {len(list(app.url_map.iter_rules()))}")
    
    # CRITICAL: Export the Flask app as 'handler' for Vercel
    # Vercel's Python runtime looks for a 'handler' variable
    handler = app
    
    emergency_log("✓ Handler exported as Flask app")
    
except Exception as e:
    # If anything fails, create a minimal error handler
    emergency_log(f"CRITICAL ERROR during setup: {e}")
    emergency_log(traceback.format_exc())
    
    try:
        from flask import Flask, jsonify
        
        error_app = Flask(__name__)
        
        @error_app.route('/', defaults={'path': ''})
        @error_app.route('/<path:path>')
        def error_handler(path):
            emergency_log(f"Error handler called with path: {path}")
            return jsonify({
                "error": "Function initialization failed",
                "error_message": str(e),
                "error_type": type(e).__name__,
                "traceback": traceback.format_exc(),
                "path": path
            }), 500
        
        handler = error_app
        app = error_app
        emergency_log("✓ Error handler app created")
        
    except Exception as e2:
        emergency_log(f"CRITICAL: Failed to create error handler: {e2}")
        emergency_log(traceback.format_exc())
        # Last resort: raise to see error in logs
        raise

emergency_log("=" * 80)
emergency_log("Module initialization complete")
emergency_log("=" * 80)
