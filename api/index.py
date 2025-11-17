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

# Initialize Flask app first for error handling
from flask import Flask, jsonify
error_app = Flask(__name__)

def create_error_handler(error_msg, error_type, error_tb, parent_dir_val):
    """Create an error handler Flask app"""
    @error_app.route('/', defaults={'path': ''})
    @error_app.route('/<path:path>')
    def error_handler(path):
        return jsonify({
            "error": f"Failed to load Flask app: {error_msg}",
            "type": error_type,
            "traceback": error_tb,
            "path": path,
            "parent_dir": parent_dir_val or 'unknown',
            "cwd": os.getcwd(),
            "sys_path": list(sys.path[:5])  # First 5 entries
        }), 500
    return error_app

try:
    # Add parent directory to path to import app
    _parent_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    sys.path.insert(0, _parent_dir)
    
    # Change to parent directory so relative imports work
    os.chdir(_parent_dir)
    
    # Import Flask app
    from app import app
    
    # Add a simple test route to verify Flask is working
    @app.route('/test-vercel', methods=['GET'])
    def test_vercel():
        return jsonify({
            "status": "ok",
            "message": "Flask app is working",
            "cwd": os.getcwd(),
            "parent_dir": _parent_dir
        })
    
    # Export handler for Vercel - Vercel expects 'handler' or 'app'
    handler = app
    
except Exception as e:
    # Store error info
    error_msg = str(e)
    error_type = type(e).__name__
    error_tb = traceback.format_exc()
    
    # Create error handler
    create_error_handler(error_msg, error_type, error_tb, _parent_dir)
    
    handler = error_app
    app = error_app

