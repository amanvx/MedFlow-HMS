<!-- Register Component -->
<template>
  <div class="login-page">
    <div class="login-card">
      <div class="brand-header">
        <i class="bi bi-person-plus display-4"></i>
        <h2>Patient Registration</h2>
        <p>Create your account</p>
      </div>
      <div class="card-body">
        <div v-if="error" class="alert alert-danger">{{ error }}</div>
        <div v-if="success" class="alert alert-success">Registration successful! Redirecting...</div>
        
        <form @submit.prevent="handleRegister" v-if="!success">
          <div class="mb-3">
            <label class="form-label fw-bold">Full Name</label>
            <input type="text" class="form-control" v-model="form.full_name" required>
          </div>
          
          <div class="mb-3">
            <label class="form-label fw-bold">Email</label>
            <input type="email" class="form-control" v-model="form.email" required>
          </div>
          
          <div class="mb-3">
            <label class="form-label fw-bold">Password</label>
            <input type="password" class="form-control" v-model="form.password" minlength="6" required>
          </div>
          
          <div class="mb-3">
            <label class="form-label fw-bold">Contact Number</label>
            <input type="tel" class="form-control" v-model="form.contact">
          </div>
          
          <div class="mb-4">
            <label class="form-label fw-bold">Address</label>
            <textarea class="form-control" v-model="form.address" rows="2"></textarea>
          </div>
          
          <button type="submit" class="btn btn-success w-100 mb-3" :disabled="loading">
            <span v-if="loading" class="spinner-border spinner-border-sm me-2"></span>
            {{ loading ? 'Registering...' : 'Create Account' }}
          </button>
        </form>
        
        <div class="text-center">
          <p class="mb-0">Already have an account? 
            <router-link to="/login" class="fw-bold text-decoration-none">Sign In</router-link>
          </p>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
export default {
  name: 'RegisterComponent',
  data() {
    return {
      form: {
        full_name: '',
        email: '',
        password: '',
        contact: '',
        address: ''
      },
      loading: false,
      error: '',
      success: false
    }
  },
  methods: {
    async handleRegister() {
      this.loading = true
      this.error = ''
      try {
        this.$emit('register', this.form)
      } catch (err) {
        this.error = err.message || 'Registration failed'
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
  max-width: 450px;
  background: #fff;
}

.brand-header {
  background: linear-gradient(135deg, #28a745 0%, #20c997 100%);
  color: white;
  padding: 2rem;
  border-radius: 12px 12px 0 0;
  text-align: center;
}

.card-body {
  padding: 2.5rem;
}
</style>
