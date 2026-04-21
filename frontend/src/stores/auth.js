import { defineStore } from 'pinia'
import axios from 'axios'

export const useAuthStore = defineStore('auth', {
  state: () => ({
    token: localStorage.getItem('token') || null,
    username: localStorage.getItem('username') || null,
    isAdmin: localStorage.getItem('isAdmin') === 'true'
  }),
  getters: {
    isAuthenticated: (state) => !!state.token,
  },
  actions: {
    async login(username, password) {
      try {
        const res = await axios.post('http://127.0.0.1:8000/api/login/', { username, password })

        this.token = res.data.access
        this.username = res.data.username
        this.isAdmin = res.data.is_staff // Отримуємо статус з бекенду

        localStorage.setItem('token', this.token)
        localStorage.setItem('username', this.username)
        localStorage.setItem('isAdmin', this.isAdmin)

        axios.defaults.headers.common['Authorization'] = `Bearer ${this.token}`
        return true
      } catch (error) {
        console.error('Login error', error)
        return false
      }
    },
    logout() {
      this.token = null
      this.username = null
      this.isAdmin = false
      localStorage.removeItem('token')
      localStorage.removeItem('username')
      localStorage.removeItem('isAdmin')
      delete axios.defaults.headers.common['Authorization']
    }
  }
})
