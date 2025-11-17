"""
Vercel serverless function entry point
Imports the Flask app from the parent directory
"""
import sys
import os

# Add parent directory to path to import app
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import app

# Export handler for Vercel
handler = app

