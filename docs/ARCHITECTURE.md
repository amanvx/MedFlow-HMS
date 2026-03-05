# MedFlow HMS — Architecture Overview

## High-Level Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                        Browser                                  │
│              Vue 3 SPA (Vite + Bootstrap)                       │
│  ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌──────────────────┐  │
│  │  Admin   │ │  Doctor  │ │ Patient  │ │  Auth (Login/    │  │
│  │ Dashboard│ │Dashboard │ │Dashboard │ │  Register)       │  │
│  └──────────┘ └──────────┘ └──────────┘ └──────────────────┘  │
└────────────────────────────┬────────────────────────────────────┘
                             │ HTTP/REST (JWT in Authorization header)
                             ▼
┌─────────────────────────────────────────────────────────────────┐
│                    Flask API  (:5000)                           │
│  ┌────────────┐  ┌───────────┐  ┌────────────┐  ┌──────────┐  │
│  │ /api/auth  │  │/api/admin │  │/api/doctor │  │/api/     │  │
│  │            │  │           │  │            │  │patient   │  │
│  └──────┬─────┘  └─────┬─────┘  └─────┬──────┘  └────┬─────┘  │
│         └──────────────┴──────────────┴──────────────┘        │
│                         │  Services Layer                       │
│              ┌──────────┴──────────────────┐                   │
│              │  auth / patient / doctor /  │                   │
│              │  appointment / email service│                   │
│              └──────────┬──────────────────┘                   │
│                         │                                       │
│              ┌──────────┴──────────────────┐                   │
│              │     SQLAlchemy ORM           │                   │
│              └──────────┬──────────────────┘                   │
└─────────────────────────┼───────────────────────────────────────┘
                          │
               ┌──────────▼──────────┐
               │  SQLite / PostgreSQL │
               └─────────────────────┘

         ┌────────────────────────────┐
         │  Celery + Redis (optional) │
         │  - Daily appointment       │
         │    reminders (8am)         │
         │  - Monthly doctor reports  │
         │    (1st of month, 9am)     │
         └────────────────────────────┘
```

---

## Backend Layer Details

### `config.py`
Central configuration using Python classes. `DevelopmentConfig` and `ProductionConfig` extend a base `Config`. Selected via `FLASK_ENV` environment variable.

### `app/__init__.py` — App Factory
Uses Flask's application factory pattern (`create_app()`). Responsibilities:
- Initialize extensions (SQLAlchemy, JWT, CORS)
- Register blueprints
- Register global error handlers
- Auto-create admin account and default departments on first run

### Models (`app/models/`)

| Model | Table | Description |
|-------|-------|-------------|
| `User` | `users` | Base account for all roles. Stores email, hashed password, role |
| `Doctor` | `doctors` | Doctor profile linked to a `User` and `Department` |
| `Patient` | `patients` | Patient profile linked to a `User` |
| `Department` | `departments` | Hospital departments |
| `Appointment` | `appointments` | Booking between a patient and doctor |
| `Treatment` | `treatments` | Post-appointment diagnosis and prescription |
| `Invoice` | `invoices` | Billing records per appointment |
| `Upload` | `uploads` | Patient file attachments |
| `JobStatus` | `job_statuses` | Celery background task tracking |

All models share a single `SQLAlchemy` instance (`db`) defined in `app/models/user.py` and re-exported from `app/models/__init__.py`.

### Routes (`app/routes/`)
Each route file is a Flask **Blueprint**:

| Blueprint | Prefix | Access |
|-----------|--------|--------|
| `auth` | `/api/auth` | Public |
| `admin` | `/api/admin` | Admin only |
| `doctor` | `/api/doctor` | Doctor only |
| `patient` | `/api/patient` | Patient only |
| `uploads` | `/api` | Authenticated |

Role guards are implemented as decorators in `app/routes/auth.py` (`admin_required`, `doctor_required`, `patient_required`).

### Services (`app/services/`)
Business logic is kept out of route handlers to keep routes thin and improve testability.

### Middleware (`app/middleware/`)
- `error_handlers.py` — Registers global HTTP error handlers (400, 401, 403, 404, 405, 500) returning consistent JSON responses.
- `auth.py` — JWT helper utilities.

### Utils (`app/utils/`)
- `decorators.py` — Role decorator implementations using JWT claims.
- `validators.py` — Input validation helpers (email, phone, date, required fields).
- `helpers.py` — File naming, datetime formatting, age calculation.
- `cache.py` — Optional Redis caching decorator.

---

## Frontend Layer Details

Built as a **Single-Page Application (SPA)** using:
- **Vue 3** (Composition API optional, Options API used in components)
- **Vue Router 4** — Hash-based routing (`createWebHashHistory`)
- **Vuex 4** — Global state (auth, doctors, departments, appointments)
- **Axios** — HTTP client with JWT interceptor
- **Bootstrap 5** — UI components and layout

### Route Guards
`router/index.js` checks `localStorage` for a token before each navigation. Unauthenticated users are redirected to `/login`. After login, users are redirected to their role-specific dashboard.

### State Management (Vuex)
The store manages:
- Auth state (`user`, `token`, `isAuthenticated`)
- Domain data (`doctors`, `departments`, `appointments`, `patients`)
- UI state (`loading`, `error`)

---

## Authentication Flow

```
Client                          Server
  │                               │
  ├── POST /api/auth/login ──────▶│
  │                               │  Verify email + bcrypt password
  │                               │  Create JWT with {sub: user_id, role: role}
  │◀── { access_token } ──────────┤
  │                               │
  ├── GET /api/admin/overview ───▶│
  │   Authorization: Bearer <jwt> │  Decode JWT → verify role == "admin"
  │◀── { stats: ... } ────────────┤
```

Tokens expire after **1 hour** (configurable via `JWT_ACCESS_TOKEN_EXPIRES`).

---

## File Upload Flow

1. Client POSTs `multipart/form-data` to `/api/upload`
2. Server validates extension and size (max 16 MB)
3. File saved to `uploads/` with a UUID-based filename
4. `Upload` record saved to DB with original filename, stored path, and patient association
5. Client retrieves file via `/api/uploads/<filename>`

---

## Database

Development uses **SQLite** (zero-config). Switch to PostgreSQL for production by setting `DATABASE_URL` in `.env`.

Schema is auto-created by SQLAlchemy on startup (`db.create_all()`).

---

## Background Tasks

Celery tasks in `app/tasks/email_tasks.py`:

| Task | Schedule | Description |
|------|----------|-------------|
| `send_daily_reminders` | Daily at 08:00 | Email patients with next-day appointments |
| `generate_monthly_reports` | 1st of month at 09:00 | Email doctors their monthly activity report |

Redis is required as both the message broker and result backend. Tasks are registered via Celery beat.
