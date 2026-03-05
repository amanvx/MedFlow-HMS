# Frontend Component Structure

This directory contains the complete Vue.js 3 frontend for the Hospital Management System, organized by wireframe specifications.

## 📁 Directory Structure

```
frontend/
├── index.html                  # Main HTML entry point
├── server.py                   # Flask server to serve frontend
├── src/
│   ├── main.js                 # Main Vue application (already exists)
│   └── components/             # Vue components (NEW)
│       ├── LoginComponent.vue
│       ├── RegisterComponent.vue
│       ├── AdminDashboard.vue
│       ├── DoctorDashboard.vue
│       ├── PatientDashboard.vue
│       ├── FindDoctor.vue
│       ├── BookAppointment.vue
│       ├── AppointmentHistory.vue
│       └── PatientRecord.vue
```

## 🎨 Components Overview

### Authentication Components
- **LoginComponent.vue** - Login page with role selector (matches login_screen.html wireframe)
- **RegisterComponent.vue** - Patient registration form

### Dashboard Components
- **AdminDashboard.vue** - Admin dashboard with statistics, doctor management, appointments (matches admin_dashboard.html)
- **DoctorDashboard.vue** - Doctor dashboard with today's schedule, availability management (matches doctor_dashboard.html)
- **PatientDashboard.vue** - Patient dashboard with upcoming appointments, doctor availability grid (matches patient_dashboard.html)

### Functional Components
- **FindDoctor.vue** - Doctor search and browse interface (matches find_doctor.html)
- **BookAppointment.vue** - Multi-step appointment booking wizard (matches book_appointment.html)
- **AppointmentHistory.vue** - Patient appointment history with tabs (matches appointment_history.html)
- **PatientRecord.vue** - Doctor view of patient consultation form (matches patient_record.html)

## 🔧 Integration Method

### Option 1: Using .vue Files (Recommended with Build Tool)

If you want to use the created .vue files, you'll need to set up a build process:

1. Install Vue CLI or Vite:
```bash
npm install -g @vue/cli
# or
npm create vite@latest
```

2. Set up a proper Vue project structure
3. Import and register components
4. Use Vue Router for navigation

### Option 2: Using CDN (Current Setup)

The current index.html uses Vue 3 via CDN. To integrate the components:

1. Convert the .vue files to inline component definitions in main.js
2. Register them globally using `app.component()`
3. Use dynamic component rendering with `<component :is="currentView">`

## 📋 Component Props and Events

### AdminDashboard
- **Props**: `user` (object)
- **Events**: `logout`

### DoctorDashboard
- **Props**: `user` (object)
- **Events**: `logout`, `save-availability`, `fetch-doctor-data`

### PatientDashboard
- **Props**: `user` (object)
- **Events**: `logout`, `fetch-patient-data`

### FindDoctor
- **Props**: None
- **Events**: `back`, `book-confirmed`, `fetch-doctors`, `fetch-departments`

### BookAppointment
- **Props**: `doctor` (object)
- **Events**: `confirm`, `cancel`

### AppointmentHistory
- **Props**: None
- **Events**: `back`, `reschedule`, `cancel`, `download-pdf`, `fetch-appointments`

### PatientRecord
- **Props**: `appointment` (object)
- **Events**: `save`, `close`

## 🎯 Wireframe Mapping

| Wireframe File | Component File | Description |
|----------------|----------------|-------------|
| login_screen.html | LoginComponent.vue | Login interface |
| admin_dashboard.html | AdminDashboard.vue | Admin overview |
| doctor_dashboard.html | DoctorDashboard.vue | Doctor schedule |
| patient_dashboard.html | PatientDashboard.vue | Patient home |
| find_doctor.html | FindDoctor.vue | Doctor search |
| book_appointment.html | BookAppointment.vue | Booking wizard |
| appointment_history.html | AppointmentHistory.vue | Appointment list |
| patient_record.html | PatientRecord.vue | Consultation form |
| doctor_management.html | Part of AdminDashboard.vue | Doctor CRUD |
| appointment_management.html | Part of AdminDashboard.vue | Appointment oversight |

## 🚀 Next Steps

1. **For Development**: Set up a proper Vue 3 project with build tools
2. **For Production**: Use the Vue CLI or Vite to bundle the application
3. **API Integration**: Connect all components to the backend API endpoints
4. **State Management**: Consider using Pinia or Vuex for complex state
5. **Routing**: Implement Vue Router for proper URL-based navigation

## 📝 Notes

- All components follow the Bootstrap 5 design system
- Icons use Bootstrap Icons (bi-*)
- Color scheme matches the wireframes (blues, greens, gradients)
- Responsive design for mobile and desktop
- Components emit events for parent-child communication
- API calls use Axios with JWT token authentication

## 🔗 Backend API Endpoints Used

- POST `/api/auth/login`
- POST `/api/auth/register`
- GET `/api/admin/overview`
- GET `/api/admin/doctors`
- GET `/api/doctor/appointments`
- GET `/api/patient/appointments`
- GET `/api/patient/doctors`
- POST `/api/patient/appointments`

See backend documentation for complete API reference.
