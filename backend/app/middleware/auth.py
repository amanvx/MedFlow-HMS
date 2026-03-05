from functools import wraps
from flask import request, jsonify
from flask_jwt_extended import verify_jwt_in_request, get_jwt_identity, get_jwt
from app.models import User


def jwt_required_custom(fn):
    @wraps(fn)
    def wrapper(*args, **kwargs):
        try:
            verify_jwt_in_request()
            return fn(*args, **kwargs)
        except Exception as e:
            return jsonify({
                "error": "Authentication required",
                "message": str(e)
            }), 401
    
    return wrapper


def get_current_user_obj():
    try:
        verify_jwt_in_request()
        user_id = get_jwt_identity()
        return User.query.get(user_id)
    except:
        return None


def check_user_active():
    user = get_current_user_obj()
    if not user or not user.is_active:
        return False
    return True


class AuthMiddleware:    
    @staticmethod
    def verify_token():
        
        try:
            verify_jwt_in_request()
            return True
        except:
            return False
    
    @staticmethod
    def get_user_id():
        
        try:
            return get_jwt_identity()
        except:
            return None
    
    @staticmethod
    def get_user_role():
        
        try:
            claims = get_jwt()
            return claims.get('role')
        except:
            return None
    
    @staticmethod
    def has_role(required_role):
        
        try:
            user_role = AuthMiddleware.get_user_role()
            return user_role == required_role
        except:
            return False
    
    @staticmethod
    def is_admin():
        
        return AuthMiddleware.has_role('admin')
    
    @staticmethod
    def is_doctor():
        
        return AuthMiddleware.has_role('doctor')
    
    @staticmethod
    def is_patient():
        
        return AuthMiddleware.has_role('patient')

