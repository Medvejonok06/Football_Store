import { defineStore } from 'pinia'
import axios from 'axios'

export const useAuthStore = defineStore('auth', {
  state: () => ({
    token: localStorage.getItem('token') || null,
    username: localStorage.getItem('username') || null
  }),
  getters: {
    isAuthenticated: (state) => !!state.token,
  },
  actions: {
    async login(username, password) {
      try {
        const res = await axios.post('http://127.0.0.1:8000/api/login/', { username, password })
        this.token = res.data.access
        this.username = username
        // Зберігаємо в пам'яті браузера
        localStorage.setItem('token', this.token)
        localStorage.setItem('username', this.username)
        // Додаємо токен до всіх наступних запитів
        axios.defaults.headers.common['Authorization'] = `Bearer ${this.token}`
        return true
      } catch (error) {
        console.error('Помилка логіну', error)
        return false
      }
    },
    async register(username, email, password) {
      try {
        await axios.post('http://127.0.0.1:8000/api/register/', { username, email, password })
        // Після успішної реєстрації одразу логінимось
        return await this.login(username, password)
      } catch (error) {
        console.error('Помилка реєстрації', error)
        return false
      }
    },
    logout() {
      this.token = null
      this.username = null
      localStorage.removeItem('token')
      localStorage.removeItem('username')
      delete axios.defaults.headers.common['Authorization']
    }
  }
})
