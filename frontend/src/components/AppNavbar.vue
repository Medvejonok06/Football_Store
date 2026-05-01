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
  <nav class="navbar glass-effect">
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

      <div class="user-pill" @click="handleLogout">
        <span class="user-emoji">😎</span>
        <div class="user-details">
          <span class="user-prefix">ПРИВІТ,</span>
          <span class="user-name">{{ authStore.user?.username || 'medvejonok' }}</span>
        </div>
      </div>

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

.logo-badge {
  background: white;
  color: #050811;
  border-radius: 12px;
  font-weight: 900;
  padding: 8px 12px;
}

.logo-text { color: white; }
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
  padding: 5px 15px;
  background: rgba(255, 255, 255, 0.03);
  border-radius: 16px;
  border: 1px solid rgba(255, 255, 255, 0.05);
  cursor: pointer;
}

.user-pill:hover { border-color: rgba(255, 255, 255, 0.2); }

.user-prefix { color: #64748b; font-size: 0.6rem; font-weight: 800; }
.user-name { color: white; font-weight: 800; font-size: 0.9rem; }
</style>
