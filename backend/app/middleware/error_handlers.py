

from flask import jsonify
from werkzeug.exceptions import HTTPException
from sqlalchemy.exc import SQLAlchemyError
from jwt.exceptions import InvalidTokenError


def register_error_handlers(app):
    
    
    @app.errorhandler(400)
    def bad_request(error):
        
        return jsonify({
            "error": "Bad Request",
            "message": str(error)
        }), 400
    
    @app.errorhandler(401)
    def unauthorized(error):
        
        return jsonify({
            "error": "Unauthorized",
            "message": "Authentication required"
        }), 401
    
    @app.errorhandler(403)
    def forbidden(error):
        
        return jsonify({
            "error": "Forbidden",
            "message": "You don't have permission to access this resource"
        }), 403
    
    @app.errorhandler(404)
    def not_found(error):
        
        return jsonify({
            "error": "Not Found",
            "message": "The requested resource was not found"
        }), 404
    
    @app.errorhandler(405)
    def method_not_allowed(error):
        
        return jsonify({
            "error": "Method Not Allowed",
            "message": "The method is not allowed for the requested URL"
        }), 405
    
    @app.errorhandler(500)
    def internal_server_error(error):
        
        app.logger.error(f"Internal server error: {str(error)}")
        return jsonify({
            "error": "Internal Server Error",
            "message": "An unexpected error occurred"
        }), 500
    
    @app.errorhandler(SQLAlchemyError)
    def handle_db_error(error):
        
        app.logger.error(f"Database error: {str(error)}")
        return jsonify({
            "error": "Database Error",
            "message": "A database error occurred"
        }), 500
    
    @app.errorhandler(InvalidTokenError)
    def handle_jwt_error(error):
        
        return jsonify({
            "error": "Invalid Token",
            "message": "The authentication token is invalid or expired"
        }), 401
    
    @app.errorhandler(Exception)
    def handle_unexpected_error(error):
        
        app.logger.error(f"Unexpected error: {str(error)}", exc_info=True)
        
        # In production, don't expose error details
        if app.config.get('DEBUG'):
            message = str(error)
        else:
            message = "An unexpected error occurred"
        
        return jsonify({
            "error": "Server Error",
            "message": message
        }), 500
    
    @app.errorhandler(ValueError)
    def handle_value_error(error):
        
        return jsonify({
            "error": "Validation Error",
            "message": str(error)
        }), 400


class ErrorResponse:
    
    
    @staticmethod
    def bad_request(message="Bad request"):
        return jsonify({"error": message}), 400
    
    @staticmethod
    def unauthorized(message="Authentication required"):
        return jsonify({"error": message}), 401
    
    @staticmethod
    def forbidden(message="Access denied"):
        return jsonify({"error": message}), 403
    
    @staticmethod
    def not_found(message="Resource not found"):
        return jsonify({"error": message}), 404
    
    @staticmethod
    def internal_error(message="Internal server error"):
        return jsonify({"error": message}), 500
    
    @staticmethod
    def custom_error(message, status_code=400):
        return jsonify({"error": message}), status_code

