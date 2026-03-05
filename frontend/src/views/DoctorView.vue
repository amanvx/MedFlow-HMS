<template>
  <div>
    <DoctorDashboard 
      :user="user" 
      @logout="handleLogout"
    />
  </div>
</template>

<script>
import DoctorDashboard from '../components/DoctorDashboard.vue'
import { mapGetters, mapActions } from 'vuex'

export default {
  name: 'DoctorView',
  components: {
    DoctorDashboard
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
