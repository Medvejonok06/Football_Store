<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import axios from 'axios'
import { useCartStore } from '../stores/cart'

const route = useRoute()
const router = useRouter()
const cartStore = useCartStore()

const product = ref(null)
const isLoading = ref(true)

const selectedSize = ref(null)
const selectedColor = ref(null)

// --- ЛОГІКА КАРУСЕЛІ ---
const currentPhotoIndex = ref(0)
const photos = ref([]) // Масив для фотографій

onMounted(async () => {
  try {
    const response = await axios.get(`http://127.0.0.1:8000/api/products/${route.params.id}/`)
    product.value = response.data

    // ТЕПЕР МИ БЕРЕМО РЕАЛЬНІ ФОТО З ГАЛЕРЕЇ
    const gallery = product.value.images.map(img => img.image)

    // Додаємо головне фото на початок, а потім всі додаткові
    photos.value = [product.value.image, ...gallery]

  } catch (error) {
    console.error('Помилка завантаження:', error)
  } finally {
    isLoading.value = false
  }
})

// Наступна фотографія
const nextPhoto = () => {
  if (photos.value.length === 0) return
  currentPhotoIndex.value = (currentPhotoIndex.value + 1) % photos.value.length
}

// Попередня фотографія
const prevPhoto = () => {
  if (photos.value.length === 0) return
  currentPhotoIndex.value = (currentPhotoIndex.value - 1 + photos.value.length) % photos.value.length
}

// Вибір фотографії через мініатюру
const selectPhoto = (index) => {
  currentPhotoIndex.value = index
}

// --- РОЗМІРИ ТА КОЛІР ---
const availableSizes = computed(() => {
  if (!product.value) return []
  const cat = (product.value.category_name || '').toLowerCase()
  const name = (product.value.name || '').toLowerCase()
  const textToCheck = cat + ' ' + name

  if (textToCheck.includes('м\'яч') || textToCheck.includes('мяч')) {
    return ['3', '4', '5']
  } else if (
    textToCheck.includes('бутс') || textToCheck.includes('взуття') || textToCheck.includes('сороконіж') ||
    textToCheck.includes('футзалк') || textToCheck.includes('бамп') || textToCheck.includes('кросівк') ||
    textToCheck.includes('lunargato')
  ) {
    return Array.from({ length: 12 }, (_, i) => (36 + i).toString())
  } else {
    return ['XS', 'S', 'M', 'L', 'XL']
  }
})

const availableColors = [
  { name: 'Black', hex: '#1e293b' },
  { name: 'White', hex: '#f8fafc' },
  { name: 'Red', hex: '#ef4444' },
  { name: 'Blue', hex: '#3b82f6' },
  { name: 'Neon', hex: '#00ff88' }
]

const addToCartWithVariations = () => {
  if (!selectedSize.value || !selectedColor.value) {
    alert('Будь ласка, оберіть розмір та колір перед додаванням у кошик!')
    return
  }
  const cartItem = {
    ...product.value,
    id: `${product.value.id}-${selectedSize.value}-${selectedColor.value.name}`,
    name: `${product.value.name} (${selectedSize.value}, ${selectedColor.value.name})`
  }
  cartStore.addToCart(cartItem)
  alert('Додано в кошик! 🛒')
}
</script>

<template>
  <div class="product-page">
    <button class="back-btn" @click="router.push('/')">← Назад до каталогу</button>

    <div v-if="isLoading" class="loading">Завантаження...</div>

    <div v-else-if="product" class="product-layout">

      <div class="product-visual">
        <div class="carousel-container">

          <div v-if="photos.length > 0" class="carousel-main">
            <button v-if="photos.length > 1" class="nav-btn prev-btn" @click="prevPhoto">←</button>
            <button v-if="photos.length > 1" class="nav-btn next-btn" @click="nextPhoto">→</button>

            <img :src="photos[currentPhotoIndex]" :alt="product.name" class="main-image-file">
          </div>

          <div v-else class="emoji-placeholder">⚽</div>

          <div v-if="photos.length > 1" class="carousel-thumbs">
            <div
              v-for="(photo, index) in photos" :key="index"
              class="thumb-wrapper"
              :class="{ 'active': index === currentPhotoIndex }"
              @click="selectPhoto(index)"
            >
              <img :src="photo" :alt="`${product.name} rakyrs ${index + 1}`">
            </div>
          </div>
        </div>
      </div>

      <div class="product-info">
        <span class="badge">{{ product.category_name }}</span>
        <h1>{{ product.name }}</h1>
        <p class="price">{{ product.price }} ₴</p>

        <div class="variation-block">
          <h3>Колір: <span>{{ selectedColor ? selectedColor.name : 'Не обрано' }}</span></h3>
          <div class="color-options">
            <button
              v-for="color in availableColors" :key="color.name" class="color-circle"
              :class="{ 'active': selectedColor?.name === color.name }"
              :style="{ backgroundColor: color.hex }" @click="selectedColor = color"
            ></button>
          </div>
        </div>

        <div class="variation-block">
          <h3>Розмір: <span>{{ selectedSize || 'Не обрано' }}</span></h3>
          <div class="size-options">
            <button
              v-for="size in availableSizes" :key="size" class="size-pill"
              :class="{ 'active': selectedSize === size }" @click="selectedSize = size"
            >
              {{ size }}
            </button>
          </div>
        </div>

        <div class="description-box">
          <h3>Про товар</h3>
          <p v-if="product.stud_type"><strong>Особливості:</strong> {{ product.stud_type }}</p>
          <p>{{ product.description }}</p>
        </div>

        <button class="buy-btn" :class="{ 'disabled': !selectedSize || !selectedColor }" @click="addToCartWithVariations">
          {{ (!selectedSize || !selectedColor) ? 'Оберіть розмір та колір' : 'Додати в кошик 🛒' }}
        </button>
      </div>
    </div>
  </div>
</template>

<style scoped>
.product-page { max-width: 1200px; margin: 0 auto; padding: 20px; }
.back-btn { background: none; border: none; color: #64748b; font-size: 1.1em; font-weight: 700; cursor: pointer; margin-bottom: 30px; transition: 0.2s; }
.back-btn:hover { color: #0f172a; transform: translateX(-5px); }

.loading { text-align: center; padding: 100px; font-size: 1.2rem; color: #64748b; font-weight: bold; }
.product-layout { display: grid; grid-template-columns: 1.5fr 1fr; gap: 40px; background: white; padding: 30px; border-radius: 32px; box-shadow: 0 10px 40px rgba(0,0,0,0.05); }

/* --- СТИЛІ КАРУСЕЛІ (НОВЕ) --- */
.product-visual { background: #f8fafc; border-radius: 24px; padding: 20px; height: 100%; }
.carousel-container { display: flex; flex-direction: column; gap: 15px; height: 100%; justify-content: space-between;}

/* Головна зона фотографії */
.carousel-main {
  position: relative;
  background: white;
  border-radius: 18px;
  display: flex;
  align-items: center;
  justify-content: center;
  height: 400px; /* Фіксована висота для каруселі */
  overflow: hidden;
  box-shadow: 0 4px 15px rgba(0,0,0,0.03);
}

/* Кнопки навігації */
.nav-btn {
  position: absolute; top: 50%; transform: translateY(-50%);
  background: rgba(255, 255, 255, 0.7); backdrop-filter: blur(5px);
  border: none; width: 40px; height: 40px; border-radius: 50%;
  font-size: 1.3rem; color: var(--dark); cursor: pointer; z-index: 5;
  transition: 0.2s; display: flex; align-items: center; justify-content: center;
}
.nav-btn:hover { background: var(--dark); color: white; transform: translateY(-50%) scale(1.1); }
.prev-btn { left: 15px; }
.next-btn { right: 15px; }

/* Головне фото */
.main-image-file { max-width: 100%; max-height: 100%; object-fit: contain; padding: 20px; transition: 0.3s cubic-bezier(0.175, 0.885, 0.32, 1.275); }

/* Емодзі, якщо фото немає */
.emoji-placeholder { font-size: 8rem; text-align: center; padding: 100px 0; }

/* Зона мініатюр */
.carousel-thumbs { display: flex; gap: 10px; justify-content: center; }
.thumb-wrapper {
  width: 70px; height: 70px; background: white; border-radius: 10px;
  cursor: pointer; overflow: hidden; transition: 0.2s;
  border: 2px solid #e2e8f0; display: flex; align-items: center; justify-content: center;
}
.thumb-wrapper img { width: 100%; height: 100%; object-fit: contain; padding: 5px; opacity: 0.7; }
.thumb-wrapper:hover { border-color: #cbd5e1; }
.thumb-wrapper:hover img { opacity: 1; }
.thumb-wrapper.active { border-color: var(--accent); box-shadow: 0 0 0 4px rgba(99, 102, 241, 0.1); }
.thumb-wrapper.active img { opacity: 1; }

/* ІНФОРМАЦІЯ */
.badge { background: #e0e7ff; color: #4f46e5; padding: 6px 14px; border-radius: 100px; font-weight: 800; font-size: 0.85rem; }
h1 { font-size: 2.2rem; font-weight: 900; color: #0f172a; margin: 10px 0; line-height: 1.1; }
.price { font-size: 1.8rem; font-weight: 900; color: #6366f1; margin-bottom: 25px; }

.variation-block { margin-bottom: 25px; }
.variation-block h3 { font-size: 0.95rem; font-weight: 700; color: #1e293b; margin-bottom: 10px; }
.variation-block h3 span { color: #94a3b8; font-weight: 600; }
.color-options { display: flex; gap: 12px; }
.color-circle { width: 36px; height: 36px; border-radius: 50%; border: 3px solid white; box-shadow: 0 4px 10px rgba(0,0,0,0.1); cursor: pointer; transition: 0.2s; }
.color-circle.active { transform: scale(1.15); box-shadow: 0 0 0 2px #0f172a; }
.size-options { display: flex; flex-wrap: wrap; gap: 8px; }
.size-pill { padding: 9px 18px; background: white; border: 2px solid #e2e8f0; border-radius: 12px; font-weight: 700; color: #64748b; cursor: pointer; transition: 0.2s; font-size: 0.9rem; }
.size-pill:hover { border-color: #94a3b8; }
.size-pill.active { background: #0f172a; color: white; border-color: #0f172a; }

.description-box { background: #f8fafc; padding: 15px; border-radius: 14px; margin-bottom: 25px; }
.description-box h3 { font-size: 1rem; margin-top: 0; margin-bottom: 8px; }
.description-box p { color: #475569; line-height: 1.5; margin: 0; font-size: 0.9rem; }

.buy-btn { width: 100%; padding: 18px; background: #0f172a; color: white; border: none; border-radius: 16px; font-size: 1.1rem; font-weight: 800; cursor: pointer; transition: 0.3s; }
.buy-btn:hover:not(.disabled) { background: #00ff88; color: #0f172a; transform: translateY(-3px); box-shadow: 0 10px 20px rgba(0,255,136,0.3); }
.buy-btn.disabled { background: #cbd5e1; cursor: not-allowed; color: #94a3b8; }

@media (max-width: 900px) {
  .product-layout { grid-template-columns: 1fr; }
}
</style>
