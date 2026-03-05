from flask import Flask, jsonify
from flask_jwt_extended import JWTManager
from flask_cors import CORS
from app.models import db, User, Department
from config import config
import os
import click

jwt = JWTManager()


def create_app(config_name="default"):
    
    app = Flask(__name__)
    app.config.from_object(config[config_name])

    db.init_app(app)
    jwt.init_app(app)

    @jwt.expired_token_loader
    def expired_token_callback(jwt_header, jwt_payload):
        return jsonify({"error": "Token has expired"}), 401

    @jwt.invalid_token_loader
    def invalid_token_callback(error):
        return jsonify({"error": "Invalid token"}), 422

    @jwt.unauthorized_loader
    def missing_token_callback(error):
        return jsonify({"error": "Authorization token is missing"}), 401

    CORS(
        app,
        resources={
            r"/api/*": {
                "origins": ["http://localhost:8080", "http://127.0.0.1:8080"],
                "methods": ["GET", "POST", "PUT", "DELETE", "PATCH", "OPTIONS"],
                "allow_headers": ["Authorization", "Content-Type"],
            }
        },
    )

    from app.middleware.error_handlers import register_error_handlers
    register_error_handlers(app)

    os.makedirs(app.config["UPLOAD_FOLDER"], exist_ok=True)

    @app.cli.command("init-db")
    def init_db_command():
        
        initialize_database(app)
        click.echo("Database initialized!")

    with app.app_context():
        db.create_all()
        initialize_database(app)

    from .routes import auth, admin, doctor, patient, uploads

    app.register_blueprint(auth, url_prefix="/api/auth")
    app.register_blueprint(admin, url_prefix="/api/admin")
    app.register_blueprint(doctor, url_prefix="/api/doctor")
    app.register_blueprint(patient, url_prefix="/api/patient")
    app.register_blueprint(uploads, url_prefix="/api")

    @app.route("/api/health")
    def health_check():
        return {"status": "healthy", "message": "HMS API is running"}, 200

    return app


def initialize_database(app):
    
    admin_email = app.config["ADMIN_EMAIL"]
    admin = User.query.filter_by(email=admin_email).first()

    if not admin:
        admin = User()
        admin.email = admin_email
        admin.role = "admin"
        admin.full_name = app.config["ADMIN_NAME"]
        admin.is_active = True
        admin.set_password(app.config["ADMIN_PASSWORD"])

        db.session.add(admin)
        db.session.commit()

        print(f"Admin user created successfully!")
        print(f"  Email: {admin_email}")
        print(f"  Password: {app.config['ADMIN_PASSWORD']}")
        print("  Please change the default password after first login!")

    if Department.query.count() == 0:
        default_departments_data = [
            ("General Medicine", "General health checkups and consultations"),
            ("Cardiology", "Heart and cardiovascular system"),
            ("Neurology", "Brain and nervous system"),
            ("Pediatrics", "Children and adolescent health"),
            ("Orthopedics", "Bones, joints, and muscles"),
            ("Dermatology", "Skin conditions"),
            ("Ophthalmology", "Eye care and vision"),
            ("Gynecology", "Women reproductive health"),
        ]

        for name, description in default_departments_data:
            dept = Department()
            dept.name = name
            dept.description = description
            db.session.add(dept)

        db.session.commit()
        print(f"Created {len(default_departments_data)} default departments")

