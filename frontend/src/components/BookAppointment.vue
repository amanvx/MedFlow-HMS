<!-- Book Appointment Component -->
<template>
  <div class="booking-wizard">
    <!-- Step Indicator -->
    <div class="step-indicator mb-4">
      <div :class="['step', {active: step >= 1}]">1. Doctor Info</div>
      <div :class="['step', {active: step >= 2}]">2. Choose Slot</div>
      <div :class="['step', {active: step >= 3}]">3. Confirmation</div>
    </div>

    <!-- Step 1: Doctor Information -->
    <div v-if="step === 1">
      <div class="row">
        <div class="col-md-4">
          <div class="doctor-card mb-3">
            <div class="text-center">
              <div class="doctor-avatar mx-auto mb-3">
                {{ getInitials(doctor.full_name) }}
              </div>
              <h6 class="mb-0">{{ doctor.full_name }}</h6>
              <small class="text-muted">{{ doctor.specialization }}</small>
              <div class="mt-2">
                <span class="badge bg-info text-dark">{{ doctor.department_name }}</span>
              </div>
              <hr>
              <div class="text-start small">
                <strong>Specialization:</strong> {{ doctor.specialization }}<br>
                <strong>Department:</strong> {{ doctor.department_name }}
              </div>
            </div>
          </div>
        </div>
        <div class="col-md-8">
          <p class="text-muted">Please review doctor information and proceed to select appointment date and time.</p>
          <button class="btn btn-primary" @click="step = 2">
            Next: Choose Date & Time <i class="bi bi-arrow-right ms-2"></i>
          </button>
        </div>
      </div>
    </div>

    <!-- Step 2: Date & Time Selection -->
    <div v-if="step === 2">
      <div class="row">
        <div class="col-md-12">
          <h6 class="mb-3">Select Date & Time</h6>
          
          <!-- Date Selector -->
          <div class="d-flex gap-2 mb-4 overflow-auto pb-2">
            <div 
              v-for="(date, index) in availableDates" 
              :key="index"
              :class="['date-item', {active: selectedDate === date.value}]"
              @click="selectDate(date.value)"
            >
              <strong>{{ date.label }}</strong><br>
              <small>{{ date.day }}</small>
            </div>
          </div>

          <!-- Time Slots -->
          <div v-if="selectedDate">
            <h6>Available Slots</h6>
            
            <div class="mb-4">
              <p class="small text-muted mb-1">Morning</p>
              <button 
                v-for="slot in morningSlots" 
                :key="slot"
                :class="['btn slot-btn', selectedTime === slot ? 'btn-primary' : 'btn-outline-primary']"
                @click="selectedTime = slot"
                :disabled="!isSlotAvailable(slot)"
              >
                {{ slot }}
              </button>
            </div>

            <div class="mb-4">
              <p class="small text-muted mb-1">Afternoon</p>
              <button 
                v-for="slot in afternoonSlots" 
                :key="slot"
                :class="['btn slot-btn', selectedTime === slot ? 'btn-primary' : 'btn-outline-primary']"
                @click="selectedTime = slot"
                :disabled="!isSlotAvailable(slot)"
              >
                {{ slot }}
              </button>
            </div>

            <!-- Reason for Visit -->
            <div class="mb-3">
              <label class="form-label small">Reason for Visit (Optional)</label>
              <textarea 
                class="form-control form-control-sm" 
                rows="2" 
                v-model="notes"
                placeholder="Briefly describe your symptoms..."
              ></textarea>
            </div>

            <div class="d-flex gap-2">
              <button class="btn btn-outline-secondary" @click="step = 1">
                <i class="bi bi-arrow-left me-2"></i>Back
              </button>
              <button 
                class="btn btn-primary" 
                @click="step = 3"
                :disabled="!selectedTime"
              >
                Next: Confirm <i class="bi bi-arrow-right ms-2"></i>
              </button>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Step 3: Confirmation -->
    <div v-if="step === 3">
      <div class="alert alert-info">
        <h6>Appointment Details</h6>
        <hr>
        <div class="row">
          <div class="col-6"><strong>Doctor:</strong></div>
          <div class="col-6">{{ doctor.full_name }}</div>
          <div class="col-6"><strong>Date:</strong></div>
          <div class="col-6">{{ formatDate(selectedDate) }}</div>
          <div class="col-6"><strong>Time:</strong></div>
          <div class="col-6">{{ selectedTime }}</div>
          <div class="col-6"><strong>Reason:</strong></div>
          <div class="col-6">{{ notes || 'General Checkup' }}</div>
        </div>
      </div>

      <div class="form-check mb-3">
        <input class="form-check-input" type="checkbox" v-model="agreeTerms" id="agreeTerms">
        <label class="form-check-label" for="agreeTerms">
          I confirm the appointment details are correct
        </label>
      </div>

      <div class="d-flex gap-2">
        <button class="btn btn-outline-secondary" @click="step = 2">
          <i class="bi bi-arrow-left me-2"></i>Back
        </button>
        <button 
          class="btn btn-success btn-book w-100" 
          @click="confirmBooking"
          :disabled="!agreeTerms || loading"
        >
          <span v-if="loading" class="spinner-border spinner-border-sm me-2"></span>
          {{ loading ? 'Booking...' : 'Confirm Appointment' }}
        </button>
      </div>
    </div>
  </div>
</template>

<script>
export default {
  name: 'BookAppointment',
  props: ['doctor'],
  data() {
    return {
      step: 1,
      selectedDate: null,
      selectedTime: null,
      notes: '',
      agreeTerms: false,
      loading: false,
      availableDates: [],
      morningSlots: ['09:00 AM', '10:00 AM', '11:00 AM', '11:30 AM'],
      afternoonSlots: ['02:00 PM', '03:00 PM', '04:00 PM', '05:00 PM'],
      bookedSlots: []
    }
  },
  methods: {
    getInitials(name) {
      return name.split(' ').map(n => n[0]).join('').toUpperCase().substr(0, 2)
    },
    selectDate(date) {
      this.selectedDate = date
      this.selectedTime = null
      // Fetch booked slots for this date
    },
    isSlotAvailable(slot) {
      // Check if slot is already booked
      return !this.bookedSlots.includes(`${this.selectedDate} ${slot}`)
    },
    formatDate(dateStr) {
      if (!dateStr) return ''
      const date = new Date(dateStr)
      return date.toLocaleDateString('en-US', { month: 'long', day: 'numeric', year: 'numeric' })
    },
    async confirmBooking() {
      this.loading = true
      try {
        const booking = {
          doctor_id: this.doctor.id,
          appointment_dt: `${this.selectedDate}T${this.convertTo24Hour(this.selectedTime)}`,
          notes: this.notes
        }
        this.$emit('confirm', booking)
      } catch (error) {
        console.error('Booking failed:', error)
      } finally {
        this.loading = false
      }
    },
    convertTo24Hour(time) {
      const [t, period] = time.split(' ')
      let [hours, minutes] = t.split(':')
      hours = parseInt(hours)
      if (period === 'PM' && hours !== 12) hours += 12
      if (period === 'AM' && hours === 12) hours = 0
      return `${hours.toString().padStart(2, '0')}:${minutes}:00`
    },
    generateAvailableDates() {
      const dates = []
      const today = new Date()
      for (let i = 0; i < 7; i++) {
        const date = new Date(today)
        date.setDate(today.getDate() + i)
        dates.push({
          value: date.toISOString().split('T')[0],
          label: date.toLocaleDateString('en-US', { month: 'short', day: 'numeric' }),
          day: date.toLocaleDateString('en-US', { weekday: 'short' })
        })
      }
      this.availableDates = dates
    }
  },
  mounted() {
    this.generateAvailableDates()
  }
}
</script>

<style scoped>
.step-indicator {
  display: flex;
  justify-content: space-between;
}

.step {
  flex: 1;
  text-align: center;
  padding: 10px;
  border-bottom: 3px solid #dee2e6;
  color: #6c757d;
  font-weight: 600;
}

.step.active {
  border-color: #007bff;
  color: #007bff;
}

.date-item {
  cursor: pointer;
  padding: 10px 15px;
  border: 1px solid #dee2e6;
  border-radius: 5px;
  text-align: center;
  min-width: 80px;
  background: #fff;
  transition: all 0.2s;
}

.date-item.active {
  background: #007bff;
  color: white;
  border-color: #007bff;
}

.date-item:hover {
  border-color: #007bff;
}

.slot-btn {
  margin: 5px;
  min-width: 100px;
  font-size: 0.85rem;
}

.btn-book {
  background-color: #28a745;
  color: white;
  font-weight: bold;
}

.doctor-avatar {
  width: 80px;
  height: 80px;
  border-radius: 50%;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 1.8rem;
  font-weight: 700;
}
</style>
