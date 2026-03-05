<!-- Patient Management Component (Admin) -->
<template>
  <div>
    <div class="d-flex justify-content-between align-items-center mb-4">
      <div>
        <h4 class="fw-bold mb-0">Patient Management</h4>
        <p class="text-muted small mb-0">Search and manage registered patients</p>
      </div>
    </div>

    <!-- Alert -->
    <div v-if="alertMsg" :class="['alert', alertType === 'success' ? 'alert-success' : 'alert-danger', 'alert-dismissible']" role="alert">
      {{ alertMsg }}
      <button type="button" class="btn-close" @click="alertMsg = ''"></button>
    </div>

    <!-- Search Bar -->
    <div class="content-card mb-4">
      <div class="card-body">
        <div class="row g-2 align-items-end">
          <div class="col-md-8">
            <label class="form-label fw-semibold small">Search Patients</label>
            <div class="input-group">
              <span class="input-group-text"><i class="bi bi-search"></i></span>
              <input
                v-model="searchQuery"
                type="text"
                class="form-control"
                placeholder="Search by name or email..."
                @keyup.enter="fetchPatients"
              />
              <button class="btn btn-primary" @click="fetchPatients">Search</button>
              <button class="btn btn-outline-secondary" @click="clearSearch">Clear</button>
            </div>
          </div>
          <div class="col-md-4 text-end">
            <span class="text-muted small">Total: <strong>{{ pagination.total || 0 }}</strong> patients</span>
          </div>
        </div>
      </div>
    </div>

    <!-- Patients Table -->
    <div class="content-card">
      <div class="card-body p-0">
        <div v-if="loading" class="text-center py-5">
          <div class="spinner-border text-primary" role="status"></div>
          <p class="text-muted mt-2">Loading patients...</p>
        </div>

        <div v-else-if="patients.length === 0" class="text-center py-5">
          <i class="bi bi-people display-4 text-muted"></i>
          <p class="text-muted mt-2">{{ searchQuery ? 'No patients found matching your search.' : 'No patients registered yet.' }}</p>
        </div>

        <div v-else class="table-responsive">
          <table class="table table-hover align-middle mb-0">
            <thead class="table-light">
              <tr>
                <th>#</th>
                <th>Patient</th>
                <th>Contact</th>
                <th>Blood Group</th>
                <th>Age / DOB</th>
                <th>Registered</th>
                <th>Status</th>
                <th>Actions</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="(pat, idx) in patients" :key="pat.id">
                <td class="text-muted small">{{ (pagination.page - 1) * pagination.per_page + idx + 1 }}</td>
                <td>
                  <div class="d-flex align-items-center gap-2">
                    <div class="rounded-circle bg-primary text-white d-flex align-items-center justify-content-center" style="width:36px;height:36px;font-size:.85rem;">
                      {{ (pat.full_name || 'P').charAt(0).toUpperCase() }}
                    </div>
                    <div>
                      <div class="fw-semibold">{{ pat.full_name || '—' }}</div>
                      <small class="text-muted">{{ pat.email }}</small>
                    </div>
                  </div>
                </td>
                <td>{{ pat.contact || '—' }}</td>
                <td>
                  <span v-if="pat.blood_group" class="badge bg-danger">{{ pat.blood_group }}</span>
                  <span v-else class="text-muted">—</span>
                </td>
                <td>
                  <span v-if="pat.date_of_birth">{{ formatDate(pat.date_of_birth) }}</span>
                  <span v-else class="text-muted">—</span>
                </td>
                <td>{{ formatDate(pat.created_at) }}</td>
                <td>
                  <span :class="['badge', pat.is_active !== false ? 'bg-success' : 'bg-secondary']">
                    {{ pat.is_active !== false ? 'Active' : 'Inactive' }}
                  </span>
                </td>
                <td>
                  <div class="d-flex gap-1">
                    <button class="btn btn-outline-info btn-sm" @click="viewPatient(pat)" title="View details">
                      <i class="bi bi-eye"></i>
                    </button>
                    <button
                      v-if="pat.is_active !== false"
                      class="btn btn-outline-danger btn-sm"
                      @click="confirmDeactivate(pat)"
                      title="Deactivate patient"
                    >
                      <i class="bi bi-person-dash"></i>
                    </button>
                    <span v-else class="text-muted small fst-italic align-self-center">Deactivated</span>
                  </div>
                </td>
              </tr>
            </tbody>
          </table>
        </div>

        <!-- Pagination -->
        <div v-if="pagination.pages > 1" class="d-flex justify-content-between align-items-center px-3 py-2 border-top">
          <small class="text-muted">
            Showing {{ (pagination.page - 1) * pagination.per_page + 1 }}–{{ Math.min(pagination.page * pagination.per_page, pagination.total) }} of {{ pagination.total }}
          </small>
          <div class="d-flex gap-1">
            <button class="btn btn-sm btn-outline-secondary" :disabled="!pagination.has_prev" @click="changePage(pagination.page - 1)">
              <i class="bi bi-chevron-left"></i> Prev
            </button>
            <button class="btn btn-sm btn-outline-secondary" :disabled="!pagination.has_next" @click="changePage(pagination.page + 1)">
              Next <i class="bi bi-chevron-right"></i>
            </button>
          </div>
        </div>
      </div>
    </div>

    <!-- Patient Details Modal -->
    <div v-if="selectedPatient" class="modal fade show d-block" tabindex="-1" style="background:rgba(0,0,0,.5)">
      <div class="modal-dialog modal-lg">
        <div class="modal-content">
          <div class="modal-header">
            <h5 class="modal-title"><i class="bi bi-person-circle me-2"></i>{{ selectedPatient.full_name }}</h5>
            <button type="button" class="btn-close" @click="selectedPatient = null"></button>
          </div>
          <div class="modal-body">
            <div class="row g-3">
              <div class="col-md-6">
                <label class="form-label fw-semibold small text-muted">FULL NAME</label>
                <p class="mb-0">{{ selectedPatient.full_name || '—' }}</p>
              </div>
              <div class="col-md-6">
                <label class="form-label fw-semibold small text-muted">EMAIL</label>
                <p class="mb-0">{{ selectedPatient.email || '—' }}</p>
              </div>
              <div class="col-md-4">
                <label class="form-label fw-semibold small text-muted">CONTACT</label>
                <p class="mb-0">{{ selectedPatient.contact || '—' }}</p>
              </div>
              <div class="col-md-4">
                <label class="form-label fw-semibold small text-muted">BLOOD GROUP</label>
                <p class="mb-0">{{ selectedPatient.blood_group || '—' }}</p>
              </div>
              <div class="col-md-4">
                <label class="form-label fw-semibold small text-muted">DATE OF BIRTH</label>
                <p class="mb-0">{{ selectedPatient.date_of_birth ? formatDate(selectedPatient.date_of_birth) : '—' }}</p>
              </div>
              <div class="col-12">
                <label class="form-label fw-semibold small text-muted">ADDRESS</label>
                <p class="mb-0">{{ selectedPatient.address || '—' }}</p>
              </div>
              <div class="col-md-6">
                <label class="form-label fw-semibold small text-muted">REGISTERED ON</label>
                <p class="mb-0">{{ formatDate(selectedPatient.created_at) }}</p>
              </div>
              <div class="col-md-6">
                <label class="form-label fw-semibold small text-muted">STATUS</label>
                <p class="mb-0">
                  <span :class="['badge', selectedPatient.is_active !== false ? 'bg-success' : 'bg-secondary']">
                    {{ selectedPatient.is_active !== false ? 'Active' : 'Inactive' }}
                  </span>
                </p>
              </div>
            </div>

            <!-- Appointments -->
            <div v-if="patientAppointments.length" class="mt-4">
              <h6 class="fw-semibold border-bottom pb-2">Appointment History ({{ patientAppointments.length }})</h6>
              <div class="table-responsive">
                <table class="table table-sm table-bordered">
                  <thead class="table-light">
                    <tr><th>Date</th><th>Doctor</th><th>Status</th></tr>
                  </thead>
                  <tbody>
                    <tr v-for="apt in patientAppointments.slice(0, 5)" :key="apt.id">
                      <td>{{ formatDateTime(apt.appointment_dt) }}</td>
                      <td>{{ apt.doctor_name || '—' }}</td>
                      <td><span :class="['badge', statusBadge(apt.status)]">{{ apt.status }}</span></td>
                    </tr>
                  </tbody>
                </table>
              </div>
            </div>
          </div>
          <div class="modal-footer">
            <button type="button" class="btn btn-secondary" @click="selectedPatient = null">Close</button>
            <button
              v-if="selectedPatient.is_active !== false"
              class="btn btn-danger"
              @click="confirmDeactivate(selectedPatient)"
            >
              <i class="bi bi-person-dash me-1"></i> Deactivate Patient
            </button>
          </div>
        </div>
      </div>
    </div>

    <!-- Deactivate Confirm Modal -->
    <div v-if="patientToDeactivate" class="modal fade show d-block" tabindex="-1" style="background:rgba(0,0,0,.5)">
      <div class="modal-dialog">
        <div class="modal-content">
          <div class="modal-header bg-danger text-white">
            <h5 class="modal-title"><i class="bi bi-exclamation-triangle me-2"></i>Deactivate Patient</h5>
            <button type="button" class="btn-close btn-close-white" @click="patientToDeactivate = null"></button>
          </div>
          <div class="modal-body">
            <p>Are you sure you want to deactivate <strong>{{ patientToDeactivate.full_name }}</strong>?</p>
            <p class="text-muted small">This will prevent them from logging in. This action can be reversed by a database admin.</p>
          </div>
          <div class="modal-footer">
            <button type="button" class="btn btn-secondary" @click="patientToDeactivate = null">Cancel</button>
            <button class="btn btn-danger" @click="deactivatePatient" :disabled="actionLoading">
              <span v-if="actionLoading" class="spinner-border spinner-border-sm me-1"></span>
              Deactivate
            </button>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import api from '../axios'

export default {
  name: 'PatientManagement',
  data() {
    return {
      patients: [],
      loading: false,
      actionLoading: false,
      searchQuery: '',
      pagination: { page: 1, per_page: 20, total: 0, pages: 0, has_next: false, has_prev: false },
      alertMsg: '',
      alertType: 'success',
      selectedPatient: null,
      patientAppointments: [],
      patientToDeactivate: null,
    }
  },
  methods: {
    async fetchPatients(page = 1) {
      this.loading = true
      try {
        const params = { page, per_page: this.pagination.per_page }
        if (this.searchQuery) params.search = this.searchQuery
        const res = await api.get('/api/admin/patients', { params })
        this.patients = res.data.patients || []
        this.pagination = { ...this.pagination, ...res.data.pagination, page }
      } catch (err) {
        this.showAlert('Failed to load patients: ' + (err.response?.data?.error || err.message), 'error')
      } finally {
        this.loading = false
      }
    },
    clearSearch() {
      this.searchQuery = ''
      this.fetchPatients()
    },
    changePage(newPage) {
      this.fetchPatients(newPage)
    },
    async viewPatient(pat) {
      this.selectedPatient = pat
      this.patientAppointments = []
      try {
        const res = await api.get(`/api/admin/patients/${pat.id}`)
        this.selectedPatient = { ...pat, ...res.data.patient }
        this.patientAppointments = res.data.appointments || []
      } catch (err) {
        // show what we have
      }
    },
    confirmDeactivate(pat) {
      this.patientToDeactivate = pat
      this.selectedPatient = null
    },
    async deactivatePatient() {
      if (!this.patientToDeactivate) return
      this.actionLoading = true
      try {
        await api.delete(`/api/admin/patients/${this.patientToDeactivate.id}`)
        this.showAlert(`Patient "${this.patientToDeactivate.full_name}" deactivated successfully.`, 'success')
        this.patientToDeactivate = null
        this.fetchPatients(this.pagination.page)
      } catch (err) {
        this.showAlert('Failed to deactivate: ' + (err.response?.data?.error || err.message), 'error')
      } finally {
        this.actionLoading = false
      }
    },
    formatDate(dt) {
      if (!dt) return '—'
      return new Date(dt).toLocaleDateString('en-US', { year: 'numeric', month: 'short', day: 'numeric' })
    },
    formatDateTime(dt) {
      if (!dt) return '—'
      return new Date(dt).toLocaleString('en-US', { month: 'short', day: 'numeric', year: 'numeric', hour: '2-digit', minute: '2-digit' })
    },
    statusBadge(status) {
      const m = { booked: 'bg-info', completed: 'bg-success', cancelled: 'bg-danger' }
      return m[status] || 'bg-secondary'
    },
    showAlert(msg, type = 'success') {
      this.alertMsg = msg
      this.alertType = type
      setTimeout(() => { this.alertMsg = '' }, 4000)
    },
  },
  mounted() {
    this.fetchPatients()
  }
}
</script>

<style scoped>
.content-card {
  background: #fff;
  border: 1px solid #e9ecef;
  border-radius: 12px;
  overflow: hidden;
}
.card-body { padding: 1.25rem; }
</style>
