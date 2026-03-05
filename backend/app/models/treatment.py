from datetime import datetime
from app.models.user import db


class Treatment(db.Model):
    __tablename__ = "treatments"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    appointment_id = db.Column(
        db.Integer, db.ForeignKey("appointments.id"), unique=True, nullable=False
    )
    diagnosis = db.Column(db.Text)
    prescription = db.Column(db.Text)
    notes = db.Column(db.Text)
    next_visit_dt = db.Column(db.DateTime)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    # Relationships
    appointment = db.relationship("Appointment", back_populates="treatment")

    def to_dict(self):
        return {
            "id": self.id,
            "appointment_id": self.appointment_id,
            "diagnosis": self.diagnosis,
            "prescription": self.prescription,
            "notes": self.notes,
            "next_visit_dt": self.next_visit_dt.isoformat()
            if self.next_visit_dt
            else None,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "appointment": self.appointment.to_dict() if self.appointment else None,
        }

