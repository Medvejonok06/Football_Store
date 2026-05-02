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
    <div class="auth-panel glass-card">
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

        <div v-if="!isLogin" class="input-group slide-down">
          <label>Email</label>
          <input v-model="email" type="email" placeholder="твоя_пошта@email.com" required>
        </div>

        <div class="input-group">
          <label>Пароль</label>
          <input v-model="password" type="password" placeholder="••••••••" required minlength="6">
        </div>

        <p v-if="errorMsg" class="error-text">{{ errorMsg }}</p>

        <button type="submit" class="submit-btn" :disabled="isLoading">
          {{ isLoading ? 'Зачекайте...' : (isLogin ? 'Увійти 🚀' : 'Зареєструватися ✅') }}
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
/* ФОН МОДАЛКИ */
.modal-overlay {
  position: fixed; top: 0; left: 0; width: 100vw; height: 100vh;
  background: rgba(11, 15, 25, 0.8); backdrop-filter: blur(12px);
  display: flex; justify-content: center; align-items: center; z-index: 999999;
}

/* СКЛЯНА КАРТКА (GLASSMORPHISM) */
.glass-card {
  background: rgba(17, 24, 39, 0.95);
  backdrop-filter: blur(25px);
  border: 1px solid rgba(255, 255, 255, 0.12);
  border-radius: 32px;
  padding: 40px;
  width: 90%; max-width: 420px;
  box-shadow: 0 30px 60px rgba(0, 0, 0, 0.5), 0 0 40px rgba(0, 255, 136, 0.05);
  position: relative;
  animation: slideDown 0.4s cubic-bezier(0.175, 0.885, 0.32, 1.275);
}

@keyframes slideDown {
  0% { opacity: 0; transform: translateY(-30px) scale(0.95); }
  100% { opacity: 1; transform: translateY(0) scale(1); }
}

/* КНОПКА ЗАКРИТТЯ */
.close-btn {
  position: absolute; top: 20px; right: 20px;
  background: rgba(255, 255, 255, 0.05); border: 1px solid rgba(255, 255, 255, 0.1);
  width: 40px; height: 40px; border-radius: 50%;
  font-size: 1.2rem; cursor: pointer; transition: 0.3s; color: #94a3b8;
  display: flex; align-items: center; justify-content: center;
}
.close-btn:hover {
  background: rgba(239, 68, 68, 0.1); color: #ef4444;
  border-color: rgba(239, 68, 68, 0.3); transform: rotate(90deg);
}

/* ЗАГОЛОВОК */
.auth-header { text-align: center; margin-bottom: 30px; }
.auth-icon { font-size: 3.5rem; margin-bottom: 10px; }
.auth-header h2 { margin: 0 0 5px 0; font-size: 1.8rem; font-weight: 900; color: white; }
.auth-header p { color: #94a3b8; margin: 0; font-size: 0.95rem; line-height: 1.4; }

/* ФОРМА ТА ІНПУТИ */
.auth-form { display: flex; flex-direction: column; gap: 20px; }
.input-group { display: flex; flex-direction: column; gap: 8px; }
.input-group label { font-weight: 800; font-size: 0.9rem; color: #cbd5e1; }
.input-group input {
  padding: 16px; border: 1px solid rgba(255, 255, 255, 0.1); border-radius: 16px;
  font-family: inherit; font-size: 1rem; transition: 0.3s;
  background: rgba(0, 0, 0, 0.2); color: white;
}
.input-group input::placeholder { color: #64748b; }
.input-group input:focus {
  border-color: #00ff88; outline: none; background: rgba(0, 0, 0, 0.4);
  box-shadow: 0 0 0 4px rgba(0, 255, 136, 0.1);
}

/* ПОМИЛКА */
.error-text {
  background: rgba(239, 68, 68, 0.1); color: #ef4444;
  border: 1px solid rgba(239, 68, 68, 0.3); padding: 12px; border-radius: 12px;
  font-weight: 700; font-size: 0.9rem; text-align: center; margin: 0;
}

/* НЕОНОВА КНОПКА SUBMIT */
.submit-btn {
  background: #00ff88; color: #0f172a; border: none; padding: 18px; border-radius: 16px;
  font-size: 1.1rem; font-weight: 900; cursor: pointer; transition: 0.3s; margin-top: 10px;
}
.submit-btn:hover:not(:disabled) {
  transform: translateY(-3px); box-shadow: 0 10px 20px rgba(0, 255, 136, 0.3);
}
.submit-btn:disabled { opacity: 0.5; cursor: not-allowed; filter: grayscale(1); }

/* ПІДВАЛ (ПЕРЕМИКАЧ) */
.auth-footer { margin-top: 25px; text-align: center; font-size: 0.95rem; color: #94a3b8; font-weight: 600; }
.toggle-link { color: #00ff88; cursor: pointer; transition: 0.2s; font-weight: 800; margin-left: 5px; }
.toggle-link:hover { text-shadow: 0 0 10px rgba(0, 255, 136, 0.5); }

/* АНІМАЦІЯ ПОЯВИ ПОЛЯ EMAIL */
.slide-down { animation: slideDownField 0.3s ease-out; }
@keyframes slideDownField {
  from { opacity: 0; transform: translateY(-10px); }
  to { opacity: 1; transform: translateY(0); }
}
</style>
