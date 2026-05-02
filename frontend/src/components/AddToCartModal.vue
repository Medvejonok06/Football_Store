<script setup>
import { ref } from 'vue'
import { useRouter } from 'vue-router'

defineProps({
  product: { type: Object, required: true }
})

const emit = defineEmits(['close', 'confirm-add'])
const router = useRouter()

// Список розмірів (можна потім брати з бази через props)
const sizes = ['39', '40', '41', '42', '43', '44', '45']
const selectedSize = ref(null)
const isAdded = ref(false)

const handleConfirm = () => {
  if (!selectedSize.value) return

  // Надсилаємо розмір у HomeView
  emit('confirm-add', selectedSize.value)

  // Показуємо крок з успіхом (зелена галочка)
  isAdded.value = true
}

const goToCart = () => {
  router.push('/checkout')
}
</script>

<template>
  <div class="modal-backdrop" @click.self="$emit('close')">
    <div class="modal-glass">

      <!-- КРОК 1: ВИБІР РОЗМІРУ -->
      <div v-if="!isAdded" class="step-container">
        <h3>Обери розмір</h3>
        <p class="product-name">{{ product.name }}</p>

        <div class="sizes-grid">
          <button
            v-for="size in sizes"
            :key="size"
            class="size-btn"
            :class="{ active: selectedSize === size }"
            @click="selectedSize = size"
          >
            {{ size }}
          </button>
        </div>

        <div class="actions">
          <button class="btn-primary" :disabled="!selectedSize" @click="handleConfirm">
            Додати в кошик
          </button>
          <button class="btn-secondary" @click="$emit('close')">Скасувати</button>
        </div>
      </div>

      <!-- КРОК 2: ПІДТВЕРДЖЕННЯ -->
      <div v-else class="step-container">
        <div class="success-icon">✅</div>
        <h3>Додано в кошик!</h3>
        <p class="product-name">{{ product.name }} <br><span class="highlight-size">Розмір: {{ selectedSize }}</span></p>

        <div class="actions">
          <button class="btn-primary" @click="goToCart">Оформити замовлення 🚀</button>
          <button class="btn-secondary" @click="$emit('close')">Продовжити покупки</button>
        </div>
      </div>

    </div>
  </div>
</template>

<style scoped>
/* ТЕМНИЙ ФОН І ЦЕНТРУВАННЯ */
.modal-backdrop {
  position: fixed;
  top: 0;
  left: 0;
  width: 100vw;
  height: 100vh;
  background: rgba(11, 15, 25, 0.85); /* Затемнення */
  backdrop-filter: blur(12px); /* Розмиття заднього фону */
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 999999;
}

/* СКЛЯНА КАРТКА */
.modal-glass {
  background: rgba(17, 24, 39, 0.95);
  border: 1px solid rgba(255, 255, 255, 0.12);
  border-radius: 32px;
  padding: 40px;
  width: 90%;
  max-width: 420px;
  text-align: center;
  box-shadow: 0 30px 60px rgba(0, 0, 0, 0.5), 0 0 40px rgba(0, 255, 136, 0.05);
  animation: popIn 0.3s cubic-bezier(0.175, 0.885, 0.32, 1.275);
}

@keyframes popIn {
  from { opacity: 0; transform: scale(0.9) translateY(20px); }
  to { opacity: 1; transform: scale(1) translateY(0); }
}

/* ТИПОГРАФІКА */
.step-container h3 {
  margin: 0 0 10px 0;
  font-size: 1.8rem;
  font-weight: 900;
  color: white;
}

.product-name {
  color: #94a3b8;
  font-size: 1rem;
  line-height: 1.5;
  font-weight: 600;
  margin-bottom: 25px;
  text-transform: uppercase;
}

.highlight-size {
  color: #00ff88;
  font-weight: 800;
}

.success-icon {
  font-size: 4rem;
  margin-bottom: 15px;
  filter: drop-shadow(0 10px 15px rgba(0, 255, 136, 0.2));
}

/* СІТКА РОЗМІРІВ */
.sizes-grid {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 12px;
  margin-bottom: 30px;
}

.size-btn {
  background: rgba(255, 255, 255, 0.05);
  border: 1px solid rgba(255, 255, 255, 0.1);
  color: white;
  padding: 14px 0;
  border-radius: 14px;
  font-size: 1.1rem;
  font-weight: 900;
  cursor: pointer;
  transition: 0.3s;
}

.size-btn:hover {
  border-color: #00ff88;
  color: #00ff88;
  background: rgba(0, 255, 136, 0.05);
}

.size-btn.active {
  background: #00ff88;
  color: #0f172a;
  border-color: #00ff88;
  box-shadow: 0 0 20px rgba(0, 255, 136, 0.3);
  transform: scale(1.05);
}

/* КНОПКИ ДІЙ */
.actions {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.btn-primary {
  background: #00ff88;
  color: #0f172a;
  border: none;
  padding: 16px;
  border-radius: 16px;
  font-weight: 900;
  font-size: 1.05rem;
  cursor: pointer;
  transition: 0.3s;
}

.btn-primary:hover:not(:disabled) {
  transform: translateY(-3px);
  box-shadow: 0 10px 20px rgba(0, 255, 136, 0.3);
}

.btn-primary:disabled {
  opacity: 0.4;
  cursor: not-allowed;
  filter: grayscale(1);
}

.btn-secondary {
  background: rgba(255, 255, 255, 0.05);
  color: white;
  border: 1px solid rgba(255, 255, 255, 0.1);
  padding: 16px;
  border-radius: 16px;
  font-weight: 800;
  font-size: 1.05rem;
  cursor: pointer;
  transition: 0.3s;
}

.btn-secondary:hover {
  background: rgba(255, 255, 255, 0.1);
  border-color: #00ff88;
  color: #00ff88;
}
</style>
