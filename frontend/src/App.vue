<script setup>
import { ref, onMounted } from 'vue'
import { useCartStore } from './stores/cart'
import AnalyticsDashboard from './components/AnalyticsDashboard.vue'
import { useAuthStore } from './stores/auth'
import AuthModal from './components/AuthModal.vue'
import axios from 'axios'

const authStore = useAuthStore()
const showAuthModal = ref(false)

onMounted(() => {
  if (authStore.token) {
    axios.defaults.headers.common['Authorization'] = `Bearer ${authStore.token}`
  }
})

const cartStore = useCartStore()
const isAnalyticsOpen = ref(false)
</script>

<template>
  <div class="app-shell">
    <div class="bg-blob blob-1"></div>
    <div class="bg-blob blob-2"></div>

    <header class="glass-header">
      <div class="container">
        <router-link to="/" class="logo">
          <div class="logo-circle">FS</div>
          <span class="logo-text">Football<span>PRO</span></span>
        </router-link>

        <nav class="header-actions">
          <router-link to="/about" class="action-btn about-link">Про нас</router-link>

          <button class="action-btn admin-btn" @click="isAnalyticsOpen = true">
            <span class="icon">📊</span> Аналітика
          </button>

          <div class="user-menu">
            <button
              v-if="!authStore.isAuthenticated"
              @click="showAuthModal = true"
              class="action-btn login-btn"
            >
              <span class="icon">👤</span> Увійти
            </button>

            <div v-else class="user-profile">
              <div class="user-avatar">😎</div>
              <div class="user-info">
                <span class="user-greeting">Привіт,</span>
                <span class="user-name">{{ authStore.username }}</span>
              </div>
              <button @click="authStore.logout()" class="logout-icon-btn" title="Вийти з акаунта">
                <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                  <path d="M9 21H5a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h4"></path>
                  <polyline points="16 17 21 12 16 7"></polyline>
                  <line x1="21" y1="12" x2="9" y2="12"></line>
                </svg>
              </button>
            </div>
          </div>

          <router-link to="/checkout" class="action-btn cart-btn">
            <span class="icon">🛒</span>
            Кошик
            <div v-if="cartStore.cartCount > 0" class="cart-badge">{{ cartStore.cartCount }}</div>
          </router-link>
        </nav>
      </div>
    </header>

    <main class="content-area">
      <router-view></router-view>
    </main>

    <AuthModal v-if="showAuthModal" @close="showAuthModal = false" />
    <AnalyticsDashboard v-if="isAnalyticsOpen" @close="isAnalyticsOpen = false" />
  </div>
</template>

<style>
/* ГЛОБАЛЬНІ НАЛАШТУВАННЯ */
:root {
  --primary: #00ff88;
  --accent: #6366f1;
  --dark: #0f172a;
  --text: #1e293b;
}

body {
  margin: 0;
  font-family: 'Plus Jakarta Sans', 'Inter', sans-serif;
  background: #f8fafc;
  color: var(--text);
  overflow-x: hidden;
}

.bg-blob {
  position: fixed;
  width: 600px;
  height: 600px;
  border-radius: 50%;
  filter: blur(120px);
  z-index: -1;
  opacity: 0.35;
  animation: float 25s infinite alternate ease-in-out;
}
.blob-1 { background: var(--primary); top: -150px; right: -150px; }
.blob-2 { background: var(--accent); bottom: -150px; left: -150px; animation-delay: -7s; }

@keyframes float {
  0% { transform: translate(0, 0) rotate(0deg); }
  100% { transform: translate(150px, 100px) rotate(30deg); }
}
</style>

<style scoped>
.glass-header {
  position: sticky;
  top: 0;
  z-index: 1000;
  background: rgba(255, 255, 255, 0.7);
  backdrop-filter: blur(20px);
  -webkit-backdrop-filter: blur(20px);
  border-bottom: 1px solid rgba(255, 255, 255, 0.3);
}

.container {
  max-width: 1300px;
  margin: 0 auto;
  padding: 12px 25px;
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.logo {
  display: flex;
  align-items: center;
  gap: 12px;
  text-decoration: none;
}

.logo-circle {
  width: 48px;
  height: 48px;
  background: var(--dark);
  color: var(--primary);
  border-radius: 14px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-weight: 900;
  font-size: 1.3rem;
  box-shadow: 0 10px 20px rgba(0,0,0,0.1);
}

.logo-text {
  font-size: 1.7rem;
  font-weight: 900;
  color: var(--dark);
  letter-spacing: -1px;
}
.logo-text span { color: var(--accent); }

.header-actions {
  display: flex;
  gap: 12px;
  align-items: center;
}

.action-btn {
  padding: 12px 24px;
  border-radius: 16px;
  border: none;
  font-weight: 700;
  cursor: pointer;
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
  text-decoration: none;
  display: flex;
  align-items: center;
  gap: 10px;
}

.action-btn:hover {
  transform: translateY(-4px);
  box-shadow: 0 12px 24px rgba(0,0,0,0.1);
}

.about-link { background: transparent; color: var(--dark); }
.about-link:hover { color: var(--accent); background: rgba(99, 102, 241, 0.05); }

.admin-btn { background: white; color: var(--dark); border: 1px solid #e2e8f0; }

/* СТИЛІ КНОПКИ ЛОГІНУ */
.login-btn {
  background: rgba(99, 102, 241, 0.1);
  color: var(--accent);
  border: 1px solid rgba(99, 102, 241, 0.2);
}
.login-btn:hover {
  background: var(--accent);
  color: white;
  border-color: var(--accent);
  box-shadow: 0 10px 20px rgba(99, 102, 241, 0.2);
}

/* СТИЛІ ПРОФІЛЮ КОРИСТУВАЧА */
.user-profile {
  display: flex;
  align-items: center;
  gap: 12px;
  background: white;
  padding: 6px 14px 6px 6px; /* Менше зліва для аватарки */
  border-radius: 20px;
  border: 1px solid #e2e8f0;
  box-shadow: 0 4px 15px rgba(0,0,0,0.03);
}

.user-avatar {
  width: 36px;
  height: 36px;
  background: #f1f5f9;
  border-radius: 14px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 1.1rem;
}

.user-info {
  display: flex;
  flex-direction: column;
  line-height: 1.2;
}

.user-greeting {
  font-size: 0.7rem;
  color: #64748b;
  font-weight: 700;
  text-transform: uppercase;
}

.user-name {
  font-size: 0.95rem;
  font-weight: 800;
  color: var(--dark);
}

.logout-icon-btn {
  background: transparent;
  border: none;
  color: #94a3b8;
  cursor: pointer;
  padding: 8px;
  border-radius: 12px;
  transition: 0.2s;
  display: flex;
  align-items: center;
  justify-content: center;
  margin-left: 5px;
}
.logout-icon-btn:hover {
  background: #fee2e2;
  color: #ef4444;
}

.cart-btn {
  background: var(--dark);
  color: white;
  position: relative;
}

.cart-badge {
  position: absolute;
  top: -8px;
  right: -8px;
  background: var(--primary);
  color: var(--dark);
  width: 24px;
  height: 24px;
  border-radius: 50%;
  font-size: 0.85rem;
  font-weight: 800;
  display: flex;
  align-items: center;
  justify-content: center;
  box-shadow: 0 4px 10px rgba(0, 255, 136, 0.4);
}

.content-area {
  max-width: 1300px;
  margin: 40px auto;
  padding-bottom: 100px;
}
</style>
