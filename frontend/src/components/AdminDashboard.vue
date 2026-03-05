<!-- Admin Dashboard Component -->
<template>
  <div class="dashboard-wrapper">
    <!-- Sidebar -->
    <div class="sidebar">
      <div class="sidebar-header">
        <h4>HMS Admin</h4>
      </div>
      <nav class="sidebar-menu">
        <a @click="currentView = 'dashboard'" :class="['menu-item', {active: currentView === 'dashboard'}]">
          <i class="bi bi-speedometer2"></i> Dashboard
        </a>
        <a @click="currentView = 'doctors'" :class="['menu-item', {active: currentView === 'doctors'}]">
          <i class="bi bi-people"></i> Manage Doctors
        </a>
        <a @click="currentView = 'appointments'" :class="['menu-item', {active: currentView === 'appointments'}]">
          <i class="bi bi-calendar-check"></i> Manage Appointments
        </a>
        <a @click="currentView = 'departments'" :class="['menu-item', {active: currentView === 'departments'}]">
          <i class="bi bi-building"></i> Departments
        </a>
        <a @click="currentView = 'patients'" :class="['menu-item', {active: currentView === 'patients'}]">
          <i class="bi bi-person-lines-fill"></i> Patients
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
        <header class="d-flex justify-content-between align-items-center mb-4 pb-3 border-bottom">
          <div>
            <h2 class="fw-bold">Dashboard Overview</h2>
            <p class="text-muted">Welcome back, {{ user?.full_name || 'Admin' }}</p>
          </div>
          <div class="d-flex align-items-center">
            <div class="me-3 text-end">
              <div class="fw-bold">{{ user?.full_name || 'Admin User' }}</div>
              <small class="text-muted">Administrator</small>
            </div>
            <div class="user-avatar">
              {{ (user?.full_name || 'A').charAt(0).toUpperCase() }}
            </div>
          </div>
        </header>

        <!-- Statistics Cards -->
        <div class="row g-4 mb-4">
          <div class="col-md-3">
            <div class="card stat-card shadow-sm">
              <div class="card-body d-flex align-items-center">
                <div class="icon-box bg-doctors me-3">
                  <i class="bi bi-person-badge"></i>
                </div>
                <div>
                  <h3 class="mb-0 fw-bold">{{ stats.total_doctors || 0 }}</h3>
                  <small class="text-muted">Total Doctors</small>
                </div>
              </div>
            </div>
          </div>
          <div class="col-md-3">
            <div class="card stat-card shadow-sm">
              <div class="card-body d-flex align-items-center">
                <div class="icon-box bg-patients me-3">
                  <i class="bi bi-people"></i>
                </div>
                <div>
                  <h3 class="mb-0 fw-bold">{{ stats.total_patients || 0 }}</h3>
                  <small class="text-muted">Total Patients</small>
                </div>
              </div>
            </div>
          </div>
          <div class="col-md-3">
            <div class="card stat-card shadow-sm">
              <div class="card-body d-flex align-items-center">
                <div class="icon-box bg-appointments me-3">
                  <i class="bi bi-calendar-check"></i>
                </div>
                <div>
                  <h3 class="mb-0 fw-bold">{{ stats.total_appointments || 0 }}</h3>
                  <small class="text-muted">Appointments</small>
                </div>
              </div>
            </div>
          </div>
          <div class="col-md-3">
            <div class="card stat-card shadow-sm">
              <div class="card-body d-flex align-items-center">
                <div class="icon-box bg-alerts me-3">
                  <i class="bi bi-exclamation-triangle"></i>
                </div>
                <div>
                  <h3 class="mb-0 fw-bold">{{ (stats.appointment_breakdown?.booked || 0) }}</h3>
                  <small class="text-muted">Pending</small>
                </div>
              </div>
            </div>
          </div>
        </div>

        <!-- Recent Activity & Quick Actions -->
        <div class="row">
          <div class="col-md-8">
            <div class="content-card">
              <div class="card-header">
                <h5>Recent Activity</h5>
              </div>
              <div class="card-body p-0">
                <table class="table table-hover mb-0">
                  <thead>
                    <tr class="table-light">
                      <th>ID</th>
                      <th>Patient</th>
                      <th>Doctor</th>
                      <th>Date & Time</th>
                      <th>Status</th>
                    </tr>
                  </thead>
                  <tbody>
                    <tr v-for="apt in recentAppointments" :key="apt.id">
                      <td>#{{ apt.id }}</td>
                      <td>{{ apt.patient_name }}</td>
                      <td>{{ apt.doctor_name }}</td>
                      <td>{{ formatDateTime(apt.appointment_dt) }}</td>
                      <td>
                        <span :class="['badge-custom', `badge-${apt.status}`]">
                          {{ apt.status }}
                        </span>
                      </td>
                    </tr>
                    <tr v-if="!recentAppointments.length">
                      <td colspan="5" class="text-center text-muted">No recent appointments</td>
                    </tr>
                  </tbody>
                </table>
              </div>
            </div>
          </div>
          <div class="col-md-4">
            <div class="content-card">
              <div class="card-header">
                <h5>Quick Actions</h5>
              </div>
              <div class="card-body">
                <div class="d-grid gap-2">
                  <button @click="currentView = 'doctors'" class="btn btn-outline-primary text-start p-3">
                    <i class="bi bi-plus-circle me-2"></i> Add New Doctor
                  </button>
                  <button @click="currentView = 'appointments'" class="btn btn-outline-secondary text-start p-3">
                    <i class="bi bi-calendar-check me-2"></i> View All Appointments
                  </button>
                  <button @click="currentView = 'departments'" class="btn btn-outline-info text-start p-3">
                    <i class="bi bi-building me-2"></i> Manage Departments
                  </button>
                  <button @click="currentView = 'patients'" class="btn btn-outline-success text-start p-3">
                    <i class="bi bi-person-lines-fill me-2"></i> View All Patients
                  </button>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- Doctor Management View -->
      <div v-if="currentView === 'doctors'">
        <DoctorManagement />
      </div>

      <!-- Appointment Management View -->
      <div v-if="currentView === 'appointments'">
        <AppointmentManagement />
      </div>

      <!-- Department Management View -->
      <div v-if="currentView === 'departments'">
        <DepartmentManagement />
      </div>

      <!-- Patient Management View -->
      <div v-if="currentView === 'patients'">
        <PatientManagement />
      </div>
    </div>

    <!-- Toast Notifications -->
    <div class="toast-container">
      <div v-for="toast in toasts" :key="toast.id" :class="['toast', `toast-${toast.type}`]">
        <i :class="toast.type === 'success' ? 'bi bi-check-circle-fill text-success' : 'bi bi-x-circle-fill text-danger'"></i>
        <span>{{ toast.message }}</span>
      </div>
    </div>
  </div>
</template>

<script>
import api from '../axios'
import DoctorManagement from './DoctorManagement.vue'
import AppointmentManagement from './AppointmentManagement.vue'
import DepartmentManagement from './DepartmentManagement.vue'
import PatientManagement from './PatientManagement.vue'

export default {
  name: 'AdminDashboard',
  components: {
    DoctorManagement,
    AppointmentManagement,
    DepartmentManagement,
    PatientManagement
  },
  props: ['user'],
  data() {
    return {
      currentView: 'dashboard',
      stats: {},
      recentAppointments: [],
      toasts: []
    }
  },
  methods: {
    handleLogout() {
      this.$emit('logout')
    },
    formatDateTime(dt) {
      if (!dt) return ''
      const date = new Date(dt)
      return date.toLocaleString('en-US', { 
        month: 'short', 
        day: 'numeric',
        year: 'numeric',
        hour: '2-digit', 
        minute: '2-digit' 
      })
    },
    addToast(message, type = 'success') {
      const id = Date.now()
      this.toasts.push({ id, message, type })
      setTimeout(() => {
        this.toasts = this.toasts.filter(t => t.id !== id)
      }, 3000)
    },
    async fetchDashboardData() {
      try {
        const response = await api.get('/api/admin/overview')
        this.stats = response.data.stats || {}
        this.recentAppointments = response.data.recent_appointments || []
      } catch (error) {
        console.error('Failed to fetch dashboard data:', error)
        this.stats = {
          total_doctors: 0,
          total_patients: 0,
          total_appointments: 0,
          appointment_breakdown: { booked: 0 }
        }
      }
    }
  },
  mounted() {
    this.fetchDashboardData()
  }
}
</script>

<style scoped>
/* Component styles will be inherited from main index.html */
</style>
