from datetime import datetime
from app.models.user import db


class Invoice(db.Model):

    __tablename__ = "invoices"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    patient_id = db.Column(db.Integer, db.ForeignKey("patients.id"), nullable=False)
    amount_cents = db.Column(db.Integer, nullable=False)
    description = db.Column(db.Text)
    status = db.Column(
        db.String(20), nullable=False, default="pending"
    )  # pending, paid, failed
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    paid_at = db.Column(db.DateTime)

    # Relationships
    patient = db.relationship("Patient", back_populates="invoices")

    def to_dict(self):
        return {
            "id": self.id,
            "patient_id": self.patient_id,
            "amount": self.amount_cents / 100,  # Convert cents to dollars
            "description": self.description,
            "status": self.status,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "paid_at": self.paid_at.isoformat() if self.paid_at else None,
        }

