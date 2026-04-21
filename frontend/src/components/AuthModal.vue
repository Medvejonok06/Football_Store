<script setup>
import { ref } from 'vue'
import { useAuthStore } from '../stores/auth'

const emit = defineEmits(['close'])
const authStore = useAuthStore()

const isLogin = ref(true) // true - вхід, false - реєстрація
const username = ref('')
const email = ref('')
const password = ref('')
const errorMsg = ref('')
const isLoading = ref(false)

const toggleMode = () => {
  isLogin.value = !isLogin.value
  errorMsg.value = ''
}

const submitForm = async () => {
  isLoading.value = true
  errorMsg.value = ''

  let success
  if (isLogin.value) {
    success = await authStore.login(username.value, password.value)
    if (!success) errorMsg.value = 'Невірний логін або пароль'
  } else {
    success = await authStore.register(username.value, email.value, password.value)
    if (!success) errorMsg.value = 'Помилка реєстрації (можливо, ім\'я вже зайняте)'
  }

  isLoading.value = false
  if (success) {
    emit('close')
  }
}
</script>

<template>
  <div class="modal-overlay" @click.self="emit('close')">
    <div class="auth-panel">
      <button class="close-btn" @click="emit('close')">✕</button>

      <div class="auth-header">
        <div class="auth-icon">🔐</div>
        <h2>{{ isLogin ? 'З поверненням!' : 'Створити акаунт' }}</h2>
        <p>{{ isLogin ? 'Увійди, щоб керувати своїми замовленнями' : 'Приєднуйся до нашої футбольної сім\'ї' }}</p>
      </div>

      <form @submit.prevent="submitForm" class="auth-form">
        <div class="input-group">
          <label>Логін</label>
          <input v-model="username" type="text" placeholder="Твій нікнейм" required>
        </div>

        <div v-if="!isLogin" class="input-group">
          <label>Email</label>
          <input v-model="email" type="email" placeholder="твоя_пошта@email.com" required>
        </div>

        <div class="input-group">
          <label>Пароль</label>
          <input v-model="password" type="password" placeholder="••••••••" required minlength="6">
        </div>

        <p v-if="errorMsg" class="error-text">{{ errorMsg }}</p>

        <button type="submit" class="submit-btn" :disabled="isLoading">
          {{ isLoading ? 'Зачекайте...' : (isLogin ? 'Увійти' : 'Зареєструватися') }}
        </button>
      </form>

      <div class="auth-footer">
        <p>
          {{ isLogin ? 'Ще немає акаунта?' : 'Вже є акаунт?' }}
          <span @click="toggleMode" class="toggle-link">
            {{ isLogin ? 'Зареєструйся' : 'Увійди' }}
          </span>
        </p>
      </div>
    </div>
  </div>
</template>

<style scoped>
.modal-overlay {
  position: fixed; top: 0; left: 0; width: 100vw; height: 100vh;
  background: rgba(15, 23, 42, 0.7); backdrop-filter: blur(10px);
  display: flex; justify-content: center; align-items: center; z-index: 9999;
}

.auth-panel {
  background: white; width: 90%; max-width: 450px;
  border-radius: 32px; padding: 40px; box-shadow: 0 25px 50px rgba(0,0,0,0.2);
  position: relative; animation: slideDown 0.4s cubic-bezier(0.175, 0.885, 0.32, 1.275);
}

@keyframes slideDown {
  0% { opacity: 0; transform: translateY(-30px) scale(0.95); }
  100% { opacity: 1; transform: translateY(0) scale(1); }
}

.close-btn {
  position: absolute; top: 20px; right: 20px; background: #f1f5f9;
  border: none; width: 40px; height: 40px; border-radius: 50%;
  font-size: 1.2rem; cursor: pointer; transition: 0.2s; color: #64748b;
}
.close-btn:hover { background: #ef4444; color: white; transform: rotate(90deg); }

.auth-header { text-align: center; margin-bottom: 30px; }
.auth-icon { font-size: 3.5rem; margin-bottom: 10px; }
.auth-header h2 { margin: 0 0 5px 0; font-size: 1.8rem; font-weight: 900; color: #0f172a; }
.auth-header p { color: #64748b; margin: 0; font-size: 0.9rem; }

.auth-form { display: flex; flex-direction: column; gap: 20px; }
.input-group { display: flex; flex-direction: column; gap: 8px; }
.input-group label { font-weight: 700; font-size: 0.9rem; color: #1e293b; }
.input-group input {
  padding: 14px 18px; border: 2px solid #e2e8f0; border-radius: 14px;
  font-family: inherit; font-size: 1rem; transition: 0.3s; background: #f8fafc;
}
.input-group input:focus { border-color: #6366f1; outline: none; background: white; box-shadow: 0 0 0 4px rgba(99, 102, 241, 0.1); }

.error-text { color: #ef4444; font-weight: 700; font-size: 0.85rem; text-align: center; margin: 0; }

.submit-btn {
  background: #0f172a; color: white; border: none; padding: 16px; border-radius: 14px;
  font-size: 1.1rem; font-weight: 800; cursor: pointer; transition: 0.3s; margin-top: 10px;
}
.submit-btn:hover:not(:disabled) { background: #6366f1; transform: translateY(-2px); box-shadow: 0 10px 20px rgba(99, 102, 241, 0.2); }
.submit-btn:disabled { background: #94a3b8; cursor: not-allowed; }

.auth-footer { margin-top: 25px; text-align: center; font-size: 0.95rem; color: #64748b; font-weight: 600; }
.toggle-link { color: #6366f1; cursor: pointer; transition: 0.2s; font-weight: 800; margin-left: 5px; }
.toggle-link:hover { text-decoration: underline; color: #4f46e5; }
</style>
