from app.models import db, Patient, User

class PatientService:
    
    @staticmethod
    def get_all_patients():
        
        patients = Patient.query.join(User).filter(User.is_active == True).all()
        return [patient.to_dict() for patient in patients]
    
    @staticmethod
    def get_patient_by_id(patient_id):
        
        patient = Patient.query.get(patient_id)
        if not patient:
            raise ValueError("Patient not found")
        return patient.to_dict()
    
    @staticmethod
    def get_patient_by_user_id(user_id):
        
        patient = Patient.query.filter_by(user_id=user_id).first()
        if not patient:
            raise ValueError("Patient profile not found")
        return patient.to_dict()
    
    @staticmethod
    def update_patient(patient_id, data):
        
        patient = Patient.query.get(patient_id)
        if not patient:
            raise ValueError("Patient not found")
        
        # Update patient fields
        if 'contact' in data:
            patient.contact = data['contact']
        if 'address' in data:
            patient.address = data['address']
        if 'date_of_birth' in data:
            patient.date_of_birth = data['date_of_birth']
        if 'blood_group' in data:
            patient.blood_group = data['blood_group']
        
        # Update user fields
        if 'full_name' in data and patient.user:
            patient.user.full_name = data['full_name']
        
        db.session.commit()
        return patient.to_dict()
    
    @staticmethod
    def get_patient_medical_history(patient_id):
        
        patient = Patient.query.get(patient_id)
        if not patient:
            raise ValueError("Patient not found")
        
        history = patient.to_dict()
        
        # Get appointments with treatments
        appointments_data = []
        for appointment in patient.appointments:
            apt_dict = appointment.to_dict()
            if appointment.treatment:
                apt_dict['treatment'] = appointment.treatment.to_dict()
            appointments_data.append(apt_dict)
        
        history['appointments'] = appointments_data
        history['total_appointments'] = len(appointments_data)
        
        return history

