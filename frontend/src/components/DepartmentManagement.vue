<template>
  <div>
    <header class="d-flex justify-content-between align-items-center mb-4">
      <div>
        <h2 class="fw-bold">Department Management</h2>
        <p class="text-muted">Manage hospital departments</p>
      </div>
      <button class="btn btn-primary" @click="showAddModal = true">
        <i class="bi bi-plus-circle me-2"></i>Add New Department
      </button>
    </header>

    <!-- Departments Grid -->
    <div class="row g-4">
      <div class="col-md-4" v-for="dept in departments" :key="dept.id">
        <div class="card shadow-sm h-100">
          <div class="card-body">
            <div class="d-flex justify-content-between align-items-start mb-3">
              <h5 class="card-title">{{ dept.name }}</h5>
              <div class="dropdown">
                <button class="btn btn-sm btn-link" data-bs-toggle="dropdown">
                  <i class="bi bi-three-dots-vertical"></i>
                </button>
                <ul class="dropdown-menu">
                  <li><a class="dropdown-item" @click="editDepartment(dept)">Edit</a></li>
                  <li><a class="dropdown-item text-danger" @click="deleteDepartment(dept.id)">Delete</a></li>
                </ul>
              </div>
            </div>
            <p class="card-text text-muted">{{ dept.description || 'No description' }}</p>
            <div class="mt-3">
              <div class="d-flex justify-content-between text-muted small">
                <span><i class="bi bi-person-badge me-1"></i>Head: {{ dept.head_name || 'N/A' }}</span>
              </div>
              <div class="d-flex justify-content-between text-muted small mt-2">
                <span><i class="bi bi-people me-1"></i>{{ dept.doctor_count || 0 }} Doctors</span>
                <span :class="['badge', dept.is_active ? 'bg-success' : 'bg-danger']">
                  {{ dept.is_active ? 'Active' : 'Inactive' }}
                </span>
              </div>
            </div>
          </div>
        </div>
      </div>
      <div v-if="departments.length === 0" class="col-12">
        <div class="alert alert-info text-center">
          <i class="bi bi-info-circle me-2"></i>
          No departments found. Click "Add New Department" to create one.
        </div>
      </div>
    </div>

    <!-- Add Department Modal -->
    <div v-if="showAddModal" class="modal-backdrop fade show" @click="showAddModal = false"></div>
    <div v-if="showAddModal" class="modal fade show d-block" tabindex="-1">
      <div class="modal-dialog">
        <div class="modal-content">
          <div class="modal-header">
            <h5 class="modal-title">Add New Department</h5>
            <button type="button" class="btn-close" @click="showAddModal = false"></button>
          </div>
          <div class="modal-body">
            <form @submit.prevent="saveDepartment">
              <div class="mb-3">
                <label class="form-label">Department Name</label>
                <input type="text" class="form-control" v-model="newDepartment.name" required>
              </div>
              <div class="mb-3">
                <label class="form-label">Description</label>
                <textarea class="form-control" v-model="newDepartment.description" rows="3"></textarea>
              </div>
              <div class="d-flex justify-content-end gap-2">
                <button type="button" class="btn btn-secondary" @click="showAddModal = false">Cancel</button>
                <button type="submit" class="btn btn-primary">Save Department</button>
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
  name: 'DepartmentManagement',
  data() {
    return {
      departments: [],
      showAddModal: false,
      newDepartment: {
        name: '',
        description: ''
      }
    }
  },
  mounted() {
    this.fetchDepartments()
  },
  methods: {
    async fetchDepartments() {
      try {
        const response = await api.get('/api/admin/departments')
        this.departments = response.data.departments || []
      } catch (error) {
        console.error('Failed to fetch departments:', error)
      }
    },
    async saveDepartment() {
      try {
        await api.post('/api/admin/departments', this.newDepartment)
        this.showAddModal = false
        this.newDepartment = { name: '', description: '' }
        this.fetchDepartments()
      } catch (error) {
        console.error('Failed to save department:', error)
      }
    },
    editDepartment(dept) {
      console.log('Edit department:', dept)
    },
    async deleteDepartment(id) {
      if (confirm('Are you sure you want to delete this department?')) {
        try {
          await api.delete(`/api/admin/departments/${id}`)
          this.fetchDepartments()
        } catch (error) {
          console.error('Failed to delete department:', error)
        }
      }
    }
  }
}
</script>

<style scoped>
.modal-backdrop {
  background-color: rgba(0, 0, 0, 0.5);
}
</style>
