from flask import Blueprint, request, jsonify
from datetime import datetime, timedelta
from sqlalchemy import and_
from app.models import db, User, Doctor, Patient, Appointment, Treatment
from app.routes.auth import doctor_required, jwt_required, get_jwt_identity

bp = Blueprint("doctor", __name__)


@bp.route("/appointments", methods=["GET"])
@doctor_required
def get_appointments():
    try:
        current_user_id = int(get_jwt_identity())
        doctor = Doctor.query.filter_by(user_id=current_user_id).first()

        if not doctor:
            return jsonify({"error": "Doctor profile not found"}), 404

        # Filter parameters
        status = request.args.get("status", "booked")
        view = request.args.get("view", "today")  # today, week, all

        query = Appointment.query.filter_by(doctor_id=doctor.id)

        if status != "all":
            query = query.filter(Appointment.status == status)

        now = datetime.now()

        if view == "today":
            today_start = now.replace(hour=0, minute=0, second=0, microsecond=0)
            today_end = today_start + timedelta(days=1)
            query = query.filter(
                and_(
                    Appointment.appointment_dt >= today_start,
                    Appointment.appointment_dt < today_end,
                )
            )
        elif view == "week":
            week_start = now.replace(hour=0, minute=0, second=0, microsecond=0)
            week_end = week_start + timedelta(days=7)
            query = query.filter(
                and_(
                    Appointment.appointment_dt >= week_start,
                    Appointment.appointment_dt < week_end,
                )
            )

        appointments = query.order_by(Appointment.appointment_dt).all()

        return jsonify({"appointments": [apt.to_dict() for apt in appointments]}), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500


@bp.route("/appointments/<int:id>", methods=["GET"])
@doctor_required
def get_appointment(id):
    try:
        current_user_id = int(get_jwt_identity())
        doctor = Doctor.query.filter_by(user_id=current_user_id).first()

        if not doctor:
            return jsonify({"error": "Doctor profile not found"}), 404

        appointment = Appointment.query.filter_by(id=id, doctor_id=doctor.id).first()

        if not appointment:
            return jsonify({"error": "Appointment not found"}), 404

        # Get treatment if exists
        treatment = None
        if appointment.treatment:
            treatment = appointment.treatment.to_dict()

        return jsonify(
            {"appointment": appointment.to_dict(), "treatment": treatment}
        ), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500


@bp.route("/appointments/<int:id>", methods=["PATCH"])
@doctor_required
def update_appointment_status(id):
    try:
        current_user_id = int(get_jwt_identity())
        doctor = Doctor.query.filter_by(user_id=current_user_id).first()

        if not doctor:
            return jsonify({"error": "Doctor profile not found"}), 404

        appointment = Appointment.query.filter_by(id=id, doctor_id=doctor.id).first()

        if not appointment:
            return jsonify({"error": "Appointment not found"}), 404

        data = request.get_json()
        if not data:
            return jsonify({"error": "No data provided"}), 400

        new_status = data.get("status")
        notes = data.get("notes", "").strip()

        if new_status and new_status not in ["completed", "cancelled"]:
            return jsonify(
                {"error": 'Invalid status. Must be "completed" or "cancelled"'}
            ), 400

        # Update appointment status
        if new_status:
            appointment.status = new_status

        # Update appointment-level notes (symptoms/reason)
        if "notes" in data:
            appointment.notes = data["notes"].strip()

        # Create or update treatment record when marking as completed
        # Also allow updating if already completed (doctor editing their notes)
        if new_status == "completed" or (
            appointment.status == "completed" and any(
                k in data for k in ["diagnosis", "prescription", "treatment_notes", "next_visit_dt"]
            )
        ):
            diagnosis = data.get("diagnosis", "").strip()
            prescription = data.get("prescription", "").strip()
            treatment_notes = data.get("treatment_notes", "").strip()
            next_visit_dt = data.get("next_visit_dt")

            if appointment.treatment:
                # Update existing treatment record
                treatment = appointment.treatment
            else:
                treatment = Treatment()
                treatment.appointment_id = appointment.id
                db.session.add(treatment)

            if diagnosis:
                treatment.diagnosis = diagnosis
            if prescription:
                treatment.prescription = prescription
            if treatment_notes:
                treatment.notes = treatment_notes

            if next_visit_dt:
                try:
                    treatment.next_visit_dt = datetime.fromisoformat(next_visit_dt)
                except (ValueError, TypeError):
                    pass
            elif "next_visit_dt" in data and not next_visit_dt:
                treatment.next_visit_dt = None

        db.session.commit()

        # Return appointment with treatment
        treatment_data = None
        if appointment.treatment:
            treatment_data = appointment.treatment.to_dict()

        return jsonify(
            {
                "message": "Appointment updated successfully",
                "appointment": appointment.to_dict(),
                "treatment": treatment_data,
            }
        ), 200

    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500


@bp.route("/availability", methods=["GET"])
@doctor_required
def get_availability():
    try:
        current_user_id = int(get_jwt_identity())
        doctor = Doctor.query.filter_by(user_id=current_user_id).first()

        if not doctor:
            return jsonify({"error": "Doctor profile not found"}), 404

        return jsonify({"availability": doctor.get_availability()}), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500


@bp.route("/availability", methods=["PUT"])
@doctor_required
def update_availability():
    try:
        current_user_id = int(get_jwt_identity())
        doctor = Doctor.query.filter_by(user_id=current_user_id).first()

        if not doctor:
            return jsonify({"error": "Doctor profile not found"}), 404

        data = request.get_json()
        if not data or "availability" not in data:
            return jsonify({"error": "Availability data is required"}), 400

        availability = data["availability"]

        # Validate availability format (should be a dict with dates as keys)
        if not isinstance(availability, dict):
            return jsonify(
                {"error": "Availability must be an object with dates as keys"}
            ), 400

        doctor.set_availability(availability)
        db.session.commit()

        return jsonify(
            {
                "message": "Availability updated successfully",
                "availability": doctor.get_availability(),
            }
        ), 200

    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500


@bp.route("/patients/<int:patient_id>/history", methods=["GET"])
@doctor_required
def get_patient_history(patient_id):
    try:
        current_user_id = int(get_jwt_identity())
        doctor = Doctor.query.filter_by(user_id=current_user_id).first()

        if not doctor:
            return jsonify({"error": "Doctor profile not found"}), 404

        patient = Patient.query.get(patient_id)
        if not patient:
            return jsonify({"error": "Patient not found"}), 404

        # Get all completed appointments with treatments
        appointments = (
            Appointment.query.filter_by(patient_id=patient_id, status="completed")
            .order_by(Appointment.appointment_dt.desc())
            .all()
        )

        history = []
        for apt in appointments:
            entry = apt.to_dict()
            if apt.treatment:
                entry["treatment"] = apt.treatment.to_dict()
            history.append(entry)

        return jsonify({"patient": patient.to_dict(), "history": history}), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500


@bp.route("/profile", methods=["GET"])
@doctor_required
def get_profile():
    try:
        current_user_id = int(get_jwt_identity())
        doctor = Doctor.query.filter_by(user_id=current_user_id).first()

        if not doctor:
            return jsonify({"error": "Doctor profile not found"}), 404

        return jsonify({"doctor": doctor.to_dict()}), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500

