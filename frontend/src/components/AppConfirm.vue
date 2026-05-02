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
        <div class="exit-icon">👋</div>
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
/* ТЕМНИЙ ФОН ТА РОЗМИТТЯ */
.modal-backdrop {
  position: fixed;
  top: 0;
  left: 0;
  width: 100vw;
  height: 100vh;
  background: rgba(11, 15, 25, 0.85); /* Глибокий темний */
  backdrop-filter: blur(12px);
  -webkit-backdrop-filter: blur(12px);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 999999;
}

/* СТЙЛЬНА СКЛЯНА КАРТКА */
.modal-glass {
  background: rgba(17, 24, 39, 0.95); /* Темний фон картки */
  border: 1px solid rgba(255, 255, 255, 0.1); /* Тонка світла рамка */
  border-radius: 32px;
  padding: 40px;
  width: 90%;
  max-width: 400px;
  text-align: center;
  box-shadow: 0 30px 60px rgba(0, 0, 0, 0.5), 0 0 40px rgba(0, 255, 136, 0.05);
  transform: translateY(0);
  transition: transform 0.3s cubic-bezier(0.175, 0.885, 0.32, 1.275);
}

.exit-icon {
  font-size: 3.5rem;
  margin-bottom: 20px;
}

.modal-title {
  margin: 0 0 10px 0;
  font-size: 1.8rem;
  font-weight: 900;
  color: white; /* Білий заголовок */
}

.modal-msg {
  margin: 0 0 30px 0;
  color: #94a3b8; /* Сірий текст */
  font-weight: 600;
  font-size: 1rem;
  line-height: 1.6;
}

/* КНОПКИ */
.modal-actions {
  display: flex;
  gap: 15px;
}

.btn-cancel, .btn-confirm {
  flex: 1;
  padding: 16px;
  border-radius: 16px;
  font-weight: 800;
  font-size: 1rem;
  cursor: pointer;
  transition: 0.3s;
  border: none;
}

/* Кнопка "Залишитись" */
.btn-cancel {
  background: rgba(255, 255, 255, 0.05);
  color: #cbd5e1;
  border: 1px solid rgba(255, 255, 255, 0.1);
}
.btn-cancel:hover {
  background: rgba(255, 255, 255, 0.1);
  color: #00ff88;
  border-color: #00ff88;
}

/* Кнопка "Вийти" */
.btn-confirm {
  background: #ef4444;
  color: white;
  box-shadow: 0 10px 20px rgba(239, 68, 68, 0.2);
}
.btn-confirm:hover {
  background: #dc2626;
  transform: translateY(-3px);
  box-shadow: 0 15px 30px rgba(239, 68, 68, 0.4);
}

/* АНІМАЦІЇ */
.fade-enter-active, .fade-leave-active {
  transition: opacity 0.3s ease;
}
.fade-enter-from, .fade-leave-to {
  opacity: 0;
}
.fade-enter-active .modal-glass, .fade-leave-active .modal-glass {
  transition: all 0.3s cubic-bezier(0.175, 0.885, 0.32, 1.275);
}
.fade-enter-from .modal-glass, .fade-leave-to .modal-glass {
  transform: scale(0.9) translateY(20px);
}
</style>
