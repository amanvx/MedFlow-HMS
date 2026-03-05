from flask import Blueprint, request, jsonify
from sqlalchemy import func
from app.models import db, User, Doctor, Patient, Department, Appointment, Treatment
from app.routes.auth import admin_required

bp = Blueprint("admin", __name__)


@bp.route("/overview", methods=["GET"])
@admin_required
def get_overview():
    try:
        total_doctors = Doctor.query.count()
        total_patients = Patient.query.count()
        total_appointments = Appointment.query.count()
        total_departments = Department.query.count()

        # Appointment status breakdown
        booked_count = Appointment.query.filter_by(status="booked").count()
        completed_count = Appointment.query.filter_by(status="completed").count()
        cancelled_count = Appointment.query.filter_by(status="cancelled").count()

        # Recent appointments
        recent_appointments = (
            Appointment.query.order_by(Appointment.created_at.desc()).limit(10).all()
        )

        return jsonify(
            {
                "stats": {
                    "total_doctors": total_doctors,
                    "total_patients": total_patients,
                    "total_appointments": total_appointments,
                    "total_departments": total_departments,
                    "appointment_breakdown": {
                        "booked": booked_count,
                        "completed": completed_count,
                        "cancelled": cancelled_count,
                    },
                },
                "recent_appointments": [apt.to_dict() for apt in recent_appointments],
            }
        ), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@bp.route("/doctors", methods=["GET"])
@admin_required
def get_doctors():
    try:
        search = request.args.get("search", "").strip()
        department_id = request.args.get("department_id", type=int)
        page = request.args.get("page", 1, type=int)
        per_page = request.args.get("per_page", 20, type=int)

        query = Doctor.query.join(User).filter(User.is_active == True)

        if search:
            query = query.filter(User.full_name.ilike(f"%{search}%"))

        if department_id:
            query = query.filter(Doctor.department_id == department_id)

        pagination = query.paginate(page=page, per_page=per_page, error_out=False)
        doctors = pagination.items

        return jsonify(
            {
                "doctors": [doc.to_dict() for doc in doctors],
                "pagination": {
                    "page": page,
                    "per_page": per_page,
                    "total": pagination.total,
                    "pages": pagination.pages,
                    "has_next": pagination.has_next,
                    "has_prev": pagination.has_prev,
                },
            }
        ), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@bp.route("/doctors", methods=["POST"])
@admin_required
def create_doctor():
    data = request.get_json()

    if not data:
        return jsonify({"error": "No data provided"}), 400

    email = data.get("email", "").strip().lower()
    password = data.get("password", "")
    full_name = data.get("full_name", "").strip()
    department_id = data.get("department_id")
    specialization = data.get("specialization", "").strip()

    # Validation
    if not email or not password or not full_name:
        return jsonify({"error": "Email, password, and full name are required"}), 400

    if len(password) < 6:
        return jsonify({"error": "Password must be at least 6 characters"}), 400

    if User.query.filter_by(email=email).first():
        return jsonify({"error": "Email already registered"}), 409

    if department_id and not Department.query.get(department_id):
        return jsonify({"error": "Department not found"}), 404

    try:
        # Create user
        user = User()
        user.email = email
        user.role = "doctor"
        user.full_name = full_name
        user.set_password(password)

        db.session.add(user)
        db.session.flush()

        # Create doctor profile
        doctor = Doctor()
        doctor.user_id = user.id
        doctor.department_id = department_id
        doctor.specialization = specialization
        doctor.set_availability({})  # Empty availability initially

        db.session.add(doctor)
        db.session.commit()

        return jsonify(
            {"message": "Doctor created successfully", "doctor": doctor.to_dict()}
        ), 201

    except Exception as e:
        db.session.rollback()
        return jsonify({"error": f"Failed to create doctor: {str(e)}"}), 500


@bp.route("/doctors/<int:id>", methods=["GET"])
@admin_required
def get_doctor(id):
    doctor = Doctor.query.get(id)
    if not doctor:
        return jsonify({"error": "Doctor not found"}), 404

    return jsonify({"doctor": doctor.to_dict()}), 200


@bp.route("/doctors/<int:id>", methods=["PUT"])
@admin_required
def update_doctor(id):
    doctor = Doctor.query.get(id)
    if not doctor:
        return jsonify({"error": "Doctor not found"}), 404

    data = request.get_json()
    if not data:
        return jsonify({"error": "No data provided"}), 400

    try:
        # Update user fields
        if "full_name" in data:
            doctor.user.full_name = data["full_name"].strip()

        if "email" in data:
            email = data["email"].strip().lower()
            if email != doctor.user.email and User.query.filter_by(email=email).first():
                return jsonify({"error": "Email already in use"}), 409
            doctor.user.email = email

        # Update doctor fields
        if "department_id" in data:
            if data["department_id"] and not Department.query.get(
                data["department_id"]
            ):
                return jsonify({"error": "Department not found"}), 404
            doctor.department_id = data["department_id"]

        if "specialization" in data:
            doctor.specialization = data["specialization"].strip()

        if "availability" in data:
            doctor.set_availability(data["availability"])

        db.session.commit()

        return jsonify(
            {"message": "Doctor updated successfully", "doctor": doctor.to_dict()}
        ), 200

    except Exception as e:
        db.session.rollback()
        return jsonify({"error": f"Failed to update doctor: {str(e)}"}), 500


@bp.route("/doctors/<int:id>", methods=["DELETE"])
@admin_required
def delete_doctor(id):
    doctor = Doctor.query.get(id)
    if not doctor:
        return jsonify({"error": "Doctor not found"}), 404

    try:
        # Soft delete by deactivating user
        doctor.user.is_active = False
        db.session.commit()

        return jsonify({"message": "Doctor deactivated successfully"}), 200

    except Exception as e:
        db.session.rollback()
        return jsonify({"error": f"Failed to deactivate doctor: {str(e)}"}), 500


@bp.route("/departments", methods=["GET"])
@admin_required
def get_departments():
    departments = Department.query.all()
    return jsonify({"departments": [dept.to_dict() for dept in departments]}), 200


@bp.route("/departments", methods=["POST"])
@admin_required
def create_department():
    data = request.get_json()

    if not data or not data.get("name"):
        return jsonify({"error": "Department name is required"}), 400

    name = data["name"].strip()
    description = data.get("description", "").strip()

    if Department.query.filter_by(name=name).first():
        return jsonify({"error": "Department already exists"}), 409

    try:
        dept = Department()
        dept.name = name
        dept.description = description

        db.session.add(dept)
        db.session.commit()

        return jsonify(
            {"message": "Department created successfully", "department": dept.to_dict()}
        ), 201

    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500


@bp.route("/departments/<int:id>", methods=["PUT"])
@admin_required
def update_department(id):
    dept = Department.query.get(id)
    if not dept:
        return jsonify({"error": "Department not found"}), 404

    data = request.get_json()
    if not data:
        return jsonify({"error": "No data provided"}), 400

    try:
        if "name" in data:
            name = data["name"].strip()
            if name != dept.name and Department.query.filter_by(name=name).first():
                return jsonify({"error": "Department name already exists"}), 409
            dept.name = name

        if "description" in data:
            dept.description = data["description"].strip()

        db.session.commit()

        return jsonify(
            {"message": "Department updated successfully", "department": dept.to_dict()}
        ), 200

    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500


@bp.route("/departments/<int:id>", methods=["DELETE"])
@admin_required
def delete_department(id):
    dept = Department.query.get(id)
    if not dept:
        return jsonify({"error": "Department not found"}), 404

    # Check if doctors are using this department
    if Doctor.query.filter_by(department_id=id).first():
        return jsonify({"error": "Cannot delete department with assigned doctors"}), 400

    try:
        db.session.delete(dept)
        db.session.commit()

        return jsonify({"message": "Department deleted successfully"}), 200

    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500


@bp.route("/patients", methods=["GET"])
@admin_required
def get_patients():
    try:
        search = request.args.get("search", "").strip()
        page = request.args.get("page", 1, type=int)
        per_page = request.args.get("per_page", 20, type=int)

        query = Patient.query.join(User).filter(User.is_active == True)

        if search:
            query = query.filter(
                db.or_(
                    User.full_name.ilike(f"%{search}%"), User.email.ilike(f"%{search}%")
                )
            )

        pagination = query.paginate(page=page, per_page=per_page, error_out=False)
        patients = pagination.items

        return jsonify(
            {
                "patients": [pat.to_dict() for pat in patients],
                "pagination": {
                    "page": page,
                    "per_page": per_page,
                    "total": pagination.total,
                    "pages": pagination.pages,
                    "has_next": pagination.has_next,
                    "has_prev": pagination.has_prev,
                },
            }
        ), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@bp.route("/patients/<int:id>", methods=["GET"])
@admin_required
def get_patient(id):
    patient = Patient.query.get(id)
    if not patient:
        return jsonify({"error": "Patient not found"}), 404

    # Get patient's appointments and treatments
    appointments = Appointment.query.filter_by(patient_id=id).all()

    return jsonify(
        {
            "patient": patient.to_dict(),
            "appointments": [apt.to_dict() for apt in appointments],
        }
    ), 200


@bp.route("/patients/<int:id>", methods=["DELETE"])
@admin_required
def delete_patient(id):
    patient = Patient.query.get(id)
    if not patient:
        return jsonify({"error": "Patient not found"}), 404

    try:
        patient.user.is_active = False
        db.session.commit()

        return jsonify({"message": "Patient deactivated successfully"}), 200

    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500


@bp.route("/appointments", methods=["GET"])
@admin_required
def get_all_appointments():
    try:
        status = request.args.get("status")
        doctor_id = request.args.get("doctor_id", type=int)
        patient_id = request.args.get("patient_id", type=int)
        page = request.args.get("page", 1, type=int)
        per_page = request.args.get("per_page", 50, type=int)

        query = Appointment.query

        if status:
            query = query.filter(Appointment.status == status)

        if doctor_id:
            query = query.filter(Appointment.doctor_id == doctor_id)

        if patient_id:
            query = query.filter(Appointment.patient_id == patient_id)

        pagination = query.order_by(Appointment.appointment_dt.desc()).paginate(
            page=page, per_page=per_page, error_out=False
        )
        appointments = pagination.items

        return jsonify(
            {
                "appointments": [apt.to_dict() for apt in appointments],
                "pagination": {
                    "page": page,
                    "per_page": per_page,
                    "total": pagination.total,
                    "pages": pagination.pages,
                    "has_next": pagination.has_next,
                    "has_prev": pagination.has_prev,
                },
            }
        ), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@bp.route("/appointments/<int:id>/cancel", methods=["POST", "PATCH"])
@admin_required
def cancel_appointment(id):
    appointment = Appointment.query.get(id)
    if not appointment:
        return jsonify({"error": "Appointment not found"}), 404

    if appointment.status == "cancelled":
        return jsonify({"error": "Appointment is already cancelled"}), 400

    try:
        appointment.status = "cancelled"
        db.session.commit()
        return jsonify(
            {"message": "Appointment cancelled successfully", "appointment": appointment.to_dict()}
        ), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500


@bp.route("/appointments/<int:id>/status", methods=["PATCH"])
@admin_required
def update_appointment_status(id):
    appointment = Appointment.query.get(id)
    if not appointment:
        return jsonify({"error": "Appointment not found"}), 404

    data = request.get_json()
    if not data or not data.get("status"):
        return jsonify({"error": "Status is required"}), 400

    new_status = data["status"]
    if new_status not in ["booked", "completed", "cancelled"]:
        return jsonify({"error": "Invalid status"}), 400

    try:
        appointment.status = new_status
        db.session.commit()
        return jsonify(
            {"message": "Appointment updated", "appointment": appointment.to_dict()}
        ), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500

