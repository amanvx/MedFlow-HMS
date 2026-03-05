from flask import Flask, send_from_directory
from flask_cors import CORS
import os

DIST_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "dist")

app = Flask(__name__, static_folder=DIST_DIR)
CORS(app)


@app.route("/")
def index():
    return send_from_directory(DIST_DIR, "index.html")


@app.route("/<path:path>")
def serve_file(path):
    full_path = os.path.join(DIST_DIR, path)
    if os.path.exists(full_path):
        return send_from_directory(DIST_DIR, path)
    return send_from_directory(DIST_DIR, "index.html")


if __name__ == "__main__":
    if not os.path.isdir(DIST_DIR):
        print("ERROR: 'dist/' folder not found. Run 'npm run build' first.")
        exit(1)
    print("Starting Frontend Server on http://localhost:8080")
    app.run(host="0.0.0.0", port=8080, debug=False)
