<template>
  <div>
    <header class="d-flex justify-content-between align-items-center mb-4">
      <div>
        <h2 class="fw-bold">Appointment Management</h2>
        <p class="text-muted">View and manage all appointments</p>
      </div>
      <div>
        <select class="form-select" v-model="statusFilter" @change="filterAppointments">
          <option value="">All Status</option>
          <option value="booked">Booked</option>
          <option value="completed">Completed</option>
          <option value="cancelled">Cancelled</option>
        </select>
      </div>
    </header>

    <!-- Appointments Table -->
    <div class="card shadow-sm">
      <div class="card-body">
        <div class="table-responsive">
          <table class="table table-hover">
            <thead>
              <tr>
                <th>ID</th>
                <th>Patient</th>
                <th>Doctor</th>
                <th>Date & Time</th>
                <th>Status</th>
                <th>Actions</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="appointment in filteredAppointments" :key="appointment.id">
                <td>{{ appointment.id }}</td>
                <td>{{ appointment.patient_name }}</td>
                <td>{{ appointment.doctor_name }}</td>
                <td>{{ formatDateTime(appointment.appointment_dt) }}</td>
                <td>
                  <span :class="['badge', getStatusClass(appointment.status)]">
                    {{ appointment.status }}
                  </span>
                </td>
                <td>
                  <button class="btn btn-sm btn-outline-primary me-1" @click="viewDetails(appointment)">
                    <i class="bi bi-eye"></i>
                  </button>
                  <button class="btn btn-sm btn-outline-danger" @click="cancelAppointment(appointment.id)">
                    <i class="bi bi-x-circle"></i>
                  </button>
                </td>
              </tr>
              <tr v-if="filteredAppointments.length === 0">
                <td colspan="6" class="text-center text-muted">No appointments found</td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import api from '../axios'

export default {
  name: 'AppointmentManagement',
  data() {
    return {
      appointments: [],
      statusFilter: '',
      filteredAppointments: []
    }
  },
  mounted() {
    this.fetchAppointments()
  },
  methods: {
    async fetchAppointments() {
      try {
        const response = await api.get('/api/admin/appointments')
        this.appointments = response.data.appointments || []
        this.filterAppointments()
      } catch (error) {
        console.error('Failed to fetch appointments:', error)
      }
    },
    filterAppointments() {
      if (this.statusFilter) {
        this.filteredAppointments = this.appointments.filter(
          apt => apt.status === this.statusFilter
        )
      } else {
        this.filteredAppointments = this.appointments
      }
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
    getStatusClass(status) {
      const classes = {
        'booked': 'bg-primary',
        'completed': 'bg-success',
        'cancelled': 'bg-danger'
      }
      return classes[status] || 'bg-secondary'
    },
    viewDetails(appointment) {
      console.log('View appointment:', appointment)
    },
    async cancelAppointment(id) {
      if (confirm('Are you sure you want to cancel this appointment?')) {
        try {
          await api.post(`/api/admin/appointments/${id}/cancel`)
          this.fetchAppointments()
        } catch (error) {
          console.error('Failed to cancel appointment:', error)
          alert(error.response?.data?.error || 'Failed to cancel appointment')
        }
      }
    }
  }
}
</script>

<style scoped>
.table {
  margin-bottom: 0;
}
</style>
