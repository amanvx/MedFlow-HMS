from app.tasks import celery
from app.models import db, Appointment, Doctor, Patient, User, Treatment, JobStatus
from datetime import datetime, timedelta
from flask import current_app
import csv
import os


@celery.task
def send_daily_reminders():
    
    try:
        tomorrow = datetime.now() + timedelta(days=1)
        tomorrow_start = tomorrow.replace(hour=0, minute=0, second=0, microsecond=0)
        tomorrow_end = tomorrow_start + timedelta(days=1)

        appointments = Appointment.query.filter(
            Appointment.appointment_dt >= tomorrow_start,
            Appointment.appointment_dt < tomorrow_end,
            Appointment.status == "booked",
        ).all()

        for apt in appointments:
            patient = Patient.query.get(apt.patient_id)
            doctor = Doctor.query.get(apt.doctor_id)

            if patient and doctor:
                # Log instead of sending email for demo
                print(f"[EMAIL REMINDER] To: {patient.user.email}")
                print(f"Subject: Appointment Reminder - Tomorrow")
                print(
                    f"Body: You have an appointment with Dr. {doctor.user.full_name} tomorrow at {apt.appointment_dt}"
                )
                print("-" * 50)

        return f"Sent {len(appointments)} reminder emails"
    except Exception as e:
        return f"Error: {str(e)}"


@celery.task
def generate_monthly_reports():
    
    try:
        last_month = datetime.now() - timedelta(days=30)

        doctors = Doctor.query.all()
        for doctor in doctors:
            appointments = Appointment.query.filter(
                Appointment.doctor_id == doctor.id,
                Appointment.appointment_dt >= last_month,
                Appointment.status == "completed",
            ).all()

            total_appointments = len(appointments)
            total_patients = len(set([apt.patient_id for apt in appointments]))

            # Log instead of sending email for demo
            print(f"[MONTHLY REPORT] To: {doctor.user.email}")
            print(f"Subject: Monthly Activity Report")
            print(f"Total Appointments: {total_appointments}")
            print(f"Unique Patients: {total_patients}")
            print("-" * 50)

        return f"Generated reports for {len(doctors)} doctors"
    except Exception as e:
        return f"Error: {str(e)}"


@celery.task
def export_patient_history(patient_id, user_id):
    
    try:
        # Create job status
        job = JobStatus()
        job.user_id = user_id
        job.job_type = "csv_export"
        job.status = "in_progress"
        db.session.add(job)
        db.session.commit()

        # Get patient's appointments with treatments
        appointments = (
            Appointment.query.filter_by(patient_id=patient_id, status="completed")
            .order_by(Appointment.appointment_dt.desc())
            .all()
        )

        # Generate CSV
        filename = f"patient_history_{patient_id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
        filepath = os.path.join(current_app.config["UPLOAD_FOLDER"], filename)

        with open(filepath, "w", newline="") as csvfile:
            writer = csv.writer(csvfile)
            writer.writerow(["Date", "Doctor", "Diagnosis", "Prescription", "Notes"])

            for apt in appointments:
                treatment = Treatment.query.filter_by(appointment_id=apt.id).first()
                doctor = Doctor.query.get(apt.doctor_id)
                writer.writerow(
                    [
                        apt.appointment_dt.strftime("%Y-%m-%d"),
                        doctor.user.full_name if doctor else "Unknown",
                        treatment.diagnosis if treatment else "",
                        treatment.prescription if treatment else "",
                        treatment.notes if treatment else "",
                    ]
                )

        # Update job status
        job.status = "completed"
        job.result_path = filepath
        job.updated_at = datetime.now()
        db.session.commit()

        # Send email with download link (log for demo)
        patient = Patient.query.get(patient_id)
        print(f"[CSV EXPORT COMPLETE] File: {filepath}")
        print(f"Email sent to: {patient.user.email}")

        return f"CSV exported successfully: {filename}"
    except Exception as e:
        if "job" in locals():
            job.status = "failed"
            job.error_message = str(e)
            db.session.commit()
        return f"Error: {str(e)}"

