<template>
  <div>
    <PatientDashboard 
      :user="user" 
      @logout="handleLogout"
    />
  </div>
</template>

<script>
import PatientDashboard from '../components/PatientDashboard.vue'
import { mapGetters, mapActions } from 'vuex'

export default {
  name: 'PatientView',
  components: {
    PatientDashboard
  },
  computed: {
    ...mapGetters(['currentUser']),
    user() {
      return this.currentUser
    }
  },
  methods: {
    ...mapActions(['logout']),
    handleLogout() {
      this.logout()
      this.$router.push('/login')
    }
  }
}
</script>
