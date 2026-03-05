from datetime import datetime
from app.models.user import db


class JobStatus(db.Model):
    __tablename__ = "job_status"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    job_type = db.Column(db.String(50), nullable=False)  # csv_export, report, etc.
    status = db.Column(
        db.String(20), nullable=False, default="pending"
    )  # pending, in_progress, completed, failed
    result_path = db.Column(db.String(500))
    error_message = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime)

    def to_dict(self):
        return {
            "id": self.id,
            "user_id": self.user_id,
            "job_type": self.job_type,
            "status": self.status,
            "result_path": self.result_path,
            "error_message": self.error_message,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }

