<script setup>
defineProps({
  show: Boolean,
  title: String,
  message: String
})
defineEmits(['close'])
</script>

<template>
  <Transition name="fade">
    <div v-if="show" class="admin-modal-overlay" @click.self="$emit('close')">
      <div class="admin-modal-content">
        <div class="modal-icon">✅</div>
        <h3>{{ title || 'Успішно' }}</h3>
        <p>{{ message }}</p>
        <button class="modal-ok-btn" @click="$emit('close')">Зрозуміло</button>
      </div>
    </div>
  </Transition>
</template>

<style scoped>
.admin-modal-overlay {
  position: fixed; top: 0; left: 0; width: 100%; height: 100%;
  background: rgba(0, 0, 0, 0.7); backdrop-filter: blur(5px);
  display: flex; align-items: center; justify-content: center; z-index: 10000;
}

.admin-modal-content {
  background: #1e293b; border: 1px solid rgba(255, 255, 255, 0.1);
  padding: 30px; border-radius: 24px; text-align: center;
  max-width: 400px; width: 90%; box-shadow: 0 25px 50px -12px rgba(0, 0, 0, 0.5);
}

.modal-icon { font-size: 3rem; margin-bottom: 15px; }

h3 { color: white; font-size: 1.5rem; margin-bottom: 10px; font-weight: 800; }

p { color: #94a3b8; font-size: 1rem; margin-bottom: 25px; line-height: 1.5; }

.modal-ok-btn {
  background: linear-gradient(135deg, #10b981 0%, #059669 100%);
  color: white; border: none; padding: 12px 40px; border-radius: 14px;
  font-weight: 800; font-size: 1rem; cursor: pointer; transition: 0.3s;
  box-shadow: 0 10px 20px rgba(16, 185, 129, 0.2);
}

.modal-ok-btn:hover { transform: translateY(-2px); box-shadow: 0 15px 25px rgba(16, 185, 129, 0.3); }

/* Анімація */
.fade-enter-active, .fade-leave-active { transition: opacity 0.3s ease; }
.fade-enter-from, .fade-leave-to { opacity: 0; }
.fade-enter-active .admin-modal-content { animation: zoom 0.3s ease; }

@keyframes zoom {
  from { transform: scale(0.8); opacity: 0; }
  to { transform: scale(1); opacity: 1; }
}
</style>
