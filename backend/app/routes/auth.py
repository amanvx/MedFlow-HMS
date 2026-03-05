from flask import Blueprint, request, jsonify
from flask_jwt_extended import (
    create_access_token,
    jwt_required,
    get_jwt_identity,
    create_refresh_token,
)
from functools import wraps
from app.models import db, User, Patient, Doctor
from datetime import datetime
import re

bp = Blueprint("auth", __name__)


def admin_required(fn):

    @wraps(fn)
    @jwt_required()
    def wrapper(*args, **kwargs):
        current_user_id = int(get_jwt_identity())
        user = User.query.get(current_user_id)
        if not user or user.role != "admin":
            return jsonify({"error": "Admin access required"}), 403
        return fn(*args, **kwargs)

    return wrapper


def doctor_required(fn):

    @wraps(fn)
    @jwt_required()
    def wrapper(*args, **kwargs):
        current_user_id = int(get_jwt_identity())
        user = User.query.get(current_user_id)
        if not user or user.role != "doctor":
            return jsonify({"error": "Doctor access required"}), 403
        return fn(*args, **kwargs)

    return wrapper


def patient_required(fn):

    @wraps(fn)
    @jwt_required()
    def wrapper(*args, **kwargs):
        current_user_id = int(get_jwt_identity())
        user = User.query.get(current_user_id)
        if not user or user.role != "patient":
            return jsonify({"error": "Patient access required"}), 403
        return fn(*args, **kwargs)

    return wrapper


def validate_email(email):
    pattern = r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$"
    return re.match(pattern, email) is not None


def validate_password(password):
    if len(password) < 6:
        return False, "Password must be at least 6 characters long"
    return True, None


@bp.route("/register", methods=["POST"])
def register():
    data = request.get_json()

    # Validation
    if not data:
        return jsonify({"error": "No data provided"}), 400

    email = data.get("email", "").strip().lower()
    password = data.get("password", "")
    full_name = data.get("full_name", "").strip()
    contact = data.get("contact", "").strip()
    address = data.get("address", "").strip()

    # Required fields
    if not email or not password or not full_name:
        return jsonify({"error": "Email, password, and full name are required"}), 400

    # Email validation
    if not validate_email(email):
        return jsonify({"error": "Invalid email format"}), 400

    # Password validation
    valid, msg = validate_password(password)
    if not valid:
        return jsonify({"error": msg}), 400

    # Check if email exists
    if User.query.filter_by(email=email).first():
        return jsonify({"error": "Email already registered"}), 409

    try:
        # Create user
        user = User()
        user.email = email
        user.role = "patient"
        user.full_name = full_name
        user.set_password(password)

        db.session.add(user)
        db.session.flush()  # Get user.id without committing

        # Create patient profile
        patient = Patient()
        patient.user_id = user.id
        patient.contact = contact
        patient.address = address

        db.session.add(patient)
        db.session.commit()

        # Generate tokens
        access_token = create_access_token(identity=str(user.id))
        refresh_token = create_refresh_token(identity=str(user.id))

        return jsonify(
            {
                "message": "Registration successful",
                "user": user.to_dict(),
                "access_token": access_token,
                "refresh_token": refresh_token,
            }
        ), 201

    except Exception as e:
        db.session.rollback()
        return jsonify({"error": f"Registration failed: {str(e)}"}), 500


@bp.route("/login", methods=["POST"])
def login():
    data = request.get_json()

    if not data:
        return jsonify({"error": "No data provided"}), 400

    email = data.get("email", "").strip().lower()
    password = data.get("password", "")

    if not email or not password:
        return jsonify({"error": "Email and password are required"}), 400

    # Find user
    user = User.query.filter_by(email=email).first()

    if not user:
        return jsonify({"error": "Invalid email or password"}), 401

    if not user.is_active:
        return jsonify({"error": "Account is deactivated. Contact admin."}), 403

    if not user.check_password(password):
        return jsonify({"error": "Invalid email or password"}), 401

    # Generate tokens
    access_token = create_access_token(identity=str(user.id))
    refresh_token = create_refresh_token(identity=str(user.id))

    # Get profile info based on role
    profile = None
    if user.role == "patient" and user.patient_profile:
        profile = user.patient_profile.to_dict()
    elif user.role == "doctor" and user.doctor_profile:
        profile = user.doctor_profile.to_dict()

    return jsonify(
        {
            "message": "Login successful",
            "user": user.to_dict(),
            "profile": profile,
            "access_token": access_token,
            "refresh_token": refresh_token,
        }
    ), 200


@bp.route("/refresh", methods=["POST"])
@jwt_required(refresh=True)
def refresh():
    current_user_id = int(get_jwt_identity())
    user = User.query.get(current_user_id)

    if not user or not user.is_active:
        return jsonify({"error": "User not found or inactive"}), 401

    new_token = create_access_token(identity=str(current_user_id))
    return jsonify({"access_token": new_token}), 200


@bp.route("/me", methods=["GET"])
@jwt_required()
def get_current_user():
    current_user_id = int(get_jwt_identity())
    user = User.query.get(current_user_id)

    if not user:
        return jsonify({"error": "User not found"}), 404

    profile = None
    if user.role == "patient" and user.patient_profile:
        profile = user.patient_profile.to_dict()
    elif user.role == "doctor" and user.doctor_profile:
        profile = user.doctor_profile.to_dict()

    return jsonify({"user": user.to_dict(), "profile": profile}), 200


@bp.route("/me", methods=["PUT"])
@jwt_required()
def update_profile():
    current_user_id = int(get_jwt_identity())
    user = User.query.get(current_user_id)

    if not user:
        return jsonify({"error": "User not found"}), 404

    data = request.get_json()
    if not data:
        return jsonify({"error": "No data provided"}), 400

    try:
        # Update user fields
        if "full_name" in data:
            user.full_name = data["full_name"].strip()

        # Update profile fields based on role
        if user.role == "patient" and user.patient_profile:
            if "contact" in data:
                user.patient_profile.contact = data["contact"].strip()
            if "address" in data:
                user.patient_profile.address = data["address"].strip()
            if "blood_group" in data:
                user.patient_profile.blood_group = data["blood_group"].strip()

        elif user.role == "doctor" and user.doctor_profile:
            if "specialization" in data:
                user.doctor_profile.specialization = data["specialization"].strip()

        db.session.commit()

        profile = None
        if user.role == "patient" and user.patient_profile:
            profile = user.patient_profile.to_dict()
        elif user.role == "doctor" and user.doctor_profile:
            profile = user.doctor_profile.to_dict()

        return jsonify(
            {
                "message": "Profile updated successfully",
                "user": user.to_dict(),
                "profile": profile,
            }
        ), 200

    except Exception as e:
        db.session.rollback()
        return jsonify({"error": f"Update failed: {str(e)}"}), 500


@bp.route("/change-password", methods=["POST"])
@jwt_required()
def change_password():
    current_user_id = int(get_jwt_identity())
    user = User.query.get(current_user_id)

    if not user:
        return jsonify({"error": "User not found"}), 404

    data = request.get_json()
    current_password = data.get("current_password", "")
    new_password = data.get("new_password", "")

    if not current_password or not new_password:
        return jsonify({"error": "Current password and new password are required"}), 400

    if not user.check_password(current_password):
        return jsonify({"error": "Current password is incorrect"}), 401

    valid, msg = validate_password(new_password)
    if not valid:
        return jsonify({"error": msg}), 400

    try:
        user.set_password(new_password)
        db.session.commit()
        return jsonify({"message": "Password changed successfully"}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": f"Password change failed: {str(e)}"}), 500

