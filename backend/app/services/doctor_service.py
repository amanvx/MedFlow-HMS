

from app.models import db, Doctor, User, Department
from datetime import datetime, timedelta
import json


class DoctorService:
    
    @staticmethod
    def get_all_doctors(department_id=None, specialization=None):
        
        query = Doctor.query.join(User).filter(User.is_active == True)
        
        if department_id:
            query = query.filter(Doctor.department_id == department_id)
        
        if specialization:
            query = query.filter(Doctor.specialization.ilike(f"%{specialization}%"))
        
        doctors = query.all()
        return [doctor.to_dict() for doctor in doctors]
    
    @staticmethod
    def get_doctor_by_id(doctor_id):
        
        doctor = Doctor.query.get(doctor_id)
        if not doctor:
            raise ValueError("Doctor not found")
        return doctor.to_dict()
    
    @staticmethod
    def create_doctor(data):
        
        # Check if email exists
        if User.query.filter_by(email=data['email']).first():
            raise ValueError("Email already exists")
        
        # Create user
        user = User(
            email=data['email'],
            full_name=data['full_name'],
            role='doctor'
        )
        user.set_password(data['password'])
        
        db.session.add(user)
        db.session.flush()
        
        # Create doctor profile
        doctor = Doctor(
            user_id=user.id,
            department_id=data.get('department_id'),
            specialization=data.get('specialization'),
            availability=json.dumps(DoctorService._generate_default_availability())
        )
        
        db.session.add(doctor)
        db.session.commit()
        
        return doctor.to_dict()
    
    @staticmethod
    def update_doctor(doctor_id, data):
        
        doctor = Doctor.query.get(doctor_id)
        if not doctor:
            raise ValueError("Doctor not found")
        
        # Update doctor fields
        if 'department_id' in data:
            doctor.department_id = data['department_id']
        if 'specialization' in data:
            doctor.specialization = data['specialization']
        
        # Update user fields
        if 'full_name' in data and doctor.user:
            doctor.user.full_name = data['full_name']
        
        db.session.commit()
        return doctor.to_dict()
    
    @staticmethod
    def delete_doctor(doctor_id):
        
        doctor = Doctor.query.get(doctor_id)
        if not doctor:
            raise ValueError("Doctor not found")
        
        if doctor.user:
            doctor.user.is_active = False
            db.session.commit()
        
        return {"message": "Doctor deactivated successfully"}
    
    @staticmethod
    def update_availability(doctor_id, availability_data):
        
        doctor = Doctor.query.get(doctor_id)
        if not doctor:
            raise ValueError("Doctor not found")
        
        doctor.set_availability(availability_data)
        db.session.commit()
        
        return doctor.to_dict()
    
    @staticmethod
    def get_availability(doctor_id):
        
        doctor = Doctor.query.get(doctor_id)
        if not doctor:
            raise ValueError("Doctor not found")
        
        return doctor.get_availability()
    
    @staticmethod
    def _generate_default_availability():
        
        availability = {}
        today = datetime.now().date()
        
        for i in range(7):
            date = today + timedelta(days=i)
            date_str = date.strftime('%Y-%m-%d')
            
            # Skip weekends
            if date.weekday() < 5:  # Monday = 0, Friday = 4
                availability[date_str] = [
                    "09:00", "10:00", "11:00", "12:00",
                    "14:00", "15:00", "16:00", "17:00"
                ]
        
        return availability

