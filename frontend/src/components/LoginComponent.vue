<!-- Login Component -->
<template>
  <div class="login-page">
    <div class="login-card">
      <div class="brand-header">
        <h2>MediCare HMS</h2>
        <p>Hospital Management System V2</p>
      </div>
      <div class="card-body">
        <form @submit.prevent="handleLogin">
          <div class="role-selector mb-4">
            <label class="form-label fw-bold">Select Your Role</label>
            <select class="form-select" v-model="role">
              <option value="patient">Patient</option>
              <option value="doctor">Doctor</option>
              <option value="admin">Administrator</option>
            </select>
          </div>
          
          <div v-if="error" class="alert alert-danger">
            <i class="bi bi-exclamation-triangle-fill me-2"></i>{{ error }}
          </div>
          
          <div class="mb-3">
            <label for="email" class="form-label fw-bold">Username / Email</label>
            <input 
              type="email" 
              class="form-control" 
              id="email" 
              v-model="email"
              placeholder="Enter your username" 
              required
            >
          </div>
          
          <div class="mb-4">
            <label for="password" class="form-label fw-bold">Password</label>
            <input 
              type="password" 
              class="form-control" 
              id="password" 
              v-model="password"
              placeholder="••••••••" 
              required
            >
          </div>
          
          <div class="d-grid mb-3">
            <button type="submit" class="btn btn-primary" :disabled="loading">
              <span v-if="loading" class="spinner-border spinner-border-sm me-2"></span>
              {{ loading ? 'Signing In...' : 'Sign In' }}
            </button>
          </div>
          
          <div class="d-flex justify-content-between footer-links">
            <a href="#" class="text-decoration-none">Forgot Password?</a>
            <router-link to="/register" class="text-decoration-none">Create Account</router-link>
          </div>
        </form>
      </div>
      <div class="text-center pb-4 text-muted" style="font-size: 0.75rem;">
        &copy; 2023 Comprehensive Hospital Management System
      </div>
    </div>
  </div>
</template>

<script>
export default {
  name: 'LoginComponent',
  data() {
    return {
      role: 'patient',
      email: '',
      password: '',
      loading: false,
      error: ''
    }
  },
  methods: {
    async handleLogin() {
      this.loading = true
      this.error = ''
      try {
        // Login logic will be implemented by main.js
        this.$emit('login', { email: this.email, password: this.password })
      } catch (err) {
        this.error = err.message || 'Login failed'
      } finally {
        this.loading = false
      }
    }
  }
}
</script>

<style scoped>
.login-page {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  min-height: 100vh;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 20px;
}

.login-card {
  border: none;
  border-radius: 12px;
  box-shadow: 0 10px 25px rgba(0,0,0,0.1);
  width: 100%;
  max-width: 400px;
  background: #fff;
}

.brand-header {
  background-color: #0d6efd;
  color: white;
  padding: 2rem;
  border-radius: 12px 12px 0 0;
  text-align: center;
}

.brand-header h2 {
  font-weight: 700;
  margin: 0;
}

.brand-header p {
  margin: 0;
  opacity: 0.8;
  font-size: 0.9rem;
}

.card-body {
  padding: 2.5rem;
}

.form-control {
  border-radius: 8px;
  padding: 0.75rem;
}

.btn-primary {
  border-radius: 8px;
  padding: 0.75rem;
  font-weight: 600;
  background-color: #0d6efd;
  border: none;
}

.footer-links {
  font-size: 0.85rem;
  color: #6c757d;
}
</style>
