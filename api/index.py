"""
Vercel serverless function entry point
Imports the Flask app from the parent directory
"""
import sys
import os
import traceback

try:
    # Add parent directory to path to import app
    parent_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    sys.path.insert(0, parent_dir)
    
    # Change to parent directory so relative imports work
    os.chdir(parent_dir)
    
    from app import app
    
    # Export handler for Vercel - Vercel expects 'handler' or 'app'
    handler = app
    
except Exception as e:
    # If import fails, create a minimal error handler with detailed error info
    from flask import Flask, jsonify
    
    error_app = Flask(__name__)
    error_message = str(e)
    error_type = type(e).__name__
    error_traceback = traceback.format_exc()
    
    @error_app.route('/', defaults={'path': ''})
    @error_app.route('/<path:path>')
    def error_handler(path):
        return jsonify({
            "error": f"Failed to load Flask app: {error_message}",
            "type": error_type,
            "traceback": error_traceback,
            "path": path,
            "parent_dir": parent_dir if 'parent_dir' in locals() else 'unknown',
            "cwd": os.getcwd(),
            "sys_path": sys.path[:3]  # First 3 entries
        }), 500
    
    handler = error_app
    app = error_app

