from app.models import db, Appointment, Doctor, Patient
from datetime import datetime, timedelta
from sqlalchemy import and_


class AppointmentService:    
    @staticmethod
    def book_appointment(patient_id, doctor_id, appointment_dt, notes=None):
        
        # Parse datetime if string
        if isinstance(appointment_dt, str):
            appointment_dt = datetime.fromisoformat(appointment_dt.replace('Z', '+00:00'))
        
        # Check if doctor exists
        doctor = Doctor.query.get(doctor_id)
        if not doctor:
            raise ValueError("Doctor not found")
        
        # Check if patient exists
        patient = Patient.query.get(patient_id)
        if not patient:
            raise ValueError("Patient not found")
        
        # Check if slot is available (no existing appointment at that time)
        existing = Appointment.query.filter(
            and_(
                Appointment.doctor_id == doctor_id,
                Appointment.appointment_dt == appointment_dt,
                Appointment.status != 'cancelled'
            )
        ).first()
        
        if existing:
            raise ValueError("Time slot already booked")
        
        # Create appointment
        appointment = Appointment(
            patient_id=patient_id,
            doctor_id=doctor_id,
            appointment_dt=appointment_dt,
            notes=notes,
            status='booked'
        )
        
        db.session.add(appointment)
        db.session.commit()
        
        return appointment.to_dict()
    
    @staticmethod
    def get_appointments(patient_id=None, doctor_id=None, status=None, from_date=None, to_date=None):
        
        query = Appointment.query
        
        if patient_id:
            query = query.filter(Appointment.patient_id == patient_id)
        
        if doctor_id:
            query = query.filter(Appointment.doctor_id == doctor_id)
        
        if status:
            query = query.filter(Appointment.status == status)
        
        if from_date:
            query = query.filter(Appointment.appointment_dt >= from_date)
        
        if to_date:
            query = query.filter(Appointment.appointment_dt <= to_date)
        
        appointments = query.order_by(Appointment.appointment_dt.desc()).all()
        return [apt.to_dict() for apt in appointments]
    
    @staticmethod
    def get_appointment_by_id(appointment_id):
        
        appointment = Appointment.query.get(appointment_id)
        if not appointment:
            raise ValueError("Appointment not found")
        return appointment.to_dict()
    
    @staticmethod
    def update_appointment_status(appointment_id, status):
        
        valid_statuses = ['booked', 'completed', 'cancelled']
        if status not in valid_statuses:
            raise ValueError(f"Invalid status. Must be one of: {', '.join(valid_statuses)}")
        
        appointment = Appointment.query.get(appointment_id)
        if not appointment:
            raise ValueError("Appointment not found")
        
        appointment.status = status
        db.session.commit()
        
        return appointment.to_dict()
    
    @staticmethod
    def cancel_appointment(appointment_id):
        
        return AppointmentService.update_appointment_status(appointment_id, 'cancelled')
    
    @staticmethod
    def complete_appointment(appointment_id):
        
        return AppointmentService.update_appointment_status(appointment_id, 'completed')
    
    @staticmethod
    def get_upcoming_appointments(doctor_id=None, patient_id=None, days=7):
        
        from_date = datetime.now()
        to_date = datetime.now() + timedelta(days=days)
        
        return AppointmentService.get_appointments(
            doctor_id=doctor_id,
            patient_id=patient_id,
            from_date=from_date,
            to_date=to_date,
            status='booked'
        )

