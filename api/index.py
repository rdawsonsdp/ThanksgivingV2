"""
Vercel serverless function entry point
Minimal Flask app for testing
"""
import sys
import traceback
import os

# Print to stderr immediately
def emergency_log(message):
    print(f"[EMERGENCY] {message}", file=sys.stderr, flush=True)

emergency_log("=" * 80)
emergency_log("api/index.py: Starting...")
emergency_log(f"Python version: {sys.version}")
emergency_log(f"Working directory: {os.getcwd()}")
emergency_log(f"Python path: {sys.path[:3]}")

try:
    from flask import Flask, jsonify
    
    # Create minimal Flask app
    app = Flask(__name__)
    
    @app.route('/', defaults={'path': ''})
    @app.route('/<path:path>')
    def handler(path):
        emergency_log(f"Handler called with path: {path}")
        if path == 'api/health' or path == 'health':
            return jsonify({
                "status": "ok",
                "message": "API is running",
                "path": path
            })
        return jsonify({
            "status": "ok",
            "message": "Flask app is running on Vercel",
            "path": path,
            "endpoints": ["/api/health"]
        })
    
    # Export for Vercel
    handler = app
    
    emergency_log("✓ Flask app created and handler exported")
    
except Exception as e:
    emergency_log(f"CRITICAL ERROR: {e}")
    emergency_log(traceback.format_exc())
    
    # Create error handler
    from flask import Flask, jsonify
    error_app = Flask(__name__)
    
    @error_app.route('/', defaults={'path': ''})
    @error_app.route('/<path:path>')
    def error_handler(path):
        return jsonify({
            "error": str(e),
            "traceback": traceback.format_exc(),
            "path": path
        }), 500
    
    handler = error_app
    app = error_app
