<!-- Doctor Dashboard Component -->
<template>
  <div class="dashboard-wrapper">
    <!-- Sidebar -->
    <div class="sidebar">
      <div class="sidebar-header">
        <h4>HMS Doctor</h4>
      </div>
      <nav class="sidebar-menu">
        <a @click="currentView = 'dashboard'" :class="['menu-item', {active: currentView === 'dashboard'}]">
          <i class="bi bi-speedometer2"></i> Dashboard
        </a>
        <a @click="currentView = 'patients'" :class="['menu-item', {active: currentView === 'patients'}]">
          <i class="bi bi-people"></i> Patient Records
        </a>
        <a @click="currentView = 'schedule'" :class="['menu-item', {active: currentView === 'schedule'}]">
          <i class="bi bi-calendar3"></i> My Schedule
        </a>
        <a @click="handleLogout" class="menu-item mt-5 text-danger">
          <i class="bi bi-box-arrow-right"></i> Logout
        </a>
      </nav>
    </div>

    <!-- Main Content -->
    <div class="main-content">
      <!-- Dashboard View -->
      <div v-if="currentView === 'dashboard'">
        <div class="d-flex justify-content-between align-items-center mb-4">
          <div>
            <h2>Doctor Dashboard</h2>
            <p class="text-muted">Today: {{ currentDate }}</p>
          </div>
        </div>

        <!-- Statistics Cards -->
        <div class="row mb-4">
          <div class="col-md-3">
            <div class="card stat-card bg-primary text-white">
              <div class="card-body p-3">
                <div class="small">Today's Appointments</div>
                <h3 class="mt-2">{{ todayCount }}</h3>
              </div>
            </div>
          </div>
          <div class="col-md-3">
            <div class="card stat-card bg-success text-white">
              <div class="card-body p-3">
                <div class="small">Completed Today</div>
                <h3 class="mt-2">{{ completedToday }}</h3>
              </div>
            </div>
          </div>
          <div class="col-md-3">
            <div class="card stat-card bg-warning text-dark">
              <div class="card-body p-3">
                <div class="small">Pending Reviews</div>
                <h3 class="mt-2">{{ pendingCount }}</h3>
              </div>
            </div>
          </div>
          <div class="col-md-3">
            <div class="card stat-card bg-info text-white">
              <div class="card-body p-3">
                <div class="small">Upcoming (7 Days)</div>
                <h3 class="mt-2">{{ weekCount }}</h3>
              </div>
            </div>
          </div>
        </div>

        <!-- Today's Schedule & Availability -->
        <div class="row">
          <div class="col-lg-8">
            <div class="content-card mb-4">
              <div class="card-header">
                <h5 class="mb-0">Today's Schedule</h5>
              </div>
              <div class="card-body">
                <table class="table table-hover">
                  <thead>
                    <tr class="table-light">
                      <th>Time</th>
                      <th>Patient Name</th>
                      <th>Reason</th>
                      <th>Status</th>
                      <th>Action</th>
                    </tr>
                  </thead>
                  <tbody>
                    <tr v-for="apt in todayAppointments" :key="apt.id">
                      <td>{{ formatTime(apt.appointment_dt) }}</td>
                      <td>{{ apt.patient_name }}</td>
                      <td>{{ apt.notes || 'General Checkup' }}</td>
                      <td>
                        <span :class="['status-badge', `bg-${getStatusColor(apt.status)}`]">
                          {{ apt.status }}
                        </span>
                      </td>
                      <td>
                        <button 
                          class="btn btn-outline-primary btn-sm"
                          @click="openPatientRecord(apt)"
                        >
                          {{ apt.status === 'completed' ? 'View' : 'Record' }}
                        </button>
                      </td>
                    </tr>
                    <tr v-if="!todayAppointments.length">
                      <td colspan="5" class="text-center text-muted">No appointments today</td>
                    </tr>
                  </tbody>
                </table>
              </div>
            </div>

            <div class="content-card">
              <div class="card-header">
                <h5 class="mb-0">Upcoming Appointments (Tomorrow)</h5>
              </div>
              <div class="card-body">
                <ul class="list-group list-group-flush">
                  <li 
                    v-for="apt in tomorrowAppointments" 
                    :key="apt.id"
                    class="list-group-item d-flex justify-content-between align-items-center"
                  >
                    <div>
                      <strong>{{ formatTime(apt.appointment_dt) }}</strong> - {{ apt.patient_name }}
                    </div>
                    <span class="badge bg-light text-dark border">Confirmed</span>
                  </li>
                  <li v-if="!tomorrowAppointments.length" class="list-group-item text-center text-muted">
                    No appointments tomorrow
                  </li>
                </ul>
              </div>
            </div>
          </div>

          <!-- Availability Section -->
          <div class="col-lg-4">
            <div class="content-card mb-4">
              <div class="card-header">
                <h5 class="mb-0">Availability (Next 7 Days)</h5>
              </div>
              <div class="card-body">
                <p class="small text-muted">Toggle your working status for patients to book.</p>
                <div class="d-grid gap-2">
                  <div 
                    v-for="day in availabilityDays" 
                    :key="day.date"
                    class="availability-slot d-flex justify-content-between align-items-center"
                  >
                    <span>{{ day.label }}</span>
                    <div class="form-check form-switch">
                      <input 
                        class="form-check-input" 
                        type="checkbox" 
                        v-model="day.available"
                        @change="updateAvailability"
                      >
                    </div>
                  </div>
                </div>
                <button class="btn btn-primary w-100 mt-3" @click="saveAvailability">
                  Save Availability
                </button>
              </div>
            </div>

            <div class="content-card">
              <div class="card-header">
                <h5 class="mb-0">Quick Patient Search</h5>
              </div>
              <div class="card-body">
                <input 
                  type="text" 
                  class="form-control" 
                  placeholder="Search by name or ID..."
                  v-model="patientSearch"
                >
                <div class="mt-3 small">
                  <a href="#" class="text-decoration-none" @click.prevent="currentView = 'patients'">
                    View Full Patient List &rarr;
                  </a>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- Patient Records View -->
      <div v-if="currentView === 'patients'">
        <h2 class="fw-bold mb-4">Patient Records</h2>
        <div class="card shadow-sm">
          <div class="card-body">
            <div class="table-responsive">
              <table class="table table-hover">
                <thead class="table-light">
                  <tr><th>Patient</th><th>Date</th><th>Notes</th><th>Status</th><th>Action</th></tr>
                </thead>
                <tbody>
                  <tr v-for="apt in allAppointments" :key="apt.id">
                    <td>{{ apt.patient_name }}</td>
                    <td>{{ formatTime(apt.appointment_dt) }}</td>
                    <td>{{ apt.notes || 'General Checkup' }}</td>
                    <td><span :class="['badge', `bg-${getStatusColor(apt.status)}`]">{{ apt.status }}</span></td>
                    <td>
                      <button class="btn btn-sm btn-outline-primary" @click="openPatientRecord(apt)">
                        {{ apt.status === 'completed' ? 'View' : 'Record' }}
                      </button>
                    </td>
                  </tr>
                  <tr v-if="!allAppointments.length">
                    <td colspan="5" class="text-center text-muted">No patient records found</td>
                  </tr>
                </tbody>
              </table>
            </div>
          </div>
        </div>
      </div>

      <!-- Schedule Management View -->
      <div v-if="currentView === 'schedule'">
        <h2 class="fw-bold mb-4">My Schedule</h2>
        <div class="row">
          <div class="col-md-6">
            <div class="card shadow-sm">
              <div class="card-header"><strong>Set Weekly Availability</strong></div>
              <div class="card-body">
                <p class="small text-muted mb-3">Toggle availability for patients to book appointments.</p>
                <div class="d-grid gap-2">
                  <div v-for="day in availabilityDays" :key="day.date"
                    class="availability-slot d-flex justify-content-between align-items-center">
                    <span>{{ day.label }}</span>
                    <div class="form-check form-switch mb-0">
                      <input class="form-check-input" type="checkbox" v-model="day.available">
                    </div>
                  </div>
                </div>
                <button class="btn btn-primary w-100 mt-3" @click="saveAvailabilityToApi">Save Availability</button>
              </div>
            </div>
          </div>
          <div class="col-md-6">
            <div class="card shadow-sm">
              <div class="card-header"><strong>Upcoming (7 Days)</strong></div>
              <div class="card-body p-0">
                <ul class="list-group list-group-flush">
                  <li v-for="apt in weekAppointments" :key="apt.id" class="list-group-item d-flex justify-content-between">
                    <span><strong>{{ formatTime(apt.appointment_dt) }}</strong> – {{ apt.patient_name }}</span>
                    <span class="badge bg-primary">Booked</span>
                  </li>
                  <li v-if="!weekAppointments.length" class="list-group-item text-center text-muted">No appointments this week</li>
                </ul>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Patient Record Modal -->
    <div v-if="showRecordModal" class="modal-overlay" @click.self="closeRecordModal">
      <div class="modal-content position-relative">
        <!-- Toast inside modal -->
        <div v-if="recordToast.msg" :class="['alert', recordToast.type === 'success' ? 'alert-success' : 'alert-danger', 'alert-dismissible', 'm-2', 'mb-0']" style="position:sticky;top:0;z-index:10;">
          <i :class="recordToast.type === 'success' ? 'bi bi-check-circle-fill me-2' : 'bi bi-x-circle-fill me-2'"></i>
          {{ recordToast.msg }}
          <button type="button" class="btn-close" @click="recordToast.msg = ''"></button>
        </div>
        <PatientRecord
          v-if="selectedAppointment"
          :appointment="selectedAppointment"
          :saving="recordSaving"
          @close="closeRecordModal"
          @save="handleSaveRecord"
        />
      </div>
    </div>
  </div>
</template>

<script>
import api from '../axios'
import PatientRecord from './PatientRecord.vue'

export default {
  name: 'DoctorDashboard',
  components: { PatientRecord },
  props: ['user'],
  data() {
    return {
      currentView: 'dashboard',
      currentDate: new Date().toLocaleDateString('en-US', { month: 'long', day: 'numeric', year: 'numeric' }),
      todayCount: 0,
      completedToday: 0,
      pendingCount: 0,
      weekCount: 0,
      todayAppointments: [],
      tomorrowAppointments: [],
      weekAppointments: [],
      allAppointments: [],
      availabilityDays: [],
      patientSearch: '',
      showRecordModal: false,
      selectedAppointment: null,
      recordSaving: false,
      recordToast: { msg: '', type: 'success' }
    }
  },
  methods: {
    handleLogout() {
      this.$emit('logout')
    },
    formatTime(dt) {
      if (!dt) return ''
      const date = new Date(dt)
      return date.toLocaleString('en-US', { month: 'short', day: 'numeric', hour: '2-digit', minute: '2-digit' })
    },
    getStatusColor(status) {
      const colors = { 'booked': 'secondary', 'completed': 'success', 'cancelled': 'danger', 'in-progress': 'warning' }
      return colors[status] || 'light'
    },
    closeRecordModal() {
      this.showRecordModal = false
      this.recordToast = { msg: '', type: 'success' }
    },
    async openPatientRecord(apt) {
      this.selectedAppointment = null
      this.recordToast = { msg: '', type: 'success' }
      this.showRecordModal = true
      try {
        // Fetch full appointment including existing treatment data
        const res = await api.get(`/api/doctor/appointments/${apt.id}`)
        this.selectedAppointment = {
          ...res.data.appointment,
          treatment: res.data.treatment || null
        }
      } catch (err) {
        // Fallback to the basic apt data if fetch fails
        this.selectedAppointment = apt
      }
    },
    async handleSaveRecord(data) {
      this.recordSaving = true
      this.recordToast = { msg: '', type: 'success' }
      try {
        await api.patch(`/api/doctor/appointments/${this.selectedAppointment.id}`, data)
        this.recordToast = { msg: 'Record saved successfully!', type: 'success' }
        // Refresh appointment in modal
        const res = await api.get(`/api/doctor/appointments/${this.selectedAppointment.id}`)
        this.selectedAppointment = { ...res.data.appointment, treatment: res.data.treatment || null }
        // Refresh dashboard counts after a moment
        setTimeout(() => this.fetchDashboardData(), 1000)
      } catch (error) {
        this.recordToast = {
          msg: error.response?.data?.error || 'Failed to save record. Please try again.',
          type: 'error'
        }
      } finally {
        this.recordSaving = false
      }
    },
    generateAvailabilityDays() {
      const days = []
      const today = new Date()
      for (let i = 0; i < 7; i++) {
        const date = new Date(today)
        date.setDate(today.getDate() + i)
        days.push({
          date: date.toISOString().split('T')[0],
          label: date.toLocaleDateString('en-US', { weekday: 'long', month: 'short', day: 'numeric' }),
          available: false
        })
      }
      return days
    },
    async saveAvailabilityToApi() {
      try {
        const availabilityMap = {}
        this.availabilityDays.forEach(d => {
          availabilityMap[d.date] = d.available
        })
        await api.put('/api/doctor/availability', { availability: availabilityMap })
        alert('Availability saved successfully!')
      } catch (error) {
        console.error('Failed to save availability:', error)
        alert(error.response?.data?.error || 'Failed to save availability')
      }
    },
    saveAvailability() {
      this.saveAvailabilityToApi()
    },
    async fetchDashboardData() {
      try {
        const [todayRes, weekRes, allRes, availRes] = await Promise.all([
          api.get('/api/doctor/appointments', { params: { view: 'today', status: 'all' } }),
          api.get('/api/doctor/appointments', { params: { view: 'week', status: 'all' } }),
          api.get('/api/doctor/appointments', { params: { view: 'all', status: 'all' } }),
          api.get('/api/doctor/availability')
        ])

        this.todayAppointments = todayRes.data.appointments || []
        this.weekAppointments = weekRes.data.appointments || []
        this.allAppointments = allRes.data.appointments || []

        const todayApts = this.todayAppointments
        this.todayCount = todayApts.length
        this.completedToday = todayApts.filter(a => a.status === 'completed').length
        this.pendingCount = todayApts.filter(a => a.status === 'booked').length
        this.weekCount = this.weekAppointments.length

        // Load tomorrow appointments
        const tomorrow = new Date()
        tomorrow.setDate(tomorrow.getDate() + 1)
        const tomorrowStr = tomorrow.toISOString().split('T')[0]
        this.tomorrowAppointments = this.weekAppointments.filter(a => a.appointment_dt && a.appointment_dt.startsWith(tomorrowStr))

        // Set up availability days with saved data
        const savedAvailability = availRes.data.availability || {}
        this.availabilityDays = this.generateAvailabilityDays().map(d => ({
          ...d,
          available: savedAvailability[d.date] === true
        }))
      } catch (error) {
        console.error('Failed to fetch doctor dashboard:', error)
        this.availabilityDays = this.generateAvailabilityDays()
      }
    }
  },
  mounted() {
    this.fetchDashboardData()
  }
}
</script>

<style scoped>
.availability-slot {
  border: 1px solid #dee2e6;
  border-radius: 8px;
  padding: 10px;
  text-align: center;
  background: white;
  transition: 0.3s;
}

.availability-slot:hover {
  border-color: #0d6efd;
}

.status-badge {
  font-size: 0.8rem;
  padding: 5px 10px;
  border-radius: 20px;
  color: white;
}
</style>
