from datetime import datetime
from app.models.user import db


class Patient(db.Model):
    __tablename__ = "patients"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(
        db.Integer, db.ForeignKey("users.id"), unique=True, nullable=False
    )
    contact = db.Column(db.String(50))
    address = db.Column(db.Text)
    date_of_birth = db.Column(db.Date)
    blood_group = db.Column(db.String(10))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    # Relationships
    user = db.relationship("User", back_populates="patient_profile")
    appointments = db.relationship("Appointment", back_populates="patient")
    uploads = db.relationship("Upload", back_populates="patient")
    invoices = db.relationship("Invoice", back_populates="patient")

    def to_dict(self):
        return {
            "id": self.id,
            "user_id": self.user_id,
            "email": self.user.email if self.user else None,
            "full_name": self.user.full_name if self.user else None,
            "contact": self.contact,
            "address": self.address,
            "date_of_birth": self.date_of_birth.isoformat()
            if self.date_of_birth
            else None,
            "blood_group": self.blood_group,
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }

