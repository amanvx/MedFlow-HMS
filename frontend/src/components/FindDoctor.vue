<!-- Find Doctor Component -->
<template>
  <div>
    <div class="d-flex justify-content-between align-items-center mb-4">
      <div>
        <h2>Find a Specialist</h2>
        <button class="btn btn-sm btn-outline-secondary mt-2" @click="$emit('back')">
          <i class="bi bi-arrow-left"></i> Back to Dashboard
        </button>
      </div>
    </div>

    <!-- Search Header -->
    <div class="search-header content-card mb-4">
      <div class="row g-3">
        <div class="col-md-5">
          <label class="form-label fw-bold">Search</label>
          <div class="input-group">
            <span class="input-group-text bg-white">
              <i class="bi bi-search"></i>
            </span>
            <input 
              type="text" 
              class="form-control border-start-0" 
              placeholder="Doctor name or specialization..."
              v-model="searchQuery"
              @input="performSearch"
            >
          </div>
        </div>
        <div class="col-md-3">
          <label class="form-label fw-bold">Department</label>
          <select class="form-select" v-model="selectedDepartment" @change="performSearch">
            <option value="">All Departments</option>
            <option v-for="dept in departments" :key="dept.id" :value="dept.id">
              {{ dept.name }}
            </option>
          </select>
        </div>
        <div class="col-md-4">
          <label class="form-label fw-bold">Availability</label>
          <div class="d-flex gap-2">
            <button 
              :class="['btn btn-outline-primary btn-sm', {active: availFilter === 'any'}]"
              @click="availFilter = 'any'; performSearch()"
            >
              Any Day
            </button>
            <button 
              :class="['btn btn-outline-primary btn-sm', {active: availFilter === 'today'}]"
              @click="availFilter = 'today'; performSearch()"
            >
              Today
            </button>
            <button 
              :class="['btn btn-outline-primary btn-sm', {active: availFilter === 'tomorrow'}]"
              @click="availFilter = 'tomorrow'; performSearch()"
            >
              Tomorrow
            </button>
          </div>
        </div>
      </div>
    </div>

    <!-- Results -->
    <div class="row mb-3">
      <div class="col-12">
        <div v-if="bookingSuccess" class="alert alert-success alert-dismissible">
          <i class="bi bi-check-circle me-2"></i>Appointment booked successfully!
        </div>
        <div v-if="bookingError" class="alert alert-danger">
          <i class="bi bi-x-circle me-2"></i>{{ bookingError }}
        </div>
        <p class="text-muted">Showing {{ filteredDoctors.length }} doctors</p>
      </div>
    </div>

    <!-- Doctor Cards -->
    <div class="row">
      <div class="col-md-6 col-lg-4" v-for="doctor in filteredDoctors" :key="doctor.id">
        <div class="doctor-card card mb-4">
          <div class="card-body">
            <div class="d-flex align-items-center mb-3">
              <div class="doctor-avatar me-3">
                {{ getInitials(doctor.full_name) }}
              </div>
              <div>
                <h5 class="card-title mb-0">{{ doctor.full_name }}</h5>
                <p class="text-primary mb-0">{{ doctor.specialization }}</p>
                <small class="text-muted">{{ doctor.department_name }}</small>
              </div>
            </div>

            <div class="mb-3">
              <h6 class="small fw-bold">Weekly Availability:</h6>
              <div class="d-flex flex-wrap gap-1">
                <span 
                  v-for="(avail, day) in doctor.availability" 
                  :key="day"
                  :class="['availability-badge', avail ? 'avail-yes' : 'avail-no']"
                >
                  {{ day.substr(0, 3) }}
                </span>
              </div>
            </div>

            <div class="d-grid">
              <button class="btn btn-primary" @click="bookDoctor(doctor)">
                <i class="bi bi-calendar-plus me-2"></i>Book Appointment
              </button>
            </div>
          </div>
        </div>
      </div>

      <div v-if="filteredDoctors.length === 0" class="col-12">
        <div class="empty-state">
          <i class="bi bi-search"></i>
          <p>No doctors found matching your criteria</p>
        </div>
      </div>
    </div>

    <!-- Booking Modal -->
    <div v-if="showBookingModal" class="modal-overlay" @click.self="showBookingModal = false">
      <div class="modal-content" style="max-width: 700px;">
        <div class="modal-header">
          <h5>Book Appointment with {{ selectedDoctor?.full_name }}</h5>
          <button type="button" class="btn-close" @click="showBookingModal = false"></button>
        </div>
        <div class="modal-body">
          <BookAppointment 
            :doctor="selectedDoctor"
            @confirm="handleBookingConfirm"
            @cancel="showBookingModal = false"
          />
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import api from '../axios'
import BookAppointment from './BookAppointment.vue'

export default {
  name: 'FindDoctor',
  components: { BookAppointment },
  data() {
    return {
      searchQuery: '',
      selectedDepartment: '',
      availFilter: 'any',
      departments: [],
      doctors: [],
      filteredDoctors: [],
      showBookingModal: false,
      selectedDoctor: null,
      bookingSuccess: false,
      bookingError: ''
    }
  },
  methods: {
    performSearch() {
      let results = this.doctors

      if (this.searchQuery) {
        const query = this.searchQuery.toLowerCase()
        results = results.filter(d =>
          (d.full_name || '').toLowerCase().includes(query) ||
          (d.specialization || '').toLowerCase().includes(query)
        )
      }

      if (this.selectedDepartment) {
        results = results.filter(d => d.department_id == this.selectedDepartment)
      }

      this.filteredDoctors = results
    },
    getInitials(name) {
      if (!name) return '?'
      return name.split(' ').map(n => n[0]).join('').toUpperCase().substr(0, 2)
    },
    bookDoctor(doctor) {
      this.selectedDoctor = doctor
      this.showBookingModal = true
      this.bookingSuccess = false
      this.bookingError = ''
    },
    async handleBookingConfirm(booking) {
      try {
        await api.post('/api/patient/appointments', booking)
        this.showBookingModal = false
        this.bookingSuccess = true
        this.$emit('book-confirmed', booking)
        setTimeout(() => { this.bookingSuccess = false }, 4000)
      } catch (error) {
        this.bookingError = error.response?.data?.error || 'Booking failed'
      }
    },
    async fetchDoctors() {
      try {
        const response = await api.get('/api/patient/doctors')
        this.doctors = response.data.doctors || []
        this.filteredDoctors = this.doctors
      } catch (error) {
        console.error('Failed to fetch doctors:', error)
      }
    },
    async fetchDepartments() {
      try {
        const response = await api.get('/api/patient/departments')
        this.departments = response.data.departments || []
      } catch (error) {
        console.error('Failed to fetch departments:', error)
      }
    }
  },
  mounted() {
    this.fetchDoctors()
    this.fetchDepartments()
  }
}
</script>

<style scoped>
.doctor-card {
  background: white;
  border: none;
  border-radius: 12px;
  transition: transform 0.2s, box-shadow 0.2s;
}

.doctor-card:hover {
  transform: translateY(-5px);
  box-shadow: 0 10px 20px rgba(0,0,0,0.1);
}

.doctor-avatar {
  width: 70px;
  height: 70px;
  border-radius: 50%;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 1.5rem;
  font-weight: 700;
}

.availability-badge {
  font-size: 0.75rem;
  padding: 4px 8px;
  border-radius: 4px;
  font-weight: 600;
}

.avail-yes {
  background-color: #d4edda;
  color: #155724;
}

.avail-no {
  background-color: #f8d7da;
  color: #721c24;
}

.search-header {
  background: white;
  padding: 25px;
  border-radius: 12px;
  box-shadow: 0 2px 10px rgba(0,0,0,0.05);
}
</style>
