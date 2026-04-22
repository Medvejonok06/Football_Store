<script setup>
import { useRouter } from 'vue-router'
import { useAuthStore } from '../stores/auth'

const router = useRouter()
const authStore = useAuthStore()

const handleLogout = () => {
  authStore.logout()
  router.push('/login')
}
</script>

<template>
  <nav class="navbar">
    <div class="logo-container" @click="router.push('/')">
      <div class="logo-badge">FS</div>
      <span class="logo-text">Football<span class="pro-highlight">PRO</span></span>
    </div>

    <div class="nav-controls">
      <button class="nav-btn outline-btn">
        <span class="btn-text">Про нас</span>
      </button>

      <button v-if="authStore.isAdmin" class="nav-btn outline-btn" @click="router.push('/admin')">
        <span class="btn-icon">📊</span>
        <span class="btn-text">Аналітика</span>
      </button>

      <div class="user-profile-btn nav-btn outline-btn" @click="handleLogout">
        <span class="user-emoji">😎</span>
        <div class="user-details">
          <span class="user-prefix">ПРИВІТ,</span>
          <span class="user-name">{{ authStore.user?.username || 'medvejonok' }}</span>
        </div>
        <span class="exit-icon">➔</span>
      </div>

      <button class="nav-btn cart-btn" @click="router.push('/cart')">
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
  background: white;
  border-bottom: 1px solid #f1f5f9;
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
  background: #0f172a;
  color: #00ff88;
  font-weight: 900;
  padding: 8px 12px;
  border-radius: 12px;
  font-size: 1.2rem;
}

.logo-text {
  font-size: 1.5rem;
  font-weight: 800;
  color: #0f172a;
  letter-spacing: -0.5px;
}

.pro-highlight {
  color: #6366f1;
}

.nav-controls {
  display: flex;
  align-items: center;
  gap: 12px;
}

/* ЗАГАЛЬНИЙ СТИЛЬ КНОПОК */
.nav-btn {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 10px;

  min-width: 160px;
  height: 48px;
  padding: 0 18px;

  border-radius: 14px;
  font-family: inherit;
  cursor: pointer;
  transition: all 0.3s ease;
  box-sizing: border-box;
}

/* ТЕКСТ (ОДНАКОВИЙ РОЗМІР ДЛЯ ВСІХ) */
.btn-text, .user-name {
  font-weight: 800;
  font-size: 0.95rem; /* Єдиний розмір шрифту */
  white-space: nowrap;
}

/* КНОПКИ З ОБВОДКОЮ */
.outline-btn {
  background: white;
  border: 2px solid #e2e8f0;
  color: #1e293b;
}

.outline-btn:hover {
  border-color: #6366f1;
  background: #f8fafc;
  transform: translateY(-2px);
}

/* КОШИК */
.cart-btn {
  background: #0f172a;
  border: 2px solid #0f172a;
  color: white;
}

.cart-btn:hover {
  background: #1e293b;
  border-color: #6366f1;
  transform: translateY(-2px);
}

/* ДЕТАЛІ КОРИСТУВАЧА */
.user-details {
  display: flex;
  flex-direction: column;
  align-items: flex-start;
  line-height: 1.1;
}

.user-prefix {
  font-size: 0.65rem;
  font-weight: 800;
  color: #94a3b8;
  text-transform: uppercase;
}

.btn-icon, .user-emoji {
  font-size: 1.2rem;
  display: flex;
  align-items: center;
}

.exit-icon {
  margin-left: auto;
  opacity: 0.3;
  font-size: 0.8rem;
}

@media (max-width: 1000px) {
  .navbar { padding: 15px 20px; }
  .nav-btn { min-width: auto; padding: 0 12px; }
  .btn-text, .user-details { display: none; }
}
</style>
