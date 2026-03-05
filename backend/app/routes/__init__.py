from .auth import bp as auth_bp
from .admin import bp as admin_bp
from .doctor import bp as doctor_bp
from .patient import bp as patient_bp
from .uploads import bp as uploads_bp

auth = auth_bp
admin = admin_bp
doctor = doctor_bp
patient = patient_bp
uploads = uploads_bp

