<template>
  <div>
    <AdminDashboard 
      :user="user" 
      @logout="handleLogout"
    />
  </div>
</template>

<script>
import AdminDashboard from '../components/AdminDashboard.vue'
import { mapGetters, mapActions } from 'vuex'

export default {
  name: 'AdminView',
  components: {
    AdminDashboard
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
