"""
Minimal test function to verify Vercel Python works
"""
from flask import Flask, jsonify

app = Flask(__name__)

@app.route('/', defaults={'path': ''})
@app.route('/<path:path>')
def handler(path):
    return jsonify({
        "status": "ok",
        "message": "Test function working",
        "path": path
    })

# Export for Vercel
handler = app

