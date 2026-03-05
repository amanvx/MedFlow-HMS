

from .user import db, User
from .department import Department
from .doctor import Doctor
from .patient import Patient
from .appointment import Appointment
from .treatment import Treatment
from .invoice import Invoice
from .upload import Upload
from .job_status import JobStatus

__all__ = [
    "db",
    "User",
    "Department",
    "Doctor",
    "Patient",
    "Appointment",
    "Treatment",
    "Invoice",
    "Upload",
    "JobStatus",
]

