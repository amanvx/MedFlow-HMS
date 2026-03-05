import re
from datetime import datetime


class Validators:
    @staticmethod
    def validate_email(email):
        
        if not email:
            return False, "Email is required"
        
        pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        if not re.match(pattern, email):
            return False, "Invalid email format"
        
        return True, None
    
    @staticmethod
    def validate_password(password):
        if not password:
            return False, "Password is required"
        
        if len(password) < 6:
            return False, "Password must be at least 6 characters"
        
        return True, None
    
    @staticmethod
    def validate_phone(phone):
        
        if not phone:
            return True, None  
        
        cleaned = re.sub(r'[\s\-\(\)]', '', phone)
        
        if not cleaned.isdigit() or len(cleaned) < 10:
            return False, "Invalid phone number format"
        
        return True, None
    
    @staticmethod
    def validate_date(date_str, field_name="Date"):
        
        if not date_str:
            return False, f"{field_name} is required"
        
        try:
            datetime.strptime(date_str, '%Y-%m-%d')
            return True, None
        except ValueError:
            return False, f"{field_name} must be in YYYY-MM-DD format"
    
    @staticmethod
    def validate_datetime(datetime_str, field_name="DateTime"):
        
        if not datetime_str:
            return False, f"{field_name} is required"
        
        try:
            datetime.fromisoformat(datetime_str.replace('Z', '+00:00'))
            return True, None
        except ValueError:
            return False, f"{field_name} must be in ISO 8601 format"
    
    @staticmethod
    def validate_required_fields(data, required_fields):
        
        missing = [field for field in required_fields if field not in data or not data[field]]
        
        if missing:
            return False, f"Missing required fields: {', '.join(missing)}"
        
        return True, None
    
    @staticmethod
    def validate_choice(value, choices, field_name="Value"):
        
        if value not in choices:
            return False, f"{field_name} must be one of: {', '.join(choices)}"
        
        return True, None
    
    @staticmethod
    def validate_appointment_data(data):
        required = ['doctor_id', 'appointment_dt']
        is_valid, error = Validators.validate_required_fields(data, required)
        if not is_valid:
            return False, error
        
        is_valid, error = Validators.validate_datetime(data['appointment_dt'], "Appointment datetime")
        if not is_valid:
            return False, error
        
        try:
            apt_dt = datetime.fromisoformat(data['appointment_dt'].replace('Z', '+00:00'))
            if apt_dt <= datetime.now():
                return False, "Appointment must be in the future"
        except:
            return False, "Invalid appointment datetime"
        
        return True, None
    
    @staticmethod
    def validate_doctor_data(data):
        
        required = ['full_name', 'email', 'password']
        is_valid, error = Validators.validate_required_fields(data, required)
        if not is_valid:
            return False, error
        
        # Validate email
        is_valid, error = Validators.validate_email(data['email'])
        if not is_valid:
            return False, error
        
        # Validate password
        is_valid, error = Validators.validate_password(data['password'])
        if not is_valid:
            return False, error
        
        return True, None
    
    @staticmethod
    def validate_patient_data(data):
        
        required = ['full_name', 'email', 'password']
        is_valid, error = Validators.validate_required_fields(data, required)
        if not is_valid:
            return False, error
        
        # Validate email
        is_valid, error = Validators.validate_email(data['email'])
        if not is_valid:
            return False, error
        
        # Validate password
        is_valid, error = Validators.validate_password(data['password'])
        if not is_valid:
            return False, error
        
        # Validate phone if present
        if 'contact' in data:
            is_valid, error = Validators.validate_phone(data['contact'])
            if not is_valid:
                return False, error
        
        return True, None

