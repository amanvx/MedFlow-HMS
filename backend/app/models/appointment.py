

from datetime import datetime
from app.models.user import db


class Appointment(db.Model):
    __tablename__ = "appointments"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    patient_id = db.Column(db.Integer, db.ForeignKey("patients.id"), nullable=False)
    doctor_id = db.Column(db.Integer, db.ForeignKey("doctors.id"), nullable=False)
    appointment_dt = db.Column(db.DateTime, nullable=False)
    status = db.Column(
        db.String(20), nullable=False, default="booked"
    )  # booked, completed, cancelled
    notes = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    # Unique constraint to prevent double-booking
    __table_args__ = (
        db.UniqueConstraint("doctor_id", "appointment_dt", name="unique_appointment"),
    )

    # Relationships
    patient = db.relationship("Patient", back_populates="appointments")
    doctor = db.relationship("Doctor", back_populates="appointments")
    treatment = db.relationship(
        "Treatment", back_populates="appointment", uselist=False
    )

    def to_dict(self):
        return {
            "id": self.id,
            "patient_id": self.patient_id,
            "patient_name": self.patient.user.full_name
            if self.patient and self.patient.user
            else None,
            "doctor_id": self.doctor_id,
            "doctor_name": self.doctor.user.full_name
            if self.doctor and self.doctor.user
            else None,
            "appointment_dt": self.appointment_dt.isoformat()
            if self.appointment_dt
            else None,
            "status": self.status,
            "notes": self.notes,
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }

