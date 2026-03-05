/**
 * Vue Router Configuration
 * Client-side routing for the HMS application
 */

import { createRouter, createWebHashHistory } from 'vue-router'

// Import views
import LoginView from '../views/LoginView.vue'
import RegisterView from '../views/RegisterView.vue'
import AdminView from '../views/AdminView.vue'
import DoctorView from '../views/DoctorView.vue'
import PatientView from '../views/PatientView.vue'

const routes = [
  {
    path: '/',
    redirect: '/login'
  },
  {
    path: '/login',
    name: 'Login',
    component: LoginView,
    meta: { requiresAuth: false }
  },
  {
    path: '/register',
    name: 'Register',
    component: RegisterView,
    meta: { requiresAuth: false }
  },
  {
    path: '/admin',
    name: 'Admin',
    component: AdminView,
    meta: { requiresAuth: true, role: 'admin' }
  },
  {
    path: '/doctor',
    name: 'Doctor',
    component: DoctorView,
    meta: { requiresAuth: true, role: 'doctor' }
  },
  {
    path: '/patient',
    name: 'Patient',
    component: PatientView,
    meta: { requiresAuth: true, role: 'patient' }
  }
]

const router = createRouter({
  history: createWebHashHistory(),
  routes
})

// Navigation Guard
router.beforeEach((to, from, next) => {
  const token = localStorage.getItem('access_token')
  const user = JSON.parse(localStorage.getItem('user') || 'null')
  
  if (to.meta.requiresAuth) {
    if (!token) {
      next('/login')
    } else if (to.meta.role && user?.role !== to.meta.role) {
      // Wrong role - redirect to appropriate dashboard
      next(`/${user.role}`)
    } else {
      next()
    }
  } else {
    // If already logged in and trying to access login/register
    if (token && user && (to.path === '/login' || to.path === '/register')) {
      next(`/${user.role}`)
    } else {
      next()
    }
  }
})

export default router
