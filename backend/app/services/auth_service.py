from flask_jwt_extended import create_access_token
from app.models import db, User, Doctor, Patient


class AuthService:    
    @staticmethod
    def login(email, password):
        
        user = User.query.filter_by(email=email).first()
        
        if not user or not user.check_password(password):
            raise ValueError("Invalid email or password")
        
        if not user.is_active:
            raise ValueError("Account is inactive")
        
        # Generate JWT token
        access_token = create_access_token(
            identity=user.id,
            additional_claims={"role": user.role}
        )
        
        return {
            "user": user.to_dict(),
            "access_token": access_token
        }
    
    @staticmethod
    def register_patient(data):
        
        # Check if email exists
        if User.query.filter_by(email=data['email']).first():
            raise ValueError("Email already registered")
        
        # Create user
        user = User(
            email=data['email'],
            full_name=data.get('full_name'),
            role='patient'
        )
        user.set_password(data['password'])
        
        db.session.add(user)
        db.session.flush()  # Get user.id
        
        # Create patient profile
        patient = Patient(
            user_id=user.id,
            contact=data.get('contact'),
            address=data.get('address')
        )
        
        db.session.add(patient)
        db.session.commit()
        
        # Generate token
        access_token = create_access_token(
            identity=user.id,
            additional_claims={"role": user.role}
        )
        
        return {
            "user": user.to_dict(),
            "access_token": access_token
        }
    
    @staticmethod
    def get_user_profile(user_id):
        
        user = User.query.get(user_id)
        if not user:
            raise ValueError("User not found")
        
        profile = user.to_dict()
        
        # Add role-specific data
        if user.role == 'doctor' and user.doctor_profile:
            profile['doctor'] = user.doctor_profile.to_dict()
        elif user.role == 'patient' and user.patient_profile:
            profile['patient'] = user.patient_profile.to_dict()
        
        return profile

