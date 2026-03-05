from flask import Blueprint, request, jsonify, Response
from datetime import datetime, timedelta
from sqlalchemy import and_, or_
import csv, io
from app.models import (
    db,
    User,
    Doctor,
    Patient,
    Appointment,
    Treatment,
    Department,
    Invoice,
    Upload,
)
from app.routes.auth import patient_required, jwt_required, get_jwt_identity

bp = Blueprint("patient", __name__)


@bp.route("/doctors", methods=["GET"])
@patient_required
def search_doctors():
    try:
        search = request.args.get("search", "").strip()
        department_id = request.args.get("department_id", type=int)
        available_only = request.args.get("available_only", "false").lower() == "true"

        query = Doctor.query.join(User).filter(
            User.is_active == True, User.role == "doctor"
        )

        if search:
            query = query.filter(
                or_(
                    User.full_name.ilike(f"%{search}%"),
                    Doctor.specialization.ilike(f"%{search}%"),
                )
            )

        if department_id:
            query = query.filter(Doctor.department_id == department_id)

        doctors = query.all()

        # Filter by availability if requested
        result = []
        for doc in doctors:
            availability = doc.get_availability()
            if available_only and not availability:
                continue

            doc_dict = doc.to_dict()
            result.append(doc_dict)

        return jsonify({"doctors": result}), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500


@bp.route("/doctors/<int:id>/availability", methods=["GET"])
@patient_required
def get_doctor_availability(id):
    try:
        doctor = Doctor.query.get(id)
        if not doctor:
            return jsonify({"error": "Doctor not found"}), 404

        availability = doctor.get_availability()

        # Get booked slots for next 7 days
        now = datetime.now()
        week_later = now + timedelta(days=7)

        booked_appointments = Appointment.query.filter(
            and_(
                Appointment.doctor_id == id,
                Appointment.appointment_dt >= now,
                Appointment.appointment_dt < week_later,
                Appointment.status.in_(["booked", "completed"]),
            )
        ).all()

        booked_slots = [apt.appointment_dt.isoformat() for apt in booked_appointments]

        return jsonify(
            {
                "doctor_id": id,
                "doctor_name": doctor.user.full_name if doctor.user else None,
                "availability": availability,
                "booked_slots": booked_slots,
            }
        ), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500


@bp.route("/appointments", methods=["POST"])
@patient_required
def book_appointment():
    try:
        current_user_id = int(get_jwt_identity())
        patient = Patient.query.filter_by(user_id=current_user_id).first()

        if not patient:
            return jsonify({"error": "Patient profile not found"}), 404

        data = request.get_json()
        if not data:
            return jsonify({"error": "No data provided"}), 400

        doctor_id = data.get("doctor_id")
        appointment_dt_str = data.get("appointment_dt")
        notes = data.get("notes", "").strip()

        if not doctor_id or not appointment_dt_str:
            return jsonify(
                {"error": "Doctor ID and appointment datetime are required"}
            ), 400

        # Validate doctor exists
        doctor = Doctor.query.get(doctor_id)
        if not doctor:
            return jsonify({"error": "Doctor not found"}), 404

        # Parse datetime
        try:
            appointment_dt = datetime.fromisoformat(appointment_dt_str)
        except ValueError:
            return jsonify(
                {"error": "Invalid datetime format. Use ISO format (YYYY-MM-DDTHH:MM)"}
            ), 400

        # Check if slot is in the future
        if appointment_dt < datetime.now():
            return jsonify({"error": "Cannot book appointments in the past"}), 400

        # Check for double booking
        existing = Appointment.query.filter_by(
            doctor_id=doctor_id, appointment_dt=appointment_dt, status="booked"
        ).first()

        if existing:
            return jsonify({"error": "This slot is already booked"}), 409

        # Create appointment
        appointment = Appointment()
        appointment.patient_id = patient.id
        appointment.doctor_id = doctor_id
        appointment.appointment_dt = appointment_dt
        appointment.status = "booked"
        appointment.notes = notes

        db.session.add(appointment)
        db.session.commit()

        return jsonify(
            {
                "message": "Appointment booked successfully",
                "appointment": appointment.to_dict(),
            }
        ), 201

    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500


@bp.route("/appointments", methods=["GET"])
@patient_required
def get_appointments():
    
    try:
        current_user_id = int(get_jwt_identity())
        patient = Patient.query.filter_by(user_id=current_user_id).first()

        if not patient:
            return jsonify({"error": "Patient profile not found"}), 404

        status_filter = request.args.get("status")  # booked, completed, cancelled
        upcoming = request.args.get("upcoming", "false").lower() == "true"

        query = Appointment.query.filter_by(patient_id=patient.id)

        if status_filter:
            query = query.filter(Appointment.status == status_filter)

        if upcoming:
            query = query.filter(Appointment.appointment_dt >= datetime.now())

        appointments = query.order_by(Appointment.appointment_dt.desc()).all()

        return jsonify({"appointments": [apt.to_dict() for apt in appointments]}), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500


@bp.route("/appointments/<int:id>", methods=["PUT"])
@patient_required
def update_appointment(id):
    
    try:
        current_user_id = int(get_jwt_identity())
        patient = Patient.query.filter_by(user_id=current_user_id).first()

        if not patient:
            return jsonify({"error": "Patient profile not found"}), 404

        appointment = Appointment.query.filter_by(id=id, patient_id=patient.id).first()

        if not appointment:
            return jsonify({"error": "Appointment not found"}), 404

        # Cannot modify completed or cancelled appointments
        if appointment.status in ["completed", "cancelled"]:
            return jsonify(
                {"error": f"Cannot modify {appointment.status} appointment"}
            ), 400

        data = request.get_json()
        if not data:
            return jsonify({"error": "No data provided"}), 400

        action = data.get("action")  # 'reschedule' or 'cancel'

        if action == "cancel":
            appointment.status = "cancelled"
            db.session.commit()

            return jsonify(
                {
                    "message": "Appointment cancelled successfully",
                    "appointment": appointment.to_dict(),
                }
            ), 200

        elif action == "reschedule":
            new_datetime_str = data.get("new_datetime")
            if not new_datetime_str:
                return jsonify(
                    {"error": "New datetime is required for rescheduling"}
                ), 400

            try:
                new_datetime = datetime.fromisoformat(new_datetime_str)
            except ValueError:
                return jsonify({"error": "Invalid datetime format"}), 400

            # Check for double booking
            existing = Appointment.query.filter(
                and_(
                    Appointment.doctor_id == appointment.doctor_id,
                    Appointment.appointment_dt == new_datetime,
                    Appointment.status == "booked",
                    Appointment.id != id,
                )
            ).first()

            if existing:
                return jsonify({"error": "New slot is already booked"}), 409

            appointment.appointment_dt = new_datetime
            db.session.commit()

            return jsonify(
                {
                    "message": "Appointment rescheduled successfully",
                    "appointment": appointment.to_dict(),
                }
            ), 200

        else:
            return jsonify(
                {"error": 'Invalid action. Use "reschedule" or "cancel"'}
            ), 400

    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500


@bp.route("/history", methods=["GET"])
@patient_required
def get_medical_history():
    
    try:
        current_user_id = int(get_jwt_identity())
        patient = Patient.query.filter_by(user_id=current_user_id).first()

        if not patient:
            return jsonify({"error": "Patient profile not found"}), 404

        # Get completed appointments with treatments
        appointments = (
            Appointment.query.filter_by(patient_id=patient.id, status="completed")
            .order_by(Appointment.appointment_dt.desc())
            .all()
        )

        history = []
        for apt in appointments:
            entry = {"appointment": apt.to_dict()}
            if apt.treatment:
                entry["treatment"] = apt.treatment.to_dict()
            history.append(entry)

        return jsonify({"history": history}), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500


@bp.route("/export", methods=["POST"])
@patient_required
def export_history():
    
    try:
        current_user_id = int(get_jwt_identity())
        patient = Patient.query.filter_by(user_id=current_user_id).first()
        if not patient:
            return jsonify({"error": "Patient profile not found"}), 404

        appointments = (
            Appointment.query.filter_by(patient_id=patient.id, status="completed")
            .order_by(Appointment.appointment_dt.desc())
            .all()
        )

        output = io.StringIO()
        writer = csv.writer(output)
        writer.writerow(["Date", "Doctor", "Department", "Diagnosis", "Prescription", "Notes", "Status"])

        for apt in appointments:
            treatment = apt.treatment
            writer.writerow([
                apt.appointment_dt.strftime("%Y-%m-%d %H:%M") if apt.appointment_dt else "",
                apt.doctor.user.full_name if apt.doctor and apt.doctor.user else "",
                apt.doctor.department.name if apt.doctor and apt.doctor.department else "",
                treatment.diagnosis if treatment else "",
                treatment.prescription if treatment else "",
                treatment.notes if treatment else "",
                apt.status,
            ])

        output.seek(0)
        return Response(
            output.getvalue(),
            mimetype="text/csv",
            headers={
                "Content-Disposition": f"attachment; filename=medical_history_{datetime.now().strftime('%Y%m%d')}.csv",
                "Access-Control-Expose-Headers": "Content-Disposition",
            },
        )

    except Exception as e:
        return jsonify({"error": str(e)}), 500


@bp.route("/departments", methods=["GET"])
@patient_required
def get_departments():
    
    try:
        departments = Department.query.all()
        return jsonify({"departments": [dept.to_dict() for dept in departments]}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@bp.route("/invoices", methods=["GET"])
@patient_required
def get_invoices():
    
    try:
        current_user_id = int(get_jwt_identity())
        patient = Patient.query.filter_by(user_id=current_user_id).first()

        if not patient:
            return jsonify({"error": "Patient profile not found"}), 404

        status = request.args.get("status")  # pending, paid, failed

        query = Invoice.query.filter_by(patient_id=patient.id)

        if status:
            query = query.filter(Invoice.status == status)

        invoices = query.order_by(Invoice.created_at.desc()).all()

        return jsonify({"invoices": [inv.to_dict() for inv in invoices]}), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500


@bp.route("/invoices/<int:id>/pay", methods=["POST"])
@patient_required
def pay_invoice(id):
    
    try:
        current_user_id = int(get_jwt_identity())
        patient = Patient.query.filter_by(user_id=current_user_id).first()

        if not patient:
            return jsonify({"error": "Patient profile not found"}), 404

        invoice = Invoice.query.filter_by(id=id, patient_id=patient.id).first()

        if not invoice:
            return jsonify({"error": "Invoice not found"}), 404

        if invoice.status == "paid":
            return jsonify({"error": "Invoice already paid"}), 400

        data = request.get_json()
        if not data:
            return jsonify({"error": "Payment data required"}), 400

        # Dummy payment validation
        card_number = data.get("card_number", "").replace(" ", "")
        expiry = data.get("expiry", "")
        cvv = data.get("cvv", "")

        # Basic validation
        if len(card_number) < 13 or len(card_number) > 19:
            return jsonify({"error": "Invalid card number"}), 400

        if len(cvv) < 3 or len(cvv) > 4:
            return jsonify({"error": "Invalid CVV"}), 400

        # Simulate payment processing
        invoice.status = "paid"
        invoice.paid_at = datetime.now()
        db.session.commit()

        return jsonify(
            {
                "message": "Payment successful",
                "transaction_id": f"TXN{datetime.now().strftime('%Y%m%d%H%M%S')}",
                "invoice": invoice.to_dict(),
            }
        ), 200

    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500


@bp.route("/uploads", methods=["GET"])
@patient_required
def get_uploads():
    
    try:
        current_user_id = int(get_jwt_identity())
        patient = Patient.query.filter_by(user_id=current_user_id).first()

        if not patient:
            return jsonify({"error": "Patient profile not found"}), 404

        uploads = Upload.query.filter_by(patient_id=patient.id).all()

        return jsonify({"uploads": [upload.to_dict() for upload in uploads]}), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500

