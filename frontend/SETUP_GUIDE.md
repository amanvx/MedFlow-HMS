# Vue.js Components Setup Guide

## Created Components (Based on Wireframes)

The following Vue Single File Components (.vue) have been created in `frontend/src/components/`:

### ✅ Created Files:

1. **LoginComponent.vue** - Login page based on login_screen.html wireframe
2. **RegisterComponent.vue** - Patient registration form
3. **AdminDashboard.vue** - Admin dashboard based on admin_dashboard.html
4. **DoctorDashboard.vue** - Doctor dashboard based on doctor_dashboard.html
5. **PatientDashboard.vue** - Patient dashboard based on patient_dashboard.html
6. **FindDoctor.vue** - Doctor search page based on find_doctor.html
7. **BookAppointment.vue** - Appointment booking wizard based on book_appointment.html
8. **AppointmentHistory.vue** - Appointment history based on appointment_history.html
9. **PatientRecord.vue** - Patient consultation form based on patient_record.html

## How to Use These Components

### Option 1: Build Setup (Recommended)

To use these .vue files with proper Single File Component support:

```bash
# Install Node.js and npm first, then:
cd frontend
npm init -y
npm install vue@3
npm install -D @vitejs/plugin-vue vite

# Create vite.config.js
# Update package.json scripts
# Import components in main.js
npm run dev
```

### Option 2: Current CDN Setup

The existing `frontend/src/main.js` and `frontend/index.html` use Vue 3 via CDN. To integrate:

1. **Convert .vue files to inline components** in main.js
2. **Copy the template sections** from each .vue file
3. **Copy the script sections** (methods, data, props)
4. **Register as global components** using `app.component(name, definition)`

### Quick Start - CDN Integration

The components are already structured to work with your existing setup. The templates, scripts, and styles from each .vue file can be extracted and registered in main.js.

Example for one component:

```javascript
// In main.js
app.component('login-component', {
  props: [],
  data() {
    return {
      // data from LoginComponent.vue
    }
  },
  methods: {
    // methods from LoginComponent.vue
  },
  template: `
    // template from LoginComponent.vue
  `
});
```

## Component Architecture

```
App (main.js)
├── LoginComponent
├── RegisterComponent
└── Authenticated Views
    ├── AdminDashboard
    │   ├── DoctorManagement (inline)
    │   ├── AppointmentManagement (inline)
    │   └── DepartmentManagement (inline)
    ├── DoctorDashboard
    │   ├── PatientRecord
    │   └── ScheduleManagement (inline)
    └── PatientDashboard
        ├── FindDoctor
        │   └── BookAppointment (modal)
        ├── AppointmentHistory
        └── MedicalHistory (inline)
```

## Styling

All components use:
- Bootstrap 5 classes
- Bootstrap Icons (bi-*)
- Custom CSS in `<style scoped>` sections
- Gradient backgrounds matching wireframes
- Responsive grid system

## API Integration Points

Each component emits events or calls APIs for:
- **Authentication**: login, register endpoints
- **Admin**: dashboard stats, doctor CRUD, appointments
- **Doctor**: appointments, patient records, availability
- **Patient**: find doctors, book appointments, view history

## Current Status

✅ All wireframe-based components created
✅ Component structure matches wireframes
✅ Props and events defined
✅ Templates implemented with Bootstrap 5
✅ Inline styles match wireframe designs

🔄 **Next Step**: Integrate with existing main.js or set up build process

## Files Created Summary

| File | Lines | Description |
|------|-------|-------------|
| LoginComponent.vue | ~180 | Login form with role selector |
| RegisterComponent.vue | ~140 | Patient registration |
| AdminDashboard.vue | ~260 | Admin stats & management |
| DoctorDashboard.vue | ~280 | Doctor schedule & patients |
| PatientDashboard.vue | ~240 | Patient home & availability |
| FindDoctor.vue | ~220 | Doctor search & cards |
| BookAppointment.vue | ~320 | 3-step booking wizard |
| AppointmentHistory.vue | ~240 | Appointment tabs & history |
| PatientRecord.vue | ~280 | Consultation form |

**Total: 9 components, ~2,160 lines of Vue code**

---

For questions or issues, refer to the Vue.js 3 documentation: https://vuejs.org/guide/introduction.html
