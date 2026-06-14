"""Entry point — run `python run.py` to start the development server."""
from app import create_app

app = create_app()

if __name__ == "__main__":
    # debug=True gives auto-reload + helpful error pages while developing.
    app.run(host="127.0.0.1", port=5000, debug=True)
