# MedFlow HMS — API Reference

**Base URL:** `http://localhost:5000/api`

All protected endpoints require an `Authorization: Bearer <token>` header.

---

## Auth — `/api/auth`

### POST `/api/auth/register`
Register a new patient account.

**Request body:**
```json
{
  "email": "patient@example.com",
  "password": "secret123",
  "full_name": "Jane Doe",
  "contact": "9876543210",
  "address": "123 Main St"
}
```

**Response `201`:**
```json
{
  "message": "Registration successful",
  "user": { "id": 1, "email": "...", "role": "patient", "full_name": "..." },
  "access_token": "<jwt>"
}
```

---

### POST `/api/auth/login`
Login and receive a JWT token.

**Request body:**
```json
{ "email": "admin@hospital.com", "password": "admin123" }
```

**Response `200`:**
```json
{
  "user": { "id": 1, "role": "admin", ... },
  "access_token": "<jwt>"
}
```

---

### GET `/api/auth/profile`
🔒 Get the current user's profile.

**Response `200`:**
```json
{
  "user": { "id": 1, "email": "...", "role": "admin", "full_name": "..." }
}
```

---

## Admin — `/api/admin` 🔒 Admin only

### GET `/api/admin/overview`
Dashboard statistics.

**Response:**
```json
{
  "stats": {
    "total_doctors": 5,
    "total_patients": 42,
    "total_appointments": 120,
    "total_departments": 8,
    "appointment_breakdown": { "booked": 30, "completed": 80, "cancelled": 10 }
  },
  "recent_appointments": [...]
}
```

---

### GET `/api/admin/doctors`
List doctors with optional filters.

**Query params:** `search`, `department_id`, `page`, `per_page`

---

### POST `/api/admin/doctors`
Create a new doctor account.

**Request body:**
```json
{
  "email": "dr.smith@hospital.com",
  "password": "secure123",
  "full_name": "Dr. John Smith",
  "department_id": 1,
  "specialization": "Cardiology"
}
```

---

### PUT `/api/admin/doctors/<id>`
Update a doctor's details.

---

### DELETE `/api/admin/doctors/<id>`
Deactivate (soft-delete) a doctor.

---

### GET `/api/admin/patients`
List all patients. Query params: `search`, `page`, `per_page`

---

### GET `/api/admin/departments`
List all departments.

---

### POST `/api/admin/departments`
Create a department.

```json
{ "name": "Radiology", "description": "Imaging and diagnostics" }
```

---

### PUT `/api/admin/departments/<id>`
Update a department.

---

### DELETE `/api/admin/departments/<id>`
Delete a department.

---

### GET `/api/admin/appointments`
List all appointments. Query params: `status`, `doctor_id`, `patient_id`, `date_from`, `date_to`, `page`, `per_page`

---

## Doctor — `/api/doctor` 🔒 Doctor only

### GET `/api/doctor/profile`
Get the authenticated doctor's profile.

---

### GET `/api/doctor/appointments`
Get the doctor's appointment schedule. Query params: `status`, `date`

---

### PATCH `/api/doctor/appointments/<id>`
Update appointment status (e.g., mark as completed).

```json
{ "status": "completed", "notes": "Patient doing well." }
```

---

### POST `/api/doctor/appointments/<id>/treatment`
Add or update treatment details for a completed appointment.

```json
{
  "diagnosis": "Hypertension",
  "prescription": "Amlodipine 5mg",
  "notes": "Follow up in 2 weeks"
}
```

---

### GET `/api/doctor/patients`
List patients who have had appointments with this doctor.

---

### GET `/api/doctor/availability`
Get the doctor's availability slots.

---

### PUT `/api/doctor/availability`
Update availability slots.

```json
{
  "2026-03-10": ["09:00", "10:00", "11:00"],
  "2026-03-11": ["14:00", "15:00"]
}
```

---

## Patient — `/api/patient` 🔒 Patient only

### GET `/api/patient/profile`
Get the authenticated patient's profile and medical info.

---

### GET `/api/patient/appointments`
List the patient's appointments.

---

### POST `/api/patient/appointments`
Book an appointment.

```json
{
  "doctor_id": 2,
  "appointment_dt": "2026-03-15T10:00:00"
}
```

---

### DELETE `/api/patient/appointments/<id>`
Cancel an appointment.

---

### GET `/api/patient/doctors`
Browse available doctors. Query params: `department_id`, `search`

---

### GET `/api/patient/invoices`
List the patient's invoices.

---

## Uploads — `/api` 🔒 Authenticated

### POST `/api/upload`
Upload a file for a patient.

**Form data:** `file` (multipart), `patient_id`

Allowed extensions: `pdf`, `png`, `jpg`, `jpeg`, `doc`, `docx`. Max size: 16 MB.

---

### GET `/api/uploads/<filename>`
Retrieve an uploaded file.

---

## Health

### GET `/api/health`
Health check (no auth required).

```json
{ "status": "healthy", "message": "HMS API is running" }
```

---

## Error Responses

All errors return JSON in the following format:

```json
{ "error": "Error Type", "message": "Human-readable description" }
```

| Code | Meaning |
|------|---------|
| 400 | Bad Request — invalid input |
| 401 | Unauthorized — missing or expired token |
| 403 | Forbidden — insufficient role |
| 404 | Not Found |
| 422 | Unprocessable Entity — malformed JWT |
| 500 | Internal Server Error |
