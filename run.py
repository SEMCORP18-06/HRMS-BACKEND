import sys
import os

# Add parent directory to path so app.main works
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app.main import app

if __name__ == '__main__':
    app.run(port=8000, debug=True, use_reloader=False)
