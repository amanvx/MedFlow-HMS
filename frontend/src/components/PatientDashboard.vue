<!-- Patient Dashboard Component -->
<template>
  <div class="dashboard-wrapper">
    <!-- Sidebar -->
    <div class="sidebar">
      <div class="sidebar-header">
        <h5>MediCare Pro</h5>
        <small class="text-muted">Patient Portal</small>
      </div>
      <nav class="sidebar-menu">
        <a @click="currentView = 'dashboard'" :class="['menu-item', {active: currentView === 'dashboard'}]">
          <i class="bi bi-house-door"></i> Dashboard
        </a>
        <a @click="currentView = 'find-doctor'" :class="['menu-item', {active: currentView === 'find-doctor'}]">
          <i class="bi bi-search"></i> Find Doctor
        </a>
        <a @click="currentView = 'appointments'" :class="['menu-item', {active: currentView === 'appointments'}]">
          <i class="bi bi-calendar-check"></i> My Appointments
        </a>
        <a @click="currentView = 'history'" :class="['menu-item', {active: currentView === 'history'}]">
          <i class="bi bi-clock-history"></i> Medical Records
        </a>
        <a @click="currentView = 'billing'" :class="['menu-item', {active: currentView === 'billing'}]">
          <i class="bi bi-receipt"></i> Billing
        </a>
        <a @click="currentView = 'profile'" :class="['menu-item', {active: currentView === 'profile'}]">
          <i class="bi bi-person-circle"></i> My Profile
        </a>
        <a @click="handleLogout" class="menu-item mt-5 text-danger">
          <i class="bi bi-box-arrow-right"></i> Logout
        </a>
      </nav>
    </div>

    <!-- Main Content -->
    <div class="main-content">
      <!-- Dashboard Home View -->
      <div v-if="currentView === 'dashboard'">
        <div class="d-flex justify-content-between align-items-center mb-4">
          <div>
            <h4 class="mb-0">Welcome back, {{ user?.full_name || 'Patient' }}</h4>
            <p class="text-muted small">Last visit: {{ lastVisit || 'No previous visits' }}</p>
          </div>
          <button @click="currentView = 'find-doctor'" class="btn btn-primary btn-sm">
            Book New Appointment
          </button>
        </div>

        <div class="row mb-4">
          <!-- Upcoming Appointments -->
          <div class="col-md-7">
            <div class="content-card">
              <div class="card-header">
                <h6 class="mb-0">Upcoming Appointments</h6>
              </div>
              <div class="card-body">
                <div v-if="upcomingAppointments.length === 0" class="empty-state">
                  <i class="bi bi-calendar-x"></i>
                  <p>No upcoming appointments</p>
                </div>
                <div class="table-responsive" v-else>
                  <table class="table table-sm align-middle">
                    <thead class="table-light">
                      <tr>
                        <th>Doctor</th>
                        <th>Dept</th>
                        <th>Date & Time</th>
                        <th>Status</th>
                      </tr>
                    </thead>
                    <tbody>
                      <tr v-for="apt in upcomingAppointments" :key="apt.id">
                        <td>{{ apt.doctor_name }}</td>
                        <td>{{ apt.department || 'General' }}</td>
                        <td>{{ formatDateTime(apt.appointment_dt) }}</td>
                        <td>
                          <span :class="['badge', `bg-${getStatusColor(apt.status)}`]">
                            {{ apt.status }}
                          </span>
                        </td>
                      </tr>
                    </tbody>
                  </table>
                </div>
              </div>
            </div>
          </div>

          <!-- Available Departments -->
          <div class="col-md-5">
            <div class="content-card">
              <div class="card-header">
                <h6 class="mb-0">Available Departments</h6>
              </div>
              <div class="card-body">
                <div class="d-flex flex-wrap gap-2">
                  <span 
                    v-for="dept in departments" 
                    :key="dept.id" 
                    class="badge border text-dark p-2"
                    style="cursor: pointer"
                    @click="searchByDepartment(dept.id)"
                  >
                    {{ dept.name }}
                  </span>
                </div>
              </div>
            </div>
          </div>
        </div>

        <!-- Doctor Availability Table -->
        <div class="content-card">
          <div class="card-header">
            <h6 class="mb-0">Doctor Availability (Next 7 Days)</h6>
          </div>
          <div class="card-body">
            <div class="table-responsive">
              <table class="table table-sm table-bordered text-center">
                <thead class="table-light">
                  <tr>
                    <th class="text-start">Doctor</th>
                    <th v-for="day in weekDays" :key="day">{{ day }}</th>
                  </tr>
                </thead>
                <tbody>
                  <tr v-for="doctor in doctorsWithAvailability" :key="doctor.id">
                    <td class="text-start">{{ doctor.full_name }}</td>
                    <td v-for="day in weekDays" :key="day">
                      <span :class="['availability-badge', doctor.available[day] ? 'bg-available' : 'bg-unavailable']">
                        {{ doctor.available[day] ? 'A' : 'U' }}
                      </span>
                    </td>
                  </tr>
                </tbody>
              </table>
              <small class="text-muted">A = Available, U = Unavailable</small>
            </div>
          </div>
        </div>

        <!-- Recent Treatment History -->
        <div class="content-card">
          <div class="card-header">
            <h6 class="mb-0">Recent Treatment History</h6>
          </div>
          <div class="card-body">
            <div class="table-responsive">
              <table class="table table-sm">
                <thead class="table-light">
                  <tr>
                    <th>Date</th>
                    <th>Diagnosis</th>
                    <th>Doctor</th>
                    <th>Prescription</th>
                    <th>Action</th>
                  </tr>
                </thead>
                <tbody>
                  <tr v-for="record in recentHistory" :key="record.id">
                    <td>{{ formatDate(record.date) }}</td>
                    <td>{{ record.diagnosis }}</td>
                    <td>{{ record.doctor_name }}</td>
                    <td>{{ record.prescription }}</td>
                    <td>
                      <button class="btn btn-outline-secondary btn-sm py-0" @click="viewRecord(record)">
                        View
                      </button>
                    </td>
                  </tr>
                  <tr v-if="!recentHistory.length">
                    <td colspan="5" class="text-center text-muted">No treatment history</td>
                  </tr>
                </tbody>
              </table>
            </div>
          </div>
        </div>
      </div>

      <!-- Find Doctor View -->
      <div v-if="currentView === 'find-doctor'">
        <FindDoctor @book-appointment="handleBookAppointment" />
      </div>

      <!-- Appointments View -->
      <div v-if="currentView === 'appointments'">
        <AppointmentHistory />
      </div>

      <!-- Medical History View -->
      <div v-if="currentView === 'history'">
        <AppointmentHistory />
      </div>

      <!-- Billing / Invoices View -->
      <div v-if="currentView === 'billing'">
        <div class="d-flex justify-content-between align-items-center mb-4">
          <div>
            <h4 class="fw-bold mb-0">Billing &amp; Invoices</h4>
            <p class="text-muted small mb-0">View and pay your outstanding invoices</p>
          </div>
          <button class="btn btn-outline-secondary btn-sm" @click="exportHistory">
            <i class="bi bi-download me-1"></i> Export History (CSV)
          </button>
        </div>

        <div v-if="billingAlert" :class="['alert', billingAlertType === 'success' ? 'alert-success' : 'alert-danger', 'alert-dismissible']">
          {{ billingAlert }}
          <button type="button" class="btn-close" @click="billingAlert = ''"></button>
        </div>

        <div class="content-card">
          <div class="card-header d-flex justify-content-between align-items-center">
            <h6 class="mb-0">Your Invoices</h6>
            <span class="badge bg-warning text-dark">{{ pendingInvoices }} Pending</span>
          </div>
          <div class="card-body p-0">
            <div v-if="invoicesLoading" class="text-center py-4">
              <div class="spinner-border text-primary spinner-border-sm"></div>
            </div>
            <div v-else-if="invoices.length === 0" class="text-center py-5">
              <i class="bi bi-receipt display-4 text-muted"></i>
              <p class="text-muted mt-2">No invoices found.</p>
            </div>
            <div v-else class="table-responsive">
              <table class="table table-hover align-middle mb-0">
                <thead class="table-light">
                  <tr><th>#</th><th>Date</th><th>Description</th><th>Amount</th><th>Status</th><th>Action</th></tr>
                </thead>
                <tbody>
                  <tr v-for="inv in invoices" :key="inv.id">
                    <td>#{{ inv.id }}</td>
                    <td>{{ formatDate(inv.created_at) }}</td>
                    <td>{{ inv.description || 'Medical Services' }}</td>
                    <td class="fw-semibold">${{ (inv.amount || 0).toFixed(2) }}</td>
                    <td>
                      <span :class="['badge', inv.status === 'paid' ? 'bg-success' : inv.status === 'failed' ? 'bg-danger' : 'bg-warning text-dark']">{{ inv.status }}</span>
                    </td>
                    <td>
                      <button v-if="inv.status !== 'paid'" class="btn btn-success btn-sm" @click="openPayModal(inv)">
                        <i class="bi bi-credit-card me-1"></i> Pay
                      </button>
                      <span v-else class="text-muted small">Paid {{ formatDate(inv.paid_at) }}</span>
                    </td>
                  </tr>
                </tbody>
              </table>
            </div>
          </div>
        </div>

        <!-- Payment Modal -->
        <div v-if="payModal" class="modal fade show d-block" tabindex="-1" style="background:rgba(0,0,0,.5)">
          <div class="modal-dialog">
            <div class="modal-content">
              <div class="modal-header">
                <h5 class="modal-title"><i class="bi bi-credit-card me-2"></i>Pay Invoice #{{ payModal.id }}</h5>
                <button type="button" class="btn-close" @click="payModal = null"></button>
              </div>
              <div class="modal-body">
                <div class="alert alert-info">Amount due: <strong>${{ (payModal.amount || 0).toFixed(2) }}</strong></div>
                <div class="mb-3">
                  <label class="form-label">Card Number</label>
                  <input v-model="payForm.card_number" type="text" class="form-control" placeholder="1234 5678 9012 3456" maxlength="19" />
                </div>
                <div class="row">
                  <div class="col-6 mb-3">
                    <label class="form-label">Expiry (MM/YY)</label>
                    <input v-model="payForm.expiry" type="text" class="form-control" placeholder="MM/YY" maxlength="5" />
                  </div>
                  <div class="col-6 mb-3">
                    <label class="form-label">CVV</label>
                    <input v-model="payForm.cvv" type="text" class="form-control" placeholder="123" maxlength="4" />
                  </div>
                </div>
                <div v-if="payError" class="alert alert-danger py-2">{{ payError }}</div>
              </div>
              <div class="modal-footer">
                <button class="btn btn-secondary" @click="payModal = null">Cancel</button>
                <button class="btn btn-success" @click="submitPayment" :disabled="payLoading">
                  <span v-if="payLoading" class="spinner-border spinner-border-sm me-1"></span>
                  Confirm Payment
                </button>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- Profile View -->
      <div v-if="currentView === 'profile'">
        <div class="d-flex justify-content-between align-items-center mb-4">
          <div>
            <h4 class="fw-bold mb-0">My Profile</h4>
            <p class="text-muted small mb-0">Update your personal information</p>
          </div>
        </div>

        <div v-if="profileAlert" :class="['alert', profileAlertType === 'success' ? 'alert-success' : 'alert-danger', 'alert-dismissible']">
          {{ profileAlert }}
          <button type="button" class="btn-close" @click="profileAlert = ''"></button>
        </div>

        <div class="row g-4">
          <div class="col-md-4">
            <div class="content-card text-center p-4">
              <div class="rounded-circle bg-primary text-white d-flex align-items-center justify-content-center mx-auto mb-3" style="width:80px;height:80px;font-size:2rem;">
                {{ (profileForm.full_name || user?.full_name || 'P').charAt(0).toUpperCase() }}
              </div>
              <h5 class="fw-bold">{{ profileForm.full_name || user?.full_name }}</h5>
              <span class="badge bg-primary">Patient</span>
            </div>
          </div>
          <div class="col-md-8">
            <div class="content-card">
              <div class="card-header"><h6 class="mb-0">Edit Profile</h6></div>
              <div class="card-body">
                <div class="row g-3">
                  <div class="col-12">
                    <label class="form-label">Full Name</label>
                    <input v-model="profileForm.full_name" type="text" class="form-control" placeholder="Your full name" />
                  </div>
                  <div class="col-md-6">
                    <label class="form-label">Contact Number</label>
                    <input v-model="profileForm.contact" type="text" class="form-control" placeholder="Phone number" />
                  </div>
                  <div class="col-md-6">
                    <label class="form-label">Blood Group</label>
                    <select v-model="profileForm.blood_group" class="form-select">
                      <option value="">Select blood group</option>
                      <option v-for="bg in bloodGroups" :key="bg" :value="bg">{{ bg }}</option>
                    </select>
                  </div>
                  <div class="col-12">
                    <label class="form-label">Address</label>
                    <textarea v-model="profileForm.address" class="form-control" rows="2" placeholder="Your address"></textarea>
                  </div>
                  <div class="col-12 d-flex gap-2 justify-content-end">
                    <button class="btn btn-secondary" @click="resetProfileForm">Reset</button>
                    <button class="btn btn-primary" @click="saveProfile" :disabled="profileSaving">
                      <span v-if="profileSaving" class="spinner-border spinner-border-sm me-1"></span>
                      Save Changes
                    </button>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import api from '../axios'
import FindDoctor from './FindDoctor.vue'
import AppointmentHistory from './AppointmentHistory.vue'

export default {
  name: 'PatientDashboard',
  components: { FindDoctor, AppointmentHistory },
  props: ['user'],
  data() {
    return {
      currentView: 'dashboard',
      lastVisit: null,
      upcomingAppointments: [],
      departments: [],
      doctorsWithAvailability: [],
      recentHistory: [],
      weekDays: ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun'],
      // Billing
      invoices: [],
      invoicesLoading: false,
      billingAlert: '',
      billingAlertType: 'success',
      payModal: null,
      payForm: { card_number: '', expiry: '', cvv: '' },
      payError: '',
      payLoading: false,
      // Profile
      profileForm: { full_name: '', contact: '', blood_group: '', address: '' },
      profileSaving: false,
      profileAlert: '',
      profileAlertType: 'success',
      bloodGroups: ['A+', 'A-', 'B+', 'B-', 'AB+', 'AB-', 'O+', 'O-'],
    }
  },
  computed: {
    pendingInvoices() {
      return this.invoices.filter(i => i.status !== 'paid').length
    }
  },
  watch: {
    currentView(val) {
      if (val === 'billing') this.fetchInvoices()
      if (val === 'profile') this.loadProfile()
    }
  },
  methods: {
    handleLogout() {
      this.$emit('logout')
    },
    formatDateTime(dt) {
      if (!dt) return ''
      const date = new Date(dt)
      return date.toLocaleString('en-US', { month: 'short', day: 'numeric', hour: '2-digit', minute: '2-digit' })
    },
    formatDate(dt) {
      if (!dt) return ''
      const date = new Date(dt)
      return date.toLocaleString('en-US', { month: 'short', day: 'numeric', year: 'numeric' })
    },
    getStatusColor(status) {
      const colors = { booked: 'info', completed: 'success', cancelled: 'danger', pending: 'warning' }
      return colors[status] || 'secondary'
    },
    searchByDepartment(deptId) {
      this.currentView = 'find-doctor'
    },
    handleBookAppointment(doctor) {},
    viewRecord(record) {},
    async fetchDashboardData() {
      try {
        const [aptsRes, deptsRes] = await Promise.all([
          api.get('/api/patient/appointments', { params: { upcoming: 'true', status: 'booked' } }),
          api.get('/api/patient/departments')
        ])
        this.upcomingAppointments = aptsRes.data.appointments || []
        this.departments = deptsRes.data.departments || []
      } catch (error) {
        console.error('Failed to fetch patient dashboard data:', error)
      }
    },
    // ── Billing ──────────────────────────────────────────────
    async fetchInvoices() {
      this.invoicesLoading = true
      try {
        const res = await api.get('/api/patient/invoices')
        this.invoices = res.data.invoices || []
      } catch (err) {
        this.billingAlert = 'Failed to load invoices: ' + (err.response?.data?.error || err.message)
        this.billingAlertType = 'error'
      } finally {
        this.invoicesLoading = false
      }
    },
    openPayModal(inv) {
      this.payModal = inv
      this.payForm = { card_number: '', expiry: '', cvv: '' }
      this.payError = ''
    },
    async submitPayment() {
      if (!this.payModal) return
      const { card_number, expiry, cvv } = this.payForm
      const cleaned = card_number.replace(/\s/g, '')
      if (cleaned.length < 13 || cleaned.length > 19) { this.payError = 'Invalid card number.'; return }
      if (!expiry) { this.payError = 'Expiry date required.'; return }
      if (cvv.length < 3) { this.payError = 'Invalid CVV.'; return }
      this.payLoading = true
      this.payError = ''
      try {
        const res = await api.post(`/api/patient/invoices/${this.payModal.id}/pay`, { card_number: cleaned, expiry, cvv })
        this.billingAlert = `Payment successful! Transaction ID: ${res.data.transaction_id}`
        this.billingAlertType = 'success'
        this.payModal = null
        this.fetchInvoices()
      } catch (err) {
        this.payError = err.response?.data?.error || 'Payment failed. Please try again.'
      } finally {
        this.payLoading = false
      }
    },
    async exportHistory() {
      try {
        const res = await api.post('/api/patient/export', {}, { responseType: 'blob' })
        const url = window.URL.createObjectURL(new Blob([res.data]))
        const link = document.createElement('a')
        link.href = url
        link.setAttribute('download', `medical_history_${new Date().toISOString().slice(0,10)}.csv`)
        document.body.appendChild(link)
        link.click()
        link.remove()
        window.URL.revokeObjectURL(url)
      } catch (err) {
        this.billingAlert = 'Export failed: ' + (err.response?.data?.error || err.message)
        this.billingAlertType = 'error'
      }
    },
    // ── Profile ──────────────────────────────────────────────
    loadProfile() {
      const u = this.user || {}
      this.profileForm = {
        full_name: u.full_name || '',
        contact: u.contact || '',
        blood_group: u.blood_group || '',
        address: u.address || '',
      }
      // Try to fetch fresh profile data
      api.get('/api/auth/me').then(res => {
        const u2 = res.data.user || {}
        const p = res.data.profile || {}
        this.profileForm = {
          full_name: u2.full_name || this.profileForm.full_name,
          contact: p.contact || this.profileForm.contact,
          blood_group: p.blood_group || this.profileForm.blood_group,
          address: p.address || this.profileForm.address,
        }
      }).catch(() => {})
    },
    resetProfileForm() {
      this.loadProfile()
    },
    async saveProfile() {
      this.profileSaving = true
      this.profileAlert = ''
      try {
        await api.put('/api/auth/me', {
          full_name: this.profileForm.full_name,
          contact: this.profileForm.contact,
          blood_group: this.profileForm.blood_group,
          address: this.profileForm.address,
        })
        this.profileAlert = 'Profile updated successfully!'
        this.profileAlertType = 'success'
      } catch (err) {
        this.profileAlert = 'Update failed: ' + (err.response?.data?.error || err.message)
        this.profileAlertType = 'error'
      } finally {
        this.profileSaving = false
      }
    },
  },
  mounted() {
    this.fetchDashboardData()
  }
}
</script>

<style scoped>
.availability-badge {
  font-size: 0.7rem;
  padding: 2px 6px;
  border-radius: 4px;
  margin-right: 2px;
  display: inline-block;
}

.bg-available {
  background-color: #28a745;
  color: white;
}

.bg-unavailable {
  background-color: #dc3545;
  color: white;
}
</style>
