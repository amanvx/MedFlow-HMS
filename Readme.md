# MedFlow HMS

A modern, full-stack **Hospital Management System (HMS)** built with **Flask** (Python) for the backend and **Vue 3** (Vite) for the frontend. MedFlow streamlines hospital operations — supporting appointment scheduling, patient management, doctor workflows, admin controls, and optional background tasks via Celery.

> **Demo admin credentials (first run):** `admin@hospital.com` / `admin123`

---

## Table of Contents

- [Features](#features)
- [Tech Stack](#tech-stack)
- [Project Structure](#project-structure)
- [Getting Started](#getting-started)
- [Environment Variables](#environment-variables)
- [API Reference](#api-reference)
- [Background Tasks (Celery)](#background-tasks-celery)
- [Deployment](#deployment)
---

## Features

- **Role-based Access:** Separate dashboards and permissions for Admin, Doctor, and Patient.
- **Appointment Management:** Book, update, and track appointments; doctors can mark appointments as completed and add treatment details.
- **Patient Records:** View and manage patient history, treatments, and invoices.
- **Doctor Management:** Assign departments, manage schedules, and review patient histories.
- **Authentication:** Secure JWT-based login and registration.
- **Email Notifications:** Appointment reminders and welcome emails via SMTP.
- **Background Tasks:** Celery + Redis for daily reminders and monthly reports (optional).
- **Responsive UI:** Built with Vue 3, Vite, and Bootstrap for a modern user experience.

## Tech Stack

| Layer | Technology |
|-------|-----------|
| Backend API | Python 3.11, Flask 3, Flask-JWT-Extended, Flask-SQLAlchemy |
| Database | SQLite (dev) / PostgreSQL (prod) via SQLAlchemy |
| Frontend | Vue 3, Vite 5, Vuex 4, Vue Router 4, Bootstrap 5 |
| Background Tasks | Celery 5 + Redis (optional) |
| Auth | JWT (JSON Web Tokens) |

---

## Project Structure

```
medflow-hms/
├── .env.example              # Environment variable template
├── .gitignore
├── Readme.md
├── backend/
│   ├── run.py                # Application entry point
│   ├── config.py             # Configuration classes (dev/prod)
│   ├── requirements.txt
│   └── app/
│       ├── __init__.py       # App factory + DB init
│       ├── models/           # SQLAlchemy models
│       │   ├── user.py       # User (admin/doctor/patient)
│       │   ├── doctor.py
│       │   ├── patient.py
│       │   ├── department.py
│       │   ├── appointment.py
│       │   ├── treatment.py
│       │   ├── invoice.py
│       │   ├── upload.py
│       │   └── job_status.py
│       ├── routes/           # Blueprint route handlers
│       │   ├── auth.py       # /api/auth/*
│       │   ├── admin.py      # /api/admin/*
│       │   ├── doctor.py     # /api/doctor/*
│       │   ├── patient.py    # /api/patient/*
│       │   └── uploads.py    # /api/uploads/*
│       ├── services/         # Business-logic layer
│       │   ├── auth_service.py
│       │   ├── doctor_service.py
│       │   ├── patient_service.py
│       │   ├── appointment_service.py
│       │   └── email_service.py
│       ├── middleware/
│       │   ├── auth.py       # JWT helper utilities
│       │   └── error_handlers.py  # Global HTTP error handlers
│       ├── tasks/            # Celery background tasks
│       │   └── email_tasks.py
│       └── utils/
│           ├── cache.py      # Redis cache helpers
│           ├── decorators.py # Role-based access decorators
│           ├── helpers.py    # Date/file utilities
│           └── validators.py # Input validation
├── frontend/
│   ├── index.html
│   ├── package.json
│   ├── vite.config.js
│   ├── server.py             # Flask static server (production only)
│   └── src/
│       ├── main.js
│       ├── App.vue
│       ├── axios.js          # Axios instance + interceptors
│       ├── router/index.js   # Vue Router
│       ├── store/index.js    # Vuex store
│       ├── views/            # Top-level route views
│       └── components/       # Reusable UI components
├── uploads/                  # Patient file uploads (auto-created)
└── wireframes/               # HTML wireframe references
```

---

## Getting Started

### Prerequisites

- Python 3.11+
- Node.js v18+ and npm

### 1. Clone & configure environment

```bash
git clone https://github.com/amanvx/MedFlow-HMS.git
cd MedFlow-HMS
cp .env.example backend/.env
# Edit backend/.env with your settings
```

### 2. Backend Setup

```bash
cd backend
python -m venv venv

# macOS/Linux
source venv/bin/activate
# Windows
venv\Scripts\activate

pip install -r requirements.txt
python run.py
```

The API starts at **http://localhost:5000**. An admin account and default departments are created automatically on first run.

### 3. Frontend Setup

```bash
cd frontend
npm install
npm run dev
```

The app is available at **http://localhost:8080**.

---

## Environment Variables

Copy `.env.example` to `backend/.env` and fill in the values.

| Variable | Default | Description |
|----------|---------|-------------|
| `FLASK_ENV` | `development` | `development` or `production` |
| `SECRET_KEY` | *(generated)* | Flask secret key |
| `JWT_SECRET_KEY` | *(generated)* | JWT signing key |
| `DATABASE_URL` | SQLite `../database.db` | Database connection string |
| `REDIS_URL` | `redis://localhost:6379/0` | Redis URL (for Celery) |
| `MAIL_SERVER` | `smtp.gmail.com` | SMTP host |
| `MAIL_PORT` | `587` | SMTP port |
| `MAIL_USERNAME` | — | Sender email address |
| `MAIL_PASSWORD` | — | SMTP password / App password |
| `ADMIN_EMAIL` | `admin@hospital.com` | Initial admin email |
| `ADMIN_PASSWORD` | `admin123` | Initial admin password |

> **Security:** Always replace default `SECRET_KEY`, `JWT_SECRET_KEY`, and `ADMIN_PASSWORD` before deploying.

---

## API Reference

See [docs/API.md](docs/API.md) for the full endpoint reference.

**Base URL:** `http://localhost:5000/api`

| Group | Prefix | Description |
|-------|--------|-------------|
| Auth | `/api/auth` | Register, login, profile |
| Admin | `/api/admin` | Manage doctors, patients, departments, appointments |
| Doctor | `/api/doctor` | View schedule, update appointments, treatments |
| Patient | `/api/patient` | Book appointments, view history, invoices |
| Uploads | `/api/uploads` | Upload/download patient files |
| Health | `/api/health` | Health check |

---

## Background Tasks (Celery)

Daily reminders and monthly reports run via Celery + Redis. These are **optional** — the app works without them.

```bash
# Start Redis (Docker example)
docker run -d -p 6379:6379 redis:alpine

# Start Celery worker (from backend/)
celery -A app.tasks worker --loglevel=info

# Start Celery beat scheduler
celery -A app.tasks beat --loglevel=info
```

---

## Deployment

### Production build (frontend)

```bash
cd frontend
npm run build
# Outputs to frontend/dist/

# Serve with Flask static server (optional)
python server.py
```
