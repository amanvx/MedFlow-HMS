from functools import wraps
from flask import request, jsonify
from flask_jwt_extended import get_jwt_identity, verify_jwt_in_request, get_jwt
from app.models import User


def admin_required(fn):  
    @wraps(fn)
    def wrapper(*args, **kwargs):
        verify_jwt_in_request()
        claims = get_jwt()
        
        if claims.get('role') != 'admin':
            return jsonify({"error": "Admin access required"}), 403
        
        return fn(*args, **kwargs)
    
    return wrapper


def doctor_required(fn): 
    @wraps(fn)
    def wrapper(*args, **kwargs):
        verify_jwt_in_request()
        claims = get_jwt()
        
        if claims.get('role') != 'doctor':
            return jsonify({"error": "Doctor access required"}), 403
        
        return fn(*args, **kwargs)
    
    return wrapper


def patient_required(fn):
    @wraps(fn)
    def wrapper(*args, **kwargs):
        verify_jwt_in_request()
        claims = get_jwt()
        
        if claims.get('role') != 'patient':
            return jsonify({"error": "Patient access required"}), 403
        
        return fn(*args, **kwargs)
    
    return wrapper


def role_required(*allowed_roles):
    def decorator(fn):
        @wraps(fn)
        def wrapper(*args, **kwargs):
            verify_jwt_in_request()
            claims = get_jwt()
            user_role = claims.get('role')
            
            if user_role not in allowed_roles:
                return jsonify({
                    "error": f"Access denied. Required roles: {', '.join(allowed_roles)}"
                }), 403
            
            return fn(*args, **kwargs)
        
        return wrapper
    return decorator


def validate_request(*required_fields):
    def decorator(fn):
        @wraps(fn)
        def wrapper(*args, **kwargs):
            data = request.get_json()
            
            if not data:
                return jsonify({"error": "Request body is required"}), 400
            
            missing = [field for field in required_fields if field not in data]
            
            if missing:
                return jsonify({
                    "error": f"Missing required fields: {', '.join(missing)}"
                }), 400
            
            return fn(*args, **kwargs)
        
        return wrapper
    return decorator


def get_current_user():
    try:
        verify_jwt_in_request()
        user_id = get_jwt_identity()
        return User.query.get(user_id)
    except:
        return None

