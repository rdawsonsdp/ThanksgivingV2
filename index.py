"""
Vercel entry point - root level
Imports the Flask app from app.py
"""
from app import app

# Export handler for Vercel
handler = app

