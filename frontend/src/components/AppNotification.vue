<script setup>
import { ref, onMounted } from 'vue'

defineProps(['message', 'type'])
const emit = defineEmits(['close'])
const visible = ref(false)

onMounted(() => {
  visible.value = true
  // Закриття через 3 секунди
  setTimeout(() => {
    visible.value = false
    setTimeout(() => emit('close'), 500) // затримка для завершення анімації виходу
  }, 3000)
})
</script>

<template>
  <Transition name="toast">
    <div v-if="visible" class="notification-container" :class="type">
      <div class="glass-toast">
        <div class="content">
          <div class="icon-box">
            <span v-if="type === 'success'">✅</span>
            <span v-else-if="type === 'info'">👟</span>
            <span v-else>ℹ️</span>
          </div>
          <p class="msg">{{ message }}</p>
        </div>
        <div class="timer-bar">
          <div class="timer-fill" :class="type"></div>
        </div>
      </div>
    </div>
  </Transition>
</template>

<style scoped>
.notification-container {
  position: fixed;
  top: 30px;
  right: 30px;
  z-index: 999999;
  width: 320px;
  pointer-events: none;
}

.glass-toast {
  pointer-events: auto;
  background: rgba(255, 255, 255, 0.85);
  backdrop-filter: blur(15px);
  -webkit-backdrop-filter: blur(15px);
  border: 1px solid rgba(255, 255, 255, 0.4);
  border-radius: 20px;
  padding: 16px;
  box-shadow: 0 20px 40px rgba(0, 0, 0, 0.1);
  overflow: hidden;
  position: relative;
}

.content {
  display: flex;
  align-items: center;
  gap: 15px;
}

.icon-box {
  width: 40px;
  height: 40px;
  background: white;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 1.2rem;
  box-shadow: 0 4px 10px rgba(0, 0, 0, 0.05);
  flex-shrink: 0;
}

.msg {
  margin: 0;
  font-size: 0.95rem;
  font-weight: 800;
  color: #1e293b;
  line-height: 1.4;
}

/* Таймер внизу */
.timer-bar {
  position: absolute;
  bottom: 0;
  left: 0;
  width: 100%;
  height: 4px;
  background: rgba(0, 0, 0, 0.02);
}

.timer-fill {
  height: 100%;
  width: 100%;
  animation: shrink 3s linear forwards;
}

.timer-fill.success { background: linear-gradient(90deg, #10b981, #34d399); }
.timer-fill.info { background: linear-gradient(90deg, #6366f1, #a855f7); }

@keyframes shrink {
  from { width: 100%; }
  to { width: 0%; }
}

/* Анімації Transition */
.toast-enter-active, .toast-leave-active {
  transition: all 0.5s cubic-bezier(0.175, 0.885, 0.32, 1.275);
}

.toast-enter-from {
  opacity: 0;
  transform: translateX(50px) scale(0.8);
}

.toast-leave-to {
  opacity: 0;
  transform: scale(0.7) translateY(-20px);
}
</style>
