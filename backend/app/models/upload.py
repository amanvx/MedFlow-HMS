from datetime import datetime
from app.models.user import db

class Upload(db.Model):
    __tablename__ = "uploads"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    patient_id = db.Column(db.Integer, db.ForeignKey("patients.id"), nullable=False)
    file_path = db.Column(db.String(500), nullable=False)
    file_type = db.Column(db.String(50))
    file_name = db.Column(db.String(255))
    uploaded_at = db.Column(db.DateTime, default=datetime.utcnow)

    # Relationships
    patient = db.relationship("Patient", back_populates="uploads")

    def to_dict(self):
        return {
            "id": self.id,
            "patient_id": self.patient_id,
            "file_path": self.file_path,
            "file_type": self.file_type,
            "file_name": self.file_name,
            "uploaded_at": self.uploaded_at.isoformat() if self.uploaded_at else None,
        }

