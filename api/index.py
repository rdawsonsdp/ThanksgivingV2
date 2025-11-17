"""
Vercel serverless function entry point
Imports the Flask app from the parent directory
"""
import sys
import os
import traceback

# Store error info globally so error handler can access it
_import_error = None
_parent_dir = None

try:
    # Add parent directory to path to import app
    _parent_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    sys.path.insert(0, _parent_dir)
    
    # Change to parent directory so relative imports work
    os.chdir(_parent_dir)
    
    # Import Flask app
    from app import app
    
    # Export handler for Vercel - Vercel expects 'handler' or 'app'
    handler = app
    
except Exception as e:
    # Store error info
    _import_error = {
        "message": str(e),
        "type": type(e).__name__,
        "traceback": traceback.format_exc()
    }
    
    # Create error handler Flask app
    from flask import Flask, jsonify
    
    error_app = Flask(__name__)
    
    @error_app.route('/', defaults={'path': ''})
    @error_app.route('/<path:path>')
    def error_handler(path):
        error_info = _import_error or {"message": "Unknown error", "type": "Unknown", "traceback": ""}
        return jsonify({
            "error": f"Failed to load Flask app: {error_info['message']}",
            "type": error_info['type'],
            "traceback": error_info['traceback'],
            "path": path,
            "parent_dir": _parent_dir or 'unknown',
            "cwd": os.getcwd(),
            "sys_path": sys.path[:5]  # First 5 entries
        }), 500
    
    handler = error_app
    app = error_app

