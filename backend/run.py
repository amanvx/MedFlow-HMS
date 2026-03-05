import os
import sys

# Add the backend directory to the path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app import create_app

# Create the application
app = create_app(os.getenv("FLASK_ENV", "development"))

if __name__ == "__main__":
    print("=" * 60)
    print("Hospital Management System - Backend Server")
    print("=" * 60)
    print(f"Environment: {os.getenv('FLASK_ENV', 'development')}")
    print(f"Database: SQLite")
    print(f"API Base URL: http://localhost:5000/api")
    print("=" * 60)
    print("\nStarting server...\n")

    app.run(host="0.0.0.0", port=5000, debug=True, use_reloader=True)

