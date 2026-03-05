from flask import Blueprint, request, jsonify, current_app
from werkzeug.utils import secure_filename
from app.models import db, Upload, Patient
from app.routes.auth import jwt_required, get_jwt_identity
import os

bp = Blueprint("uploads", __name__)

ALLOWED_EXTENSIONS = {"pdf", "png", "jpg", "jpeg", "doc", "docx"}


def allowed_file(filename):
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS


@bp.route("/patient/<int:patient_id>/uploads", methods=["POST"])
@jwt_required()
def upload_file(patient_id):
    
    current_user_id = get_jwt_identity()

    # Check if user has permission
    patient = Patient.query.get(patient_id)
    if not patient:
        return jsonify({"error": "Patient not found"}), 404

    if request.method == "POST":
        if "file" not in request.files:
            return jsonify({"error": "No file part"}), 400

        file = request.files["file"]
        if file.filename == "":
            return jsonify({"error": "No selected file"}), 400

        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)

            # Create patient directory
            patient_dir = os.path.join(
                current_app.config["UPLOAD_FOLDER"], str(patient_id)
            )
            os.makedirs(patient_dir, exist_ok=True)

            # Save file
            filepath = os.path.join(patient_dir, filename)
            file.save(filepath)

            # Save to database
            upload = Upload()
            upload.patient_id = patient_id
            upload.file_path = filepath
            upload.file_name = filename
            upload.file_type = filename.rsplit(".", 1)[1].lower()

            db.session.add(upload)
            db.session.commit()

            return jsonify(
                {"message": "File uploaded successfully", "upload": upload.to_dict()}
            ), 201
        else:
            return jsonify({"error": "File type not allowed"}), 400


@bp.route("/patient/<int:patient_id>/uploads", methods=["GET"])
@jwt_required()
def get_uploads(patient_id):
    
    uploads = Upload.query.filter_by(patient_id=patient_id).all()
    return jsonify({"uploads": [upload.to_dict() for upload in uploads]}), 200


@bp.route("/uploads/<int:id>/download", methods=["GET"])
@jwt_required()
def download_file(id):
    
    upload = Upload.query.get(id)
    if not upload:
        return jsonify({"error": "File not found"}), 404

    if os.path.exists(upload.file_path):
        from flask import send_file

        return send_file(
            upload.file_path, as_attachment=True, download_name=upload.file_name
        )
    else:
        return jsonify({"error": "File not found on server"}), 404

