<script setup>
import { ref, onMounted } from 'vue'
import { useCartStore } from './stores/cart'
import AnalyticsDashboard from './components/AnalyticsDashboard.vue'
import { useAuthStore } from './stores/auth'
import AuthModal from './components/AuthModal.vue'
import AppConfirm from './components/AppConfirm.vue'
import axios from 'axios'

const authStore = useAuthStore()
const showAuthModal = ref(false)
const showLogoutConfirm = ref(false)
const cartStore = useCartStore()
const isAnalyticsOpen = ref(false)

onMounted(() => {
  if (authStore.token) {
    axios.defaults.headers.common['Authorization'] = `Bearer ${authStore.token}`
  }
})

const handleLogout = () => {
  showLogoutConfirm.value = false
  cartStore.clearCart()
  authStore.logout()
}
</script>

<template>
  <div class="app-shell stadium-theme">
    <!-- Декоративні елементи фону -->
    <div class="pitch-markings"></div>
    <div class="stadium-light light-left"></div>
    <div class="stadium-light light-right"></div>

    <!-- ХЕДЕР ПЕРЕНЕСЕНО СЮДИ ДЛЯ ГАРАНТОВАНОЇ ВИДИМОСТІ -->
    <header class="glass-header">
      <div class="header-container">
        <router-link to="/" class="logo">
          <div class="logo-circle">FP</div>
          <span class="logo-text">Football<span>PRO</span></span>
        </router-link>

        <nav class="header-actions">
          <router-link to="/about" class="action-btn link-btn">Про нас</router-link>

          <button v-if="authStore.isAdmin" class="action-btn admin-btn" @click="isAnalyticsOpen = true">
            <span class="icon">📊</span> Аналітика
          </button>

          <div v-if="!authStore.isAuthenticated">
            <button @click="showAuthModal = true" class="action-btn login-btn">
              <span class="icon">👤</span> Увійти
            </button>
          </div>

<div v-else class="user-profile-badge">
  <span class="user-emoji">😎</span>
  <div class="user-data">
    <span class="greet">Привіт,&nbsp;</span>
    <span class="name">{{ authStore.username }}</span>
  </div>
  <button @click="showLogoutConfirm = true" class="exit-btn">➔</button>
</div>

          <router-link to="/checkout" class="action-btn cart-btn">
            <span class="icon">🛒</span> Кошик
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
    <AppConfirm
      :show="showLogoutConfirm"
      title="Вихід"
      message="Йдеш з поля? Твій кошик буде очищено 🔒"
      confirmText="Вийти"
      cancelText="Залишитись"
      @confirm="handleLogout"
      @cancel="showLogoutConfirm = false"
    />
  </div>
</template>

<style>
:root {
  --neon: #00ff88;
  --indigo: #6366f1;
  --bg-dark: #050811;
}

body {
  margin: 0;
  background: var(--bg-dark);
  font-family: 'Plus Jakarta Sans', sans-serif;
  color: #f8fafc;
}

.stadium-theme {
  min-height: 100vh;
  position: relative;
  /* Гарантуємо, що контент буде зверху */
  z-index: 1;
}

.pitch-markings {
  position: fixed; inset: 0; pointer-events: none; z-index: 0;
  background-image:
    radial-gradient(circle at 50% 50%, transparent 200px, rgba(255,255,255,0.02) 201px, transparent 202px),
    linear-gradient(to right, transparent 49.9%, rgba(255,255,255,0.02) 50%, transparent 50.1%);
}

.stadium-light { position: fixed; width: 600px; height: 600px; border-radius: 50%; filter: blur(120px); z-index: -1; opacity: 0.2; }
.light-left { background: var(--neon); top: -200px; left: -200px; }
.light-right { background: var(--indigo); bottom: -200px; right: -200px; }
</style>

<style scoped>
.glass-header {
  position: sticky; top: 0;
  z-index: 2000; /* Хедер має бути вище за все */
  background: rgba(11, 17, 33, 0.9);
  backdrop-filter: blur(15px);
  border-bottom: 1px solid rgba(255, 255, 255, 0.1);
}

.header-container {
  max-width: 1300px; margin: 0 auto; padding: 12px 25px;
  display: flex; justify-content: space-between; align-items: center;
}

.logo { display: flex; align-items: center; gap: 12px; text-decoration: none; }
.logo-circle {
  width: 45px; height: 45px; background: white; color: #050811;
  border-radius: 12px; display: flex; align-items: center; justify-content: center;
  font-weight: 900; font-size: 1.2rem;
}
.logo-text { font-size: 1.6rem; font-weight: 900; color: white; letter-spacing: -1px; }
.logo-text span { color: var(--neon); }

.header-actions { display: flex; align-items: center; gap: 15px; }

.action-btn {
  height: 48px; padding: 0 20px; border-radius: 14px;
  font-weight: 800; font-size: 0.95rem; cursor: pointer;
  transition: 0.3s; display: flex; align-items: center; gap: 10px;
  text-decoration: none; border: 1px solid rgba(255, 255, 255, 0.1);
  background: rgba(255, 255, 255, 0.05); color: #cbd5e1;
}

.action-btn:hover { background: rgba(255, 255, 255, 0.1); color: white; border-color: var(--neon); }

.cart-btn { background: var(--neon); color: #050811; border: none; }

.user-profile-badge {
  display: flex; align-items: center; gap: 12px;
  padding: 6px 15px; background: rgba(255, 255, 255, 0.05);
  border-radius: 16px; border: 1px solid rgba(255, 255, 255, 0.1);
}

.name { color: white; font-weight: 800; }
.content-area { position: relative; z-index: 10; max-width: 1300px; margin: 30px auto; }
</style>
