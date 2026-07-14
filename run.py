import sys
import os
import traceback

# Add parent directory to path so app.main works
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

try:
    from app.main import app
except Exception as e:
    from flask import Flask, jsonify
    app = Flask(__name__)
    
    @app.route("/<path:path>", methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"])
    def error_fallback(path):
        return jsonify({
            "error": "Failed to import Flask application",
            "detail": str(e),
            "traceback": traceback.format_exc()
        }), 500
        
    @app.route("/", methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"])
    def error_fallback_root():
        return jsonify({
            "error": "Failed to import Flask application",
            "detail": str(e),
            "traceback": traceback.format_exc()
        }), 500

if __name__ == '__main__':
    app.run(port=8000, debug=True, use_reloader=False)
