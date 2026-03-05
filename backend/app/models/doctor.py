from datetime import datetime
import json
from app.models.user import db


class Doctor(db.Model):
    __tablename__ = "doctors"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(
        db.Integer, db.ForeignKey("users.id"), unique=True, nullable=False
    )
    department_id = db.Column(db.Integer, db.ForeignKey("departments.id"))
    availability = db.Column(db.Text)  # JSON string of next-7-day slots
    specialization = db.Column(db.String(100))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    # Relationships
    user = db.relationship("User", back_populates="doctor_profile")
    department = db.relationship("Department", back_populates="doctors")
    appointments = db.relationship("Appointment", back_populates="doctor")

    def get_availability(self):
        if self.availability:
            return json.loads(self.availability)
        return {}

    def set_availability(self, availability_dict):
        self.availability = json.dumps(availability_dict)

    def to_dict(self):
        return {
            "id": self.id,
            "user_id": self.user_id,
            "email": self.user.email if self.user else None,
            "full_name": self.user.full_name if self.user else None,
            "department_id": self.department_id,
            "department_name": self.department.name if self.department else None,
            "specialization": self.specialization,
            "availability": self.get_availability(),
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }

