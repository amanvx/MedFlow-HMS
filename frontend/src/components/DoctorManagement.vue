<template>
  <div>
    <header class="d-flex justify-content-between align-items-center mb-4">
      <div>
        <h2 class="fw-bold">Doctor Management</h2>
        <p class="text-muted">Manage all doctors in the system</p>
      </div>
      <button class="btn btn-primary" @click="openAddModal">
        <i class="bi bi-plus-circle me-2"></i>Add New Doctor
      </button>
    </header>

    <!-- Error / Success alerts -->
    <div v-if="successMsg" class="alert alert-success alert-dismissible">
      {{ successMsg }}
      <button type="button" class="btn-close" @click="successMsg = ''"></button>
    </div>
    <div v-if="errorMsg" class="alert alert-danger alert-dismissible">
      {{ errorMsg }}
      <button type="button" class="btn-close" @click="errorMsg = ''"></button>
    </div>

    <!-- Search Bar -->
    <div class="card shadow-sm mb-3">
      <div class="card-body py-2">
        <div class="input-group">
          <span class="input-group-text"><i class="bi bi-search"></i></span>
          <input
            v-model="searchQuery"
            type="text"
            class="form-control"
            placeholder="Search by name or specialization..."
            @keyup.enter="fetchDoctors"
          />
          <button class="btn btn-primary" @click="fetchDoctors">Search</button>
          <button class="btn btn-outline-secondary" @click="searchQuery = ''; fetchDoctors()">Clear</button>
        </div>
      </div>
    </div>

    <!-- Doctors Table -->
    <div class="card shadow-sm">
      <div class="card-body">
        <div class="table-responsive">
          <table class="table table-hover">
            <thead>
              <tr>
                <th>ID</th>
                <th>Name</th>
                <th>Specialization</th>
                <th>Department</th>
                <th>Email</th>
                <th>Status</th>
                <th>Actions</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="doctor in doctors" :key="doctor.id">
                <td>{{ doctor.id }}</td>
                <td>{{ doctor.full_name }}</td>
                <td>{{ doctor.specialization || '—' }}</td>
                <td>{{ doctor.department_name || '—' }}</td>
                <td>{{ doctor.email }}</td>
                <td>
                  <span :class="['badge', doctor.is_active ? 'bg-success' : 'bg-danger']">
                    {{ doctor.is_active ? 'Active' : 'Inactive' }}
                  </span>
                </td>
                <td>
                  <div class="d-flex gap-1">
                    <button class="btn btn-sm btn-outline-primary" @click="openEditModal(doctor)" title="Edit doctor">
                      <i class="bi bi-pencil"></i>
                    </button>
                    <button class="btn btn-sm btn-outline-danger" @click="deactivateDoctor(doctor)" :title="doctor.is_active ? 'Deactivate' : 'Already Inactive'">
                      <i class="bi bi-person-x"></i>
                    </button>
                  </div>
                </td>
              </tr>
              <tr v-if="doctors.length === 0">
                <td colspan="7" class="text-center text-muted">No doctors found</td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>
    </div>

    <!-- Add Doctor Modal -->
    <div v-if="showAddModal" class="modal-backdrop fade show" style="z-index:1040" @click="showAddModal = false"></div>
    <div v-if="showAddModal" class="modal fade show d-block" tabindex="-1" style="z-index:1050">
      <div class="modal-dialog modal-lg">
        <div class="modal-content">
          <div class="modal-header">
            <h5 class="modal-title"><i class="bi bi-person-plus me-2"></i>Add New Doctor</h5>
            <button type="button" class="btn-close" @click="showAddModal = false"></button>
          </div>
          <div class="modal-body">
            <div v-if="formError" class="alert alert-danger">{{ formError }}</div>
            <form @submit.prevent="saveDoctor">
              <div class="row g-3">
                <div class="col-md-6">
                  <label class="form-label fw-bold">Full Name <span class="text-danger">*</span></label>
                  <input type="text" class="form-control" v-model="newDoctor.full_name" required placeholder="Dr. Jane Smith">
                </div>
                <div class="col-md-6">
                  <label class="form-label fw-bold">Email <span class="text-danger">*</span></label>
                  <input type="email" class="form-control" v-model="newDoctor.email" required placeholder="doctor@hospital.com">
                </div>
                <div class="col-md-6">
                  <label class="form-label fw-bold">Password <span class="text-danger">*</span></label>
                  <input type="password" class="form-control" v-model="newDoctor.password" required minlength="6" placeholder="Min 6 characters">
                </div>
                <div class="col-md-6">
                  <label class="form-label fw-bold">Specialization</label>
                  <input type="text" class="form-control" v-model="newDoctor.specialization" placeholder="e.g. Cardiologist">
                </div>
                <div class="col-md-6">
                  <label class="form-label fw-bold">Department</label>
                  <select class="form-select" v-model="newDoctor.department_id">
                    <option value="">— Select Department —</option>
                    <option v-for="dept in departments" :key="dept.id" :value="dept.id">{{ dept.name }}</option>
                  </select>
                </div>
              </div>
              <div class="d-flex justify-content-end gap-2 mt-4">
                <button type="button" class="btn btn-secondary" @click="showAddModal = false">Cancel</button>
                <button type="submit" class="btn btn-primary" :disabled="saving">
                  <span v-if="saving" class="spinner-border spinner-border-sm me-2"></span>
                  {{ saving ? 'Saving...' : 'Add Doctor' }}
                </button>
              </div>
            </form>
          </div>
        </div>
      </div>
    </div>

    <!-- Edit Doctor Modal -->
    <div v-if="showEditModal" class="modal-backdrop fade show" style="z-index:1040" @click="showEditModal = false"></div>
    <div v-if="showEditModal" class="modal fade show d-block" tabindex="-1" style="z-index:1050">
      <div class="modal-dialog modal-lg">
        <div class="modal-content">
          <div class="modal-header">
            <h5 class="modal-title"><i class="bi bi-pencil-square me-2"></i>Edit Doctor</h5>
            <button type="button" class="btn-close" @click="showEditModal = false"></button>
          </div>
          <div class="modal-body">
            <div v-if="editError" class="alert alert-danger">{{ editError }}</div>
            <form @submit.prevent="saveEdit">
              <div class="row g-3">
                <div class="col-md-6">
                  <label class="form-label fw-bold">Full Name</label>
                  <input type="text" class="form-control" v-model="editDoctor.full_name" required />
                </div>
                <div class="col-md-6">
                  <label class="form-label fw-bold">Email</label>
                  <input type="email" class="form-control" v-model="editDoctor.email" required />
                </div>
                <div class="col-md-6">
                  <label class="form-label fw-bold">Specialization</label>
                  <input type="text" class="form-control" v-model="editDoctor.specialization" />
                </div>
                <div class="col-md-6">
                  <label class="form-label fw-bold">Department</label>
                  <select class="form-select" v-model="editDoctor.department_id">
                    <option value="">— Select Department —</option>
                    <option v-for="dept in departments" :key="dept.id" :value="dept.id">{{ dept.name }}</option>
                  </select>
                </div>
              </div>
              <div class="d-flex justify-content-end gap-2 mt-4">
                <button type="button" class="btn btn-secondary" @click="showEditModal = false">Cancel</button>
                <button type="submit" class="btn btn-primary" :disabled="editSaving">
                  <span v-if="editSaving" class="spinner-border spinner-border-sm me-2"></span>
                  {{ editSaving ? 'Saving...' : 'Save Changes' }}
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
  name: 'DoctorManagement',
  data() {
    return {
      doctors: [],
      departments: [],
      showAddModal: false,
      saving: false,
      formError: '',
      successMsg: '',
      errorMsg: '',
      searchQuery: '',
      showEditModal: false,
      editDoctor: { id: null, full_name: '', email: '', specialization: '', department_id: '' },
      editError: '',
      editSaving: false,
      newDoctor: {
        full_name: '',
        email: '',
        password: '',
        specialization: '',
        department_id: ''
      }
    }
  },
  mounted() {
    this.fetchDoctors()
    this.fetchDepartments()
  },
  methods: {
    async fetchDoctors() {
      try {
        const params = {}
        if (this.searchQuery) params.search = this.searchQuery
        const response = await api.get('/api/admin/doctors', { params })
        this.doctors = response.data.doctors || []
      } catch (error) {
        console.error('Failed to fetch doctors:', error)
      }
    },
    async fetchDepartments() {
      try {
        const response = await api.get('/api/admin/departments')
        this.departments = response.data.departments || []
      } catch (error) {
        console.error('Failed to fetch departments:', error)
      }
    },
    openAddModal() {
      this.newDoctor = { full_name: '', email: '', password: '', specialization: '', department_id: '' }
      this.formError = ''
      this.showAddModal = true
    },
    async saveDoctor() {
      this.saving = true
      this.formError = ''
      try {
        const payload = {
          full_name: this.newDoctor.full_name,
          email: this.newDoctor.email,
          password: this.newDoctor.password,
          specialization: this.newDoctor.specialization,
          department_id: this.newDoctor.department_id || null
        }
        await api.post('/api/admin/doctors', payload)
        this.showAddModal = false
        this.successMsg = `Doctor "${this.newDoctor.full_name}" added successfully!`
        this.fetchDoctors()
      } catch (error) {
        this.formError = error.response?.data?.error || 'Failed to add doctor'
      } finally {
        this.saving = false
      }
    },
    async deactivateDoctor(doctor) {
      if (!doctor.is_active) return
      if (!confirm(`Deactivate Dr. ${doctor.full_name}? They will no longer be able to log in.`)) return
      try {
        await api.delete(`/api/admin/doctors/${doctor.id}`)
        this.successMsg = `Dr. ${doctor.full_name} has been deactivated.`
        this.fetchDoctors()
      } catch (error) {
        this.errorMsg = error.response?.data?.error || 'Failed to deactivate doctor'
      }
    },
    openEditModal(doctor) {
      this.editDoctor = {
        id: doctor.id,
        full_name: doctor.full_name,
        email: doctor.email,
        specialization: doctor.specialization || '',
        department_id: doctor.department_id || '',
      }
      this.editError = ''
      this.showEditModal = true
    },
    async saveEdit() {
      this.editSaving = true
      this.editError = ''
      try {
        await api.put(`/api/admin/doctors/${this.editDoctor.id}`, {
          full_name: this.editDoctor.full_name,
          email: this.editDoctor.email,
          specialization: this.editDoctor.specialization,
          department_id: this.editDoctor.department_id || null,
        })
        this.showEditModal = false
        this.successMsg = `Dr. ${this.editDoctor.full_name} updated successfully.`
        this.fetchDoctors()
      } catch (error) {
        this.editError = error.response?.data?.error || 'Failed to update doctor'
      } finally {
        this.editSaving = false
      }
    }
  }
}
</script>

<style scoped>
.table { margin-bottom: 0; }
.modal-backdrop { position: fixed; top: 0; left: 0; width: 100%; height: 100%; background: rgba(0,0,0,0.5); }
</style>
