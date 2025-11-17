"""
Flask API for Sales Dashboard
Deployable on Vercel as serverless functions
"""

import sys
import traceback
import os

# Print to stderr immediately (before logging is set up) to catch early errors
def emergency_log(message):
    """Log to stderr immediately, even if logging isn't set up."""
    print(f"[EMERGENCY] {message}", file=sys.stderr, flush=True)

try:
    emergency_log("=" * 80)
    emergency_log("Starting Flask application initialization...")
    emergency_log(f"Python version: {sys.version}")
    emergency_log(f"Working directory: {os.getcwd()}")
    emergency_log(f"Python path: {sys.path[:5]}")
    
    import logging
    
    # Configure verbose logging
    logging.basicConfig(
        level=logging.DEBUG,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        stream=sys.stderr
    )
    logger = logging.getLogger(__name__)
    logger.setLevel(logging.DEBUG)
    
    # Log startup
    logger.info("=" * 80)
    logger.info("Starting Flask application...")
    logger.info(f"Python version: {sys.version}")
    logger.info(f"Working directory: {os.getcwd()}")
    logger.info(f"Python path: {sys.path[:5]}")  # First 5 entries
    
except Exception as e:
    emergency_log(f"CRITICAL: Failed to set up logging: {e}")
    emergency_log(traceback.format_exc())
    raise

try:
    from flask import Flask, jsonify, request
    logger.info("✓ Flask imported successfully")
except Exception as e:
    error_msg = f"✗ Failed to import Flask: {e}"
    emergency_log(error_msg)
    emergency_log(traceback.format_exc())
    try:
        logger.error(error_msg)
        logger.error(traceback.format_exc())
    except:
        pass
    raise

try:
    from flask_cors import CORS
    logger.info("✓ flask_cors imported successfully")
except Exception as e:
    error_msg = f"✗ Failed to import flask_cors: {e}"
    emergency_log(error_msg)
    emergency_log(traceback.format_exc())
    try:
        logger.error(error_msg)
        logger.error(traceback.format_exc())
    except:
        pass
    raise

# Create Flask app
try:
    app = Flask(__name__)
    CORS(app)  # Enable CORS for frontend
    logger.info("✓ Flask app created")
except Exception as e:
    error_msg = f"✗ Failed to create Flask app: {e}"
    emergency_log(error_msg)
    emergency_log(traceback.format_exc())
    raise

# ============================================================================
# SIMPLE ROUTES - Just to test serverless functionality
# ============================================================================

@app.route('/api/health', methods=['GET'])
def health():
    """Health check endpoint."""
    logger.info("Health check endpoint called")
    try:
        response = {
            "status": "ok",
            "message": "API is running",
            "timestamp": __import__('datetime').datetime.now().isoformat(),
            "cwd": os.getcwd(),
            "python_version": sys.version,
        }
        logger.info(f"Health check response: {response}")
        return jsonify(response)
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        logger.error(traceback.format_exc())
        return jsonify({
            "status": "error",
            "error": str(e),
            "traceback": traceback.format_exc()
        }), 500

@app.route('/', methods=['GET'])
def index():
    """Serve a simple response."""
    logger.info("Root route (/) called")
    return jsonify({
        "status": "ok",
        "message": "Flask app is running on Vercel",
        "endpoints": {
            "/api/health": "Health check endpoint"
        }
    })

@app.route('/test', methods=['GET'])
def test():
    """Test endpoint."""
    logger.info("Test endpoint called")
    return jsonify({
        "status": "ok",
        "message": "Test endpoint working",
        "routes": [str(rule) for rule in app.url_map.iter_rules()]
    })

# ============================================================================
# COMMENTED OUT - Complex functionality (Google Sheets, data loading, etc.)
# ============================================================================

# """
# import pandas as pd
# import gspread
# from google.oauth2.service_account import Credentials
# from datetime import datetime
# import io
# from reportlab.lib import colors
# from reportlab.lib.pagesizes import letter
# from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
# from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
# from reportlab.lib.units import inch
# from openpyxl import Workbook
# from openpyxl.styles import Font, PatternFill, Alignment

# # Google Sheets configuration
# SPREADSHEET_ID = "1YAHO5rHhFVEReyAuxa7r2SDnoH7BnDfsmSEZ1LyjB8A"
# CUSTOMER_ORDERS_SHEET_NAME = "Customer Orders"
# BAKERY_PRODUCTS_SHEET_NAME = "Bakery Products Ordered "

# SCOPES = [
#     "https://www.googleapis.com/auth/spreadsheets.readonly",
#     "https://www.googleapis.com/auth/drive.readonly"
# ]

# def get_credentials():
#     # ... credential loading code ...

# def load_data():
#     # ... data loading code ...

# @app.route('/api/data', methods=['GET'])
# def get_data():
#     # ... data endpoint ...

# @app.route('/api/summary', methods=['GET'])
# def get_summary():
#     # ... summary endpoint ...

# # ... all other complex routes ...
# """

# ============================================================================
# EXPORT FOR VERCEL
# ============================================================================

# Export handler for Vercel
# Vercel expects the Flask app to be accessible as 'app' or 'handler'
try:
    handler = app
    __all__ = ['app', 'handler']
    emergency_log("✓ Handler exported successfully")
    logger.info("✓ Handler exported successfully")
    
    # Log successful app initialization
    logger.info("=" * 80)
    logger.info("Flask app initialized successfully!")
    logger.info(f"Number of routes: {len(list(app.url_map.iter_rules()))}")
    logger.info("Routes:")
    for rule in app.url_map.iter_rules():
        logger.info(f"  {rule.rule} -> {rule.endpoint}")
    logger.info("=" * 80)
    
except Exception as e:
    error_msg = f"CRITICAL: Failed to export handler: {e}"
    emergency_log(error_msg)
    emergency_log(traceback.format_exc())
    # Create a minimal error app as fallback
    try:
        from flask import Flask, jsonify
        error_app = Flask(__name__)
        @error_app.route('/', defaults={'path': ''})
        @error_app.route('/<path:path>')
        def error_handler(path):
            return jsonify({
                "error": f"Failed to initialize Flask app: {str(e)}",
                "traceback": traceback.format_exc(),
                "path": path
            }), 500
        handler = error_app
        app = error_app
        emergency_log("✓ Error handler app created as fallback")
    except Exception as e2:
        emergency_log(f"CRITICAL: Failed to create error handler: {e2}")
        emergency_log(traceback.format_exc())
        raise

# For local development and traditional hosting (Railway, Render, etc.)
if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5001))
    logger.info(f"Starting Flask development server on port {port}")
    app.run(debug=True, port=port, host='0.0.0.0')
