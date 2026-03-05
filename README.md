# MedFlow HMS

A modern, full-stack Hospital Management System (HMS) built with Flask (Python) for the backend and Vue 3 (Vite) for the frontend. MedFlow HMS streamlines hospital operations, supporting appointment scheduling, patient management, doctor workflows, and admin controls.

## Features

- **Role-based Access:** Separate dashboards and permissions for Admin, Doctor, and Patient.
- **Appointment Management:** Book, update, and track appointments; doctors can mark appointments as completed and add treatment details.
- **Patient Records:** View and manage patient history, treatments, and invoices.
- **Doctor Management:** Assign departments, manage schedules, and review patient histories.
- **Authentication:** Secure JWT-based login and registration.
- **Responsive UI:** Built with Vue 3, Vite, and Bootstrap for a modern user experience.

## Tech Stack

- **Backend:** Python 3.11, Flask, SQLAlchemy, JWT
- **Frontend:** Vue 3, Vite, Bootstrap
- **Other:** RESTful API, modular architecture

## Getting Started

### Prerequisites

- Python 3.11+
- Node.js (v16+ recommended)
- npm or yarn

### Backend Setup

1. Navigate to the backend directory:
	```
	cd backend
	```
2. Create and activate a virtual environment:
	```
	python -m venv venv
	# On macOS/Linux:
	source venv/bin/activate
	# On Windows:
	venv\Scripts\activate
	```
3. Install dependencies:
	```
	pip install -r requirements.txt
	```
4. Run the backend server:
	```
	python run.py
	```

### Frontend Setup

1. Navigate to the frontend directory:
	```
	cd frontend
	```
2. Install dependencies:
	```
	npm install
	```
3. Start the frontend server:
	```
	npm run dev
	```

### Access

- Backend API: [http://localhost:5000](http://localhost:5000)
- Frontend App: [http://localhost:8080](http://localhost:8080)

## Project Structure

- `backend/` — Flask API, models, routes, services
- `frontend/` — Vue 3 app, components, views, router, store
- `wireframes/` — UI wireframes for reference

## Contributing

Pull requests are welcome! Please review the `CONTRIBUTING.md` (if available) and follow code style guidelines.

## License

This project is licensed under the MIT License.
