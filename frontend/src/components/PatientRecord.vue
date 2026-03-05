<!-- Patient Record Component (Doctor View) -->
<template>
  <div class="patient-record">
    <!-- Header bar -->
    <div class="d-flex justify-content-between align-items-center px-3 pt-3 pb-2 border-bottom">
      <h5 class="mb-0 fw-bold">
        <i class="bi bi-clipboard2-pulse me-2 text-primary"></i>
        Consultation Record
      </h5>
      <div class="d-flex gap-2 align-items-center">
        <span v-if="isAlreadyCompleted" class="badge bg-success"><i class="bi bi-check-circle me-1"></i>Completed</span>
        <span v-else class="badge bg-info text-dark"><i class="bi bi-clock me-1"></i>Booked</span>
        <button type="button" class="btn-close" @click="$emit('close')"></button>
      </div>
    </div>

    <!-- Already-completed notice -->
    <div v-if="isAlreadyCompleted" class="alert alert-success mx-3 mt-2 mb-0 py-2 small">
      <i class="bi bi-info-circle me-1"></i>
      This consultation is <strong>completed</strong>. You can still edit and update the treatment record below.
    </div>

    <div class="row p-3">
      <!-- Patient Summary Sidebar -->
      <div class="col-lg-4">
        <div class="content-card mb-4">
          <div class="card-header bg-primary text-white">
            <strong>Patient Summary</strong>
          </div>
          <div class="card-body">
            <div class="text-center mb-3">
              <div class="patient-avatar mx-auto mb-3">
                {{ getInitials(appointment.patient_name) }}
              </div>
              <h5 class="mb-0">{{ appointment.patient_name }}</h5>
              <span class="text-muted small">ID: #{{ appointment.patient_id }}</span>
            </div>
            <hr>
            <div class="row g-2 small">
              <div class="col-6 fw-bold">Appointment:</div>
              <div class="col-6 text-end">{{ formatDate(appointment.appointment_dt) }}</div>
              <div class="col-6 fw-bold">Time:</div>
              <div class="col-6 text-end">{{ formatTime(appointment.appointment_dt) }}</div>
              <div class="col-6 fw-bold">Status:</div>
              <div class="col-6 text-end">
                <span :class="['badge', `bg-${getStatusColor(appointment.status)}`]">
                  {{ appointment.status }}
                </span>
              </div>
            </div>
          </div>
        </div>

        <div class="content-card">
          <div class="card-header bg-light">
            <strong>Visit History</strong>
          </div>
          <div class="card-body p-0" style="max-height: 300px; overflow-y: auto;">
            <div v-if="historyLoading" class="text-center py-3">
              <div class="spinner-border spinner-border-sm text-primary"></div>
            </div>
            <div v-else class="list-group list-group-flush">
              <div
                v-for="visit in visitHistory"
                :key="visit.id"
                class="list-group-item p-3"
              >
                <div class="d-flex justify-content-between">
                  <span class="fw-bold small">{{ formatDate(visit.appointment_dt) }}</span>
                  <span class="badge bg-success small">Completed</span>
                </div>
                <p class="small mb-1 text-muted">{{ visit.treatment?.diagnosis || visit.diagnosis || 'No diagnosis recorded' }}</p>
              </div>
              <div v-if="!visitHistory.length" class="list-group-item text-center text-muted small py-3">
                No previous visits
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- Consultation Form -->
      <div class="col-lg-8">
        <div class="content-card">
          <div class="card-header bg-white d-flex justify-content-between align-items-center">
            <strong>{{ isAlreadyCompleted ? 'Treatment Record (Editable)' : 'Current Consultation Session' }}</strong>
            <small v-if="appointment.treatment" class="text-success"><i class="bi bi-check-circle me-1"></i>Treatment on file</small>
          </div>
          <div class="card-body">
            <form @submit.prevent="saveRecord">
              <div class="mb-3">
                <label class="form-label fw-bold">Symptoms Reported</label>
                <textarea 
                  class="form-control" 
                  rows="2" 
                  v-model="form.symptoms"
                  placeholder="Enter symptoms described by patient..."
                ></textarea>
              </div>

              <div class="mb-3">
                <label class="form-label fw-bold">Diagnosis</label>
                <textarea 
                  class="form-control" 
                  rows="3" 
                  v-model="form.diagnosis"
                  placeholder="Enter clinical diagnosis..."
                  required
                ></textarea>
              </div>

              <div class="mb-3">
                <label class="form-label fw-bold">Prescription & Medication</label>
                <table class="table table-bordered table-sm">
                  <thead>
                    <tr class="table-light">
                      <th>Medicine Name</th>
                      <th>Dosage</th>
                      <th>Duration</th>
                      <th width="50"></th>
                    </tr>
                  </thead>
                  <tbody>
                    <tr v-for="(med, index) in form.medications" :key="index">
                      <td>
                        <input 
                          type="text" 
                          class="form-control form-control-sm" 
                          v-model="med.name"
                          placeholder="Medicine name"
                        >
                      </td>
                      <td>
                        <input 
                          type="text" 
                          class="form-control form-control-sm" 
                          v-model="med.dosage"
                          placeholder="1-0-1"
                        >
                      </td>
                      <td>
                        <input 
                          type="text" 
                          class="form-control form-control-sm" 
                          v-model="med.duration"
                          placeholder="7 Days"
                        >
                      </td>
                      <td>
                        <button 
                          type="button"
                          class="btn btn-sm btn-outline-danger"
                          @click="removeMedication(index)"
                        >
                          &times;
                        </button>
                      </td>
                    </tr>
                  </tbody>
                </table>
                <button 
                  type="button" 
                  class="btn btn-sm btn-outline-primary"
                  @click="addMedication"
                >
                  <i class="bi bi-plus-circle me-2"></i>Add Medicine
                </button>
              </div>

              <div class="mb-3">
                <label class="form-label fw-bold">Advice / Notes</label>
                <textarea 
                  class="form-control" 
                  rows="2" 
                  v-model="form.notes"
                  placeholder="Dietary advice, follow-up instructions..."
                ></textarea>
              </div>

              <div class="mb-3">
                <label class="form-label fw-bold">Next Visit (Optional)</label>
                <input 
                  type="date" 
                  class="form-control" 
                  v-model="form.nextVisit"
                >
              </div>

              <div class="form-check mb-4">
                <input 
                  class="form-check-input" 
                  type="checkbox" 
                  v-model="markComplete"
                  id="markComplete"
                >
                <label class="form-check-label fw-bold text-success" for="markComplete">
                  Mark this visit as completed
                </label>
              </div>

              <div class="d-flex gap-2">
                <button type="submit" class="btn btn-primary px-4" :disabled="saving">
                  <span v-if="saving" class="spinner-border spinner-border-sm me-2"></span>
                  <i v-else class="bi bi-save me-2"></i>
                  {{ saving ? 'Saving...' : (isAlreadyCompleted ? 'Update Record' : 'Save & Complete') }}
                </button>
                <button type="button" class="btn btn-outline-secondary" @click="$emit('close')">
                  Cancel
                </button>
              </div>
            </form>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import api from '../axios'

export default {
  name: 'PatientRecord',
  props: {
    appointment: { type: Object, required: true },
    saving: { type: Boolean, default: false }
  },
  data() {
    return {
      form: {
        symptoms: '',
        diagnosis: '',
        medications: [{ name: '', dosage: '', duration: '' }],
        notes: '',
        nextVisit: ''
      },
      markComplete: false,
      visitHistory: [],
      historyLoading: false
    }
  },
  computed: {
    isAlreadyCompleted() {
      return this.appointment.status === 'completed'
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
    getStatusColor(status) {
      const colors = { booked: 'info', completed: 'success', cancelled: 'danger' }
      return colors[status] || 'secondary'
    },
    addMedication() {
      this.form.medications.push({ name: '', dosage: '', duration: '' })
    },
    removeMedication(index) {
      if (this.form.medications.length > 1) {
        this.form.medications.splice(index, 1)
      }
    },
    parsePrescription(prescriptionStr) {
      if (!prescriptionStr) return [{ name: '', dosage: '', duration: '' }]
      const lines = prescriptionStr.split('; ').filter(Boolean)
      if (!lines.length) return [{ name: '', dosage: '', duration: '' }]
      return lines.map(line => {
        const parts = line.split(' - ')
        return {
          name: parts[0] || '',
          dosage: parts[1] || '',
          duration: parts[2] || ''
        }
      })
    },
    prefillFromTreatment() {
      const t = this.appointment.treatment
      if (t) {
        this.form.diagnosis = t.diagnosis || ''
        this.form.notes = t.notes || ''
        this.form.nextVisit = t.next_visit_dt ? t.next_visit_dt.split('T')[0] : ''
        this.form.medications = this.parsePrescription(t.prescription)
      }
      // Pre-fill symptoms from appointment notes (reason for visit)
      this.form.symptoms = this.appointment.notes || ''
      // Auto-check "mark complete" if already completed or if there's existing treatment
      if (this.isAlreadyCompleted || t) {
        this.markComplete = true
      }
    },
    async fetchVisitHistory() {
      if (!this.appointment.patient_id) return
      this.historyLoading = true
      try {
        const res = await api.get(`/api/doctor/patients/${this.appointment.patient_id}/history`)
        // Exclude the current appointment from history
        this.visitHistory = (res.data.history || [])
          .filter(h => h.id !== this.appointment.id)
          .slice(0, 5)
      } catch (err) {
        this.visitHistory = []
      } finally {
        this.historyLoading = false
      }
    },
    saveRecord() {
      const prescription = this.form.medications
        .filter(m => m.name.trim())
        .map(m => `${m.name} - ${m.dosage} - ${m.duration}`)
        .join('; ')

      const data = {
        status: this.markComplete ? 'completed' : this.appointment.status,
        notes: this.form.symptoms,        // symptoms → appointment.notes
        diagnosis: this.form.diagnosis,
        prescription: prescription,
        treatment_notes: this.form.notes,
        next_visit_dt: this.form.nextVisit || null
      }
      this.$emit('save', data)
    }
  },
  mounted() {
    this.prefillFromTreatment()
    this.fetchVisitHistory()
  },
  watch: {
    appointment: {
      deep: true,
      handler() {
        this.prefillFromTreatment()
      }
    }
  }
}
</script>

<style scoped>
.patient-avatar {
  width: 80px;
  height: 80px;
  border-radius: 50%;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 2rem;
  font-weight: 700;
}
</style>
