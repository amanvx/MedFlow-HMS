<!-- Appointment History Component -->
<template>
  <div>
    <div class="d-flex justify-content-between align-items-center mb-4">
      <h2>Appointment History</h2>
      <button class="btn btn-sm btn-outline-secondary" @click="$emit('back')">
        <i class="bi bi-arrow-left"></i> Back
      </button>
    </div>

    <!-- Tabs -->
    <ul class="nav nav-tabs mb-4">
      <li class="nav-item">
        <button 
          :class="['nav-link', {active: activeTab === 'upcoming'}]"
          @click="activeTab = 'upcoming'"
        >
          Upcoming ({{ upcomingCount }})
        </button>
      </li>
      <li class="nav-item">
        <button 
          :class="['nav-link', {active: activeTab === 'past'}]"
          @click="activeTab = 'past'"
        >
          Past Visits
        </button>
      </li>
    </ul>

    <!-- Upcoming Appointments -->
    <div v-if="activeTab === 'upcoming'">
      <div v-for="apt in upcomingAppointments" :key="apt.id" class="appointment-card mb-3">
        <div class="d-flex justify-content-between align-items-start">
          <div class="d-flex align-items-center">
            <div class="doctor-icon me-3">
              {{ getInitials(apt.doctor_name) }}
            </div>
            <div>
              <h6 class="mb-0">{{ apt.doctor_name }}</h6>
              <small class="text-muted">{{ apt.department || 'General' }}</small>
              <div class="mt-1">
                <span :class="['status-badge', `badge-${apt.status}`]">
                  {{ apt.status }}
                </span>
              </div>
            </div>
          </div>
          <div class="text-end">
            <div class="fw-bold">{{ formatDate(apt.appointment_dt) }}</div>
            <div class="text-muted small">{{ formatTime(apt.appointment_dt) }}</div>
          </div>
        </div>
        <div class="mt-3 d-flex gap-2 justify-content-end">
          <button class="btn btn-outline-secondary btn-sm" @click="reschedule(apt)">
            Reschedule
          </button>
          <button class="btn btn-outline-danger btn-sm" @click="cancel(apt)">
            Cancel Booking
          </button>
        </div>
      </div>

      <div v-if="!upcomingAppointments.length" class="empty-state">
        <i class="bi bi-calendar-x"></i>
        <p>No upcoming appointments</p>
        <button class="btn btn-primary" @click="$emit('book-new')">
          Book New Appointment
        </button>
      </div>
    </div>

    <!-- Past Appointments -->
    <div v-if="activeTab === 'past'">
      <div v-for="apt in pastAppointments" :key="apt.id" class="appointment-card past-card mb-3">
        <div class="d-flex justify-content-between">
          <div class="d-flex align-items-center">
            <div class="doctor-icon me-3">
              {{ getInitials(apt.doctor_name) }}
            </div>
            <div>
              <h6 class="mb-0">{{ apt.doctor_name }}</h6>
              <small class="text-muted">{{ apt.specialization }}</small>
            </div>
          </div>
          <div class="text-end">
            <div class="fw-bold">{{ formatDate(apt.appointment_dt) }}</div>
            <span :class="['status-badge', `badge-${apt.status}`]">
              {{ apt.status }}
            </span>
          </div>
        </div>

        <div v-if="apt.treatment" class="mt-3">
          <hr class="my-2">
          <div class="row small">
            <div class="col-6">
              <strong>Diagnosis:</strong> {{ apt.treatment.diagnosis || 'N/A' }}
            </div>
            <div class="col-6">
              <strong>Prescription:</strong> {{ apt.treatment.prescription || 'N/A' }}
            </div>
          </div>
        </div>

        <div class="mt-2 d-flex gap-2">
          <button class="btn btn-light border btn-sm" @click="viewFullRecord(apt)">
            View Full Record
          </button>
          <button class="btn btn-light border btn-sm" @click="downloadPDF(apt)">
            Download PDF
          </button>
        </div>
      </div>

      <div v-if="!pastAppointments.length" class="empty-state">
        <i class="bi bi-clock-history"></i>
        <p>No past appointments</p>
      </div>
    </div>

    <!-- Record Details Modal -->
    <div v-if="showRecordModal" class="modal-overlay" @click.self="showRecordModal = false">
      <div class="modal-content">
        <div class="modal-header">
          <h5>Appointment Record</h5>
          <button type="button" class="btn-close" @click="showRecordModal = false"></button>
        </div>
        <div class="modal-body">
          <div v-if="selectedRecord">
            <div class="mb-3">
              <strong>Date:</strong> {{ formatDate(selectedRecord.appointment_dt) }}
            </div>
            <div class="mb-3">
              <strong>Doctor:</strong> {{ selectedRecord.doctor_name }}
            </div>
            <div class="mb-3">
              <strong>Diagnosis:</strong><br>
              {{ selectedRecord.treatment?.diagnosis || 'N/A' }}
            </div>
            <div class="mb-3">
              <strong>Prescription:</strong><br>
              {{ selectedRecord.treatment?.prescription || 'N/A' }}
            </div>
            <div class="mb-3">
              <strong>Notes:</strong><br>
              {{ selectedRecord.treatment?.notes || 'N/A' }}
            </div>
          </div>
        </div>
        <div class="modal-footer">
          <button class="btn btn-secondary" @click="showRecordModal = false">Close</button>
          <button class="btn btn-primary" @click="downloadPDF(selectedRecord)">
            <i class="bi bi-download me-2"></i>Download PDF
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import api from '../axios'

export default {
  name: 'AppointmentHistory',
  data() {
    return {
      activeTab: 'upcoming',
      upcomingAppointments: [],
      pastAppointments: [],
      showRecordModal: false,
      selectedRecord: null
    }
  },
  computed: {
    upcomingCount() {
      return this.upcomingAppointments.length
    }
  },
  methods: {
    getInitials(name) {
      if (!name) return '?'
      return name.split(' ').map(n => n[0]).join('').toUpperCase().substr(0, 2)
    },
    formatDate(dt) {
      if (!dt) return ''
      const date = new Date(dt)
      return date.toLocaleDateString('en-US', { month: 'short', day: 'numeric', year: 'numeric' })
    },
    formatTime(dt) {
      if (!dt) return ''
      const date = new Date(dt)
      return date.toLocaleTimeString('en-US', { hour: '2-digit', minute: '2-digit' })
    },
    async fetchAppointments() {
      try {
        const [upcomingRes, pastRes] = await Promise.all([
          api.get('/api/patient/appointments', { params: { upcoming: 'true', status: 'booked' } }),
          api.get('/api/patient/appointments', { params: { status: 'completed' } })
        ])
        this.upcomingAppointments = upcomingRes.data.appointments || []
        this.pastAppointments = pastRes.data.appointments || []
      } catch (error) {
        console.error('Failed to fetch appointments:', error)
      }
    },
    reschedule(apt) {
      this.$emit('reschedule', apt)
    },
    async cancel(apt) {
      if (confirm('Are you sure you want to cancel this appointment?')) {
        try {
          await api.put(`/api/patient/appointments/${apt.id}`, { action: 'cancel' })
          this.fetchAppointments()
        } catch (error) {
          console.error('Failed to cancel appointment:', error)
          alert(error.response?.data?.error || 'Failed to cancel appointment')
        }
      }
    },
    viewFullRecord(apt) {
      this.selectedRecord = apt
      this.showRecordModal = true
    },
    downloadPDF(apt) {
      this.$emit('download-pdf', apt)
    }
  },
  mounted() {
    this.fetchAppointments()
  }
}
</script>

<style scoped>
.appointment-card {
  background: white;
  border-radius: 8px;
  border-left: 5px solid #007bff;
  box-shadow: 0 2px 4px rgba(0,0,0,0.05);
  padding: 15px;
}

.past-card {
  border-left-color: #6c757d;
}

.doctor-icon {
  width: 50px;
  height: 50px;
  border-radius: 50%;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  display: flex;
  align-items: center;
  justify-content: center;
  font-weight: 700;
}

.status-badge {
  font-size: 0.75rem;
  padding: 4px 8px;
  border-radius: 12px;
  font-weight: 500;
}

.badge-booked {
  background-color: #e3f2fd;
  color: #1976d2;
}

.badge-completed {
  background-color: #e8f5e9;
  color: #388e3c;
}

.badge-cancelled {
  background-color: #ffebee;
  color: #d32f2f;
}

.badge-pending {
  background-color: #fff3e0;
  color: #f57c00;
}
</style>
