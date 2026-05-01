<script setup>
defineProps({
  show: Boolean,
  title: { type: String, default: 'Підтвердження' },
  message: { type: String, default: 'Ти точно впевнений?' },
  confirmText: { type: String, default: 'Так' },
  cancelText: { type: String, default: 'Скасувати' }
})

defineEmits(['confirm', 'cancel'])
</script>

<template>
  <Transition name="fade">
    <div v-if="show" class="modal-backdrop" @click.self="$emit('cancel')">
      <div class="modal-glass">
        <div class="icon-circle">👋</div>
        <h3 class="modal-title">{{ title }}</h3>
        <p class="modal-msg">{{ message }}</p>

        <div class="modal-actions">
          <button class="btn-cancel" @click="$emit('cancel')">{{ cancelText }}</button>
          <button class="btn-confirm" @click="$emit('confirm')">{{ confirmText }}</button>
        </div>
      </div>
    </div>
  </Transition>
</template>

<style scoped>
/* Затемнення фону та блокування натискань */
.modal-backdrop {
  position: fixed;
  top: 0;
  left: 0;
  width: 100vw;
  height: 100vh;
  background: rgba(15, 23, 42, 0.4);
  backdrop-filter: blur(8px);
  -webkit-backdrop-filter: blur(8px);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 999999;
}

/* Скляне вікно */
.modal-glass {
  background: rgba(255, 255, 255, 0.9);
  border: 1px solid rgba(255, 255, 255, 0.5);
  border-radius: 28px;
  padding: 30px;
  width: 90%;
  max-width: 360px;
  text-align: center;
  box-shadow: 0 25px 50px rgba(0, 0, 0, 0.15);
  transform: translateY(0);
}

.icon-circle {
  width: 60px;
  height: 60px;
  background: #f8fafc;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 2rem;
  margin: 0 auto 15px;
  box-shadow: 0 4px 15px rgba(0,0,0,0.05);
}

.modal-title {
  margin: 0 0 10px 0;
  font-size: 1.4rem;
  font-weight: 900;
  color: #0f172a;
}

.modal-msg {
  margin: 0 0 25px 0;
  color: #64748b;
  font-weight: 600;
  font-size: 0.95rem;
  line-height: 1.5;
}

/* Кнопки */
.modal-actions {
  display: flex;
  gap: 12px;
}

.btn-cancel, .btn-confirm {
  flex: 1;
  padding: 14px;
  border-radius: 14px;
  font-weight: 800;
  font-size: 0.95rem;
  cursor: pointer;
  transition: 0.2s;
  border: none;
}

.btn-cancel {
  background: #f1f5f9;
  color: #475569;
}
.btn-cancel:hover {
  background: #e2e8f0;
  color: #0f172a;
}

.btn-confirm {
  background: #ef4444; /* Червоний колір для виходу */
  color: white;
  box-shadow: 0 4px 15px rgba(239, 68, 68, 0.3);
}
.btn-confirm:hover {
  background: #dc2626;
  transform: translateY(-2px);
}

/* Анімації Transition */
.fade-enter-active, .fade-leave-active {
  transition: opacity 0.3s ease, transform 0.3s ease;
}
.fade-enter-from, .fade-leave-to {
  opacity: 0;
}
.fade-enter-from .modal-glass, .fade-leave-to .modal-glass {
  transform: scale(0.9) translateY(20px);
}
</style>
