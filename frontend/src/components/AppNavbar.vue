<script setup>
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '../stores/auth'
import AppConfirm from '../components/AppConfirm.vue' // Імпортуємо нову модалку

const router = useRouter()
const authStore = useAuthStore()

// Стан для модалки підтвердження виходу
const showLogoutConfirm = ref(false)

const triggerLogout = () => {
  showLogoutConfirm.value = true
}

const confirmLogout = () => {
  authStore.logout()
  showLogoutConfirm.value = false
  // Після виходу просто залишаємось на головній, інтерфейс оновиться сам
  router.push('/')
}
</script>

<template>
  <nav class="navbar glass-effect">
    <!-- МОДАЛКА ПІДТВЕРДЖЕННЯ ВИХОДУ -->
    <AppConfirm
      v-if="showLogoutConfirm"
      @confirm="confirmLogout"
      @cancel="showLogoutConfirm = false"
    />

    <div class="logo-container" @click="router.push('/')">
      <div class="logo-badge">FS</div>
      <span class="logo-text">Football<span class="pro-highlight">PRO</span></span>
    </div>

    <div class="nav-controls">
      <button class="nav-btn dark-outline">
        <span class="btn-text">Про нас</span>
      </button>

      <button v-if="authStore.isAdmin" class="nav-btn neon-outline" @click="router.push('/admin')">
        <span class="btn-icon">📊</span>
        <span class="btn-text">Аналітика</span>
      </button>

      <!-- ПАНЕЛЬ КОРИСТУВАЧА -->
      <div v-if="authStore.user" class="user-pill" @click="triggerLogout">
        <span class="user-emoji">😎</span>
        <div class="user-details">
          <span class="user-prefix">ПРИВІТ,</span>
          <span class="user-name">{{ authStore.user?.username || 'Гість' }}</span>
        </div>
      </div>

      <!-- КНОПКА УВІЙТИ (якщо не залогінений) -->
      <button v-else class="nav-btn dark-outline" @click="$emit('open-auth')">
        <span class="btn-icon">👤</span>
        <span class="btn-text">Увійти</span>
      </button>

      <button class="nav-btn primary-btn" @click="router.push('/cart')">
        <span class="btn-icon">🛒</span>
        <span class="btn-text">Кошик</span>
      </button>
    </div>
  </nav>
</template>

<style scoped>
.navbar {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 15px 40px;
  background: rgba(11, 17, 33, 0.85);
  backdrop-filter: blur(15px);
  border-bottom: 1px solid rgba(255, 255, 255, 0.05);
  position: sticky;
  top: 0;
  z-index: 1000;
}

.logo-container {
  display: flex;
  align-items: center;
  gap: 12px;
  cursor: pointer;
}

.logo-badge {
  background: white;
  color: #050811;
  border-radius: 12px;
  font-weight: 900;
  padding: 8px 12px;
}

.logo-text {
  color: white;
  font-weight: 900;
  font-size: 1.2rem;
  letter-spacing: 0.5px;
}
.pro-highlight { color: #00ff88; }

.nav-controls { display: flex; align-items: center; gap: 15px; }

.nav-btn {
  height: 46px;
  padding: 0 20px;
  border-radius: 14px;
  font-weight: 800;
  cursor: pointer;
  transition: 0.3s cubic-bezier(0.4, 0, 0.2, 1);
  display: flex;
  align-items: center;
  gap: 10px;
}

.dark-outline {
  background: rgba(255, 255, 255, 0.03);
  border: 1px solid rgba(255, 255, 255, 0.1);
  color: #94a3b8;
}
.dark-outline:hover {
  background: rgba(255, 255, 255, 0.08);
  color: white;
  border-color: rgba(255, 255, 255, 0.2);
}

.neon-outline {
  background: rgba(99, 102, 241, 0.05);
  border: 1px solid rgba(99, 102, 241, 0.3);
  color: #6366f1;
}

.primary-btn {
  background: #00ff88;
  border: none;
  color: #050811;
}
.primary-btn:hover {
  box-shadow: 0 0 20px rgba(0, 255, 136, 0.3);
  transform: translateY(-2px);
}

.user-pill {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 5px 20px;
  background: rgba(255, 255, 255, 0.03);
  border-radius: 14px;
  border: 1px solid rgba(255, 255, 255, 0.1);
  cursor: pointer;
  height: 46px;
  transition: 0.3s;
}

.user-pill:hover {
  border-color: #ef4444; /* Колір виходу при наведенні */
  background: rgba(239, 68, 68, 0.05);
}

.user-details {
  display: flex;
  align-items: center;
  gap: 6px;
}

.user-prefix {
  color: #94a3b8;
  font-size: 0.9rem;
  font-weight: 800;
}

.user-name {
  color: white;
  font-size: 1rem;
  font-weight: 800;
  text-transform: uppercase;
}
</style>
