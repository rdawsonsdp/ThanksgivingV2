"""
Vercel serverless function entry point
Imports the Flask app from the parent directory
"""
import sys
import os

# Add parent directory to path to import app
parent_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, parent_dir)

# Change to parent directory so relative imports work
os.chdir(parent_dir)

from app import app

# Export handler for Vercel - Vercel expects 'handler' or 'app'
handler = app
app = app  # Also export as 'app' for compatibility

