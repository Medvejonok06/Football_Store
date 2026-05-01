<script setup>
import { ref } from 'vue'
import { useRouter } from 'vue-router'

const props = defineProps({
  product: { type: Object, required: true }
})

const emit = defineEmits(['close', 'confirm-add'])
const router = useRouter()

// Список розмірів (можна потім брати з бази)
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
      <div v-if="!isAdded">
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
      <div v-else>
        <div class="success-icon">✅</div>
        <h3>Додано в кошик!</h3>
        <p class="product-name">{{ product.name }} (Розмір: {{ selectedSize }})</p>

        <div class="actions">
          <button class="btn-primary" @click="goToCart">Оформити замовлення</button>
          <button class="btn-secondary" @click="$emit('close')">Продовжити покупки</button>
        </div>
      </div>

    </div>
  </div>
</template>

<style scoped>
/* Додай ці стилі до існуючих у AddToCartModal.vue */
.sizes-grid {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 10px;
  margin: 20px 0 30px;
}

.size-btn {
  background: rgba(255, 255, 255, 0.05);
  border: 1px solid rgba(255, 255, 255, 0.1);
  color: white;
  padding: 12px;
  border-radius: 12px;
  font-weight: 800;
  cursor: pointer;
  transition: 0.3s;
}

.size-btn:hover { border-color: #00ff88; }
.size-btn.active {
  background: #00ff88;
  color: #0f172a;
  border-color: #00ff88;
  box-shadow: 0 0 15px rgba(0, 255, 136, 0.4);
}

.btn-primary:disabled {
  opacity: 0.3;
  cursor: not-allowed;
  filter: grayscale(1);
}
/* ... решта стилів з минулого повідомлення ... */
</style>
