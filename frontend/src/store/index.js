/**
 * Vuex Store - Global State Management
 * Manages authentication, user data, and application state
 */

import { createStore } from 'vuex'
import api from '../axios'

export default createStore({
  state: {
    user: JSON.parse(localStorage.getItem('user') || 'null'),
    token: localStorage.getItem('access_token') || null,
    isAuthenticated: !!localStorage.getItem('access_token'),
    loading: false,
    error: null,
    
    // Dashboard data
    adminStats: null,
    doctors: [],
    departments: [],
    appointments: [],
    patients: []
  },
  
  getters: {
    isAuthenticated: state => state.isAuthenticated,
    currentUser: state => state.user,
    userRole: state => state.user?.role || null,
    isAdmin: state => state.user?.role === 'admin',
    isDoctor: state => state.user?.role === 'doctor',
    isPatient: state => state.user?.role === 'patient'
  },
  
  mutations: {
    SET_USER(state, user) {
      state.user = user
      state.isAuthenticated = true
      localStorage.setItem('user', JSON.stringify(user))
    },
    
    SET_TOKEN(state, token) {
      state.token = token
      localStorage.setItem('access_token', token)
    },
    
    LOGOUT(state) {
      state.user = null
      state.token = null
      state.isAuthenticated = false
      localStorage.removeItem('user')
      localStorage.removeItem('access_token')
    },
    
    SET_LOADING(state, loading) {
      state.loading = loading
    },
    
    SET_ERROR(state, error) {
      state.error = error
    },
    
    SET_ADMIN_STATS(state, stats) {
      state.adminStats = stats
    },
    
    SET_DOCTORS(state, doctors) {
      state.doctors = doctors
    },
    
    SET_DEPARTMENTS(state, departments) {
      state.departments = departments
    },
    
    SET_APPOINTMENTS(state, appointments) {
      state.appointments = appointments
    },
    
    SET_PATIENTS(state, patients) {
      state.patients = patients
    }
  },
  
  actions: {
    async login({ commit }, credentials) {
      commit('SET_LOADING', true)
      commit('SET_ERROR', null)
      try {
        const response = await api.post('/api/auth/login', credentials)
        commit('SET_USER', response.data.user)
        commit('SET_TOKEN', response.data.access_token)
        return response.data
      } catch (error) {
        commit('SET_ERROR', error.response?.data?.error || 'Login failed')
        throw error
      } finally {
        commit('SET_LOADING', false)
      }
    },
    
    async register({ commit }, formData) {
      commit('SET_LOADING', true)
      commit('SET_ERROR', null)
      try {
        const response = await api.post('/api/auth/register', formData)
        commit('SET_USER', response.data.user)
        commit('SET_TOKEN', response.data.access_token)
        return response.data
      } catch (error) {
        commit('SET_ERROR', error.response?.data?.error || 'Registration failed')
        throw error
      } finally {
        commit('SET_LOADING', false)
      }
    },
    
    logout({ commit }) {
      commit('LOGOUT')
    },
    
    async fetchAdminStats({ commit }) {
      try {
        const response = await api.get('/api/admin/overview')
        commit('SET_ADMIN_STATS', response.data.stats)
        commit('SET_APPOINTMENTS', response.data.recent_appointments)
        return response.data
      } catch (error) {
        commit('SET_ERROR', error.response?.data?.error || 'Failed to fetch stats')
        throw error
      }
    },
    
    async fetchDoctors({ commit }, params = {}) {
      try {
        const response = await api.get('/api/admin/doctors', { params })
        commit('SET_DOCTORS', response.data.doctors)
        return response.data
      } catch (error) {
        throw error
      }
    },
    
    async fetchDepartments({ commit }) {
      try {
        const response = await api.get('/api/admin/departments')
        commit('SET_DEPARTMENTS', response.data.departments)
        return response.data
      } catch (error) {
        throw error
      }
    },
    
    async fetchAppointments({ commit }, params = {}) {
      try {
        const response = await api.get('/api/patient/appointments', { params })
        commit('SET_APPOINTMENTS', response.data.appointments)
        return response.data
      } catch (error) {
        throw error
      }
    },
    
    async bookAppointment({ commit }, appointmentData) {
      try {
        const response = await api.post('/api/patient/appointments', appointmentData)
        return response.data
      } catch (error) {
        throw error
      }
    }
  },
  
  modules: {
    // Add modules here if needed
  }
})
