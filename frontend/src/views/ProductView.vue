<script setup>
import { ref, computed, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import axios from 'axios'
import { useCartStore } from '../stores/cart'
import AppNotification from '../components/AppNotification.vue'

const route = useRoute()
const router = useRouter()
const cartStore = useCartStore()

const product = ref(null)
const similarProducts = ref([])
const isLoading = ref(true)
const selectedSize = ref(null)

// СТАН ДЛЯ СПОВІЩЕНЬ
const notification = ref({
  show: false,
  message: '',
  type: 'success'
})

const showToast = (msg, type = 'success') => {
  notification.value.show = false
  setTimeout(() => {
    notification.value.message = msg
    notification.value.type = type
    notification.value.show = true
  }, 10)
}

const currentImageIndex = ref(0)

// МАСИВИ РОЗМІРІВ
const shoeSizes = [36, 37, 38, 39, 40, 41, 42, 43, 44, 45, 46, 47]
const clothingSizes = ['S', 'M', 'L', 'XL', 'XXL']
const sockSizes = ['36-39', '39-42', '42-45', '45-48']

// ДОПОМІЖНІ ЗМІННІ
const catName = computed(() => (product.value?.category_name || '').toLowerCase())
const prodName = computed(() => (product.value?.name || '').toLowerCase())

const isShoeCategory = computed(() => {
  return catName.value.includes('бутси') || catName.value.includes('сороконіжки') ||
         catName.value.includes('футзалки') || catName.value.includes('взуття')
})

const isClothingCategory = computed(() => {
  return catName.value.includes('форма') || catName.value.includes('одяг') ||
         catName.value.includes('футболка') || catName.value.includes('шорти') ||
         catName.value.includes('костюм') || prodName.value.includes('костюм')
})

const isSocksCategory = computed(() => {
  return catName.value.includes('носки') || catName.value.includes('шкарпетки')
})

const isBallCategory = computed(() => {
  return catName.value.includes('м\'яч') || catName.value.includes('мяч')
})

const needsSize = computed(() => isShoeCategory.value || isClothingCategory.value || isSocksCategory.value)

const currentSizes = computed(() => {
  if (isSocksCategory.value) return sockSizes
  if (isShoeCategory.value) return shoeSizes
  if (isClothingCategory.value) return clothingSizes
  return []
})

const sizeLabelText = computed(() => isShoeCategory.value ? 'Розмір (EU):' : 'Розмір:')

// --- 🎁 ПРОМО-АКЦІЯ ---
const applyPromo = (prod) => {
  if (!prod || !prod.name || !prod.price) return prod
  if (prod.name.toLowerCase().includes('nike')) {
    return {
      ...prod,
      original_price: prod.price,
      price: Math.round(Number(prod.price) * 0.8),
      is_promo: true
    }
  }
  return prod
}

const fetchData = async () => {
  if (!route.params.id) return
  isLoading.value = true
  selectedSize.value = null
  currentImageIndex.value = 0

  try {
    const res = await axios.get(`http://127.0.0.1:8000/api/products/${route.params.id}/`)
    product.value = applyPromo(res.data)

    const allRes = await axios.get('http://127.0.0.1:8000/api/products/')
    const allProductsRaw = Array.isArray(allRes.data) ? allRes.data : (allRes.data.results || [])
    similarProducts.value = allProductsRaw.filter(p => {
      const isSameCategory = String(p.category) === String(product.value.category)
      return isSameCategory && String(p.id) !== String(product.value.id)
    }).map(applyPromo).slice(0, 4)

  } catch (error) {
    showToast('Не вдалося завантажити товар', 'error')
  } finally {
    isLoading.value = false
    window.scrollTo({ top: 0, behavior: 'smooth' })
  }
}

watch(() => route.params.id, fetchData, { immediate: true })

// ГАЛЕРЕЯ
const allImages = computed(() => {
  if (!product.value) return []
  let images = [product.value.image]
  if (product.value.images && product.value.images.length > 0) {
    images = images.concat(product.value.images.map(img => img.image))
  }
  return images.filter(img => img)
})

const currentImage = computed(() => allImages.value[currentImageIndex.value] || '')
const nextImage = () => currentImageIndex.value = (currentImageIndex.value + 1) % allImages.value.length
const prevImage = () => currentImageIndex.value = (currentImageIndex.value - 1 + allImages.value.length) % allImages.value.length
const setMainImage = (index) => currentImageIndex.value = index

const addToCart = () => {
  if (needsSize.value && !selectedSize.value) {
    showToast('Будь ласка, оберіть розмір! 📏', 'info')
    return
  }

  cartStore.addToCart({
    ...product.value,
    selectedSize: selectedSize.value || (isBallCategory.value ? '5' : 'One Size')
  })

  showToast(`✅ ${product.value.name} додано до кошика!`, 'success')
}
</script>

<template>
  <div class="product-page">
    <AppNotification
      v-if="notification.show"
      :message="notification.message"
      :type="notification.type"
      @close="notification.show = false"
    />

    <div class="header-simple">
      <button class="back-btn" @click="router.push('/')">← Назад до каталогу</button>
    </div>

    <div v-if="!isLoading && product" class="product-layout">
      <!-- ЛІВА КОЛОНКА: ГАЛЕРЕЯ -->
      <div class="gallery-section">
        <div class="main-image-wrapper glass-card">
          <div v-if="product.is_promo" class="promo-tag-big">ЮВІЛЕЙНА ЗНИЖКА -20%</div>
          <button v-if="allImages.length > 1" class="nav-arrow prev" @click="prevImage">❮</button>
          <img :src="currentImage" :alt="product.name" class="main-img">
          <button v-if="allImages.length > 1" class="nav-arrow next" @click="nextImage">❯</button>
        </div>
        <div class="thumbnails-grid" v-if="allImages.length > 1">
          <div
            v-for="(img, index) in allImages" :key="index"
            class="thumb-box glass-card"
            :class="{ active: currentImageIndex === index }"
            @click="setMainImage(index)"
          >
            <img :src="img" class="thumb-img">
          </div>
        </div>
      </div>

      <!-- ПРАВА КОЛОНКА: ІНФО -->
      <div class="info-section">
        <div class="info-glass glass-card">
          <span class="category-path">{{ product.category_name }}</span>
          <h1 class="product-title">{{ product.name }}</h1>

          <div class="price-box">
            <div class="price-values">
              <span v-if="product.is_promo" class="old-price-val">{{ product.original_price }} ₴</span>
              <span class="current-price" :class="{ 'promo-color': product.is_promo }">{{ product.price }} ₴</span>
            </div>
            <div class="stock-badge" :class="product.stock > 0 ? 'in' : 'out'">
              {{ product.stock > 0 ? 'В наявності' : 'Немає' }}
            </div>
          </div>

          <div class="size-selector-block">
            <div class="size-header">
              <h3>{{ sizeLabelText }}</h3>
              <span class="selected-val">{{ selectedSize || 'Оберіть зі списку' }}</span>
            </div>

            <div v-if="needsSize" class="sizes-container">
              <button
                v-for="size in currentSizes" :key="size"
                class="size-chip"
                :class="{ active: selectedSize === size }"
                @click="selectedSize = size"
              >
                {{ size }}
              </button>
            </div>
            <div v-else class="one-size-info">
              <span class="info-icon">ℹ️</span>
              {{ isBallCategory ? 'Розмір: 5 (Стандарт)' : 'Універсальний розмір' }}
            </div>
          </div>

          <button
            class="add-to-cart-btn"
            :class="{ 'btn-disabled': product.stock <= 0 }"
            @click="addToCart"
            :disabled="product.stock <= 0"
          >
            {{ product.stock > 0 ? (selectedSize || !needsSize ? 'Додати до кошика 🛍️' : 'Оберіть розмір') : 'Товар закінчився' }}
          </button>
        </div>

        <div class="description-glass glass-card">
          <h3>Опис та характеристики</h3>
          <p>{{ product.description || 'Детальний опис цієї моделі скоро з\'явиться.' }}</p>
        </div>
      </div>
    </div>

    <!-- LOADERS -->
    <div v-else-if="isLoading" class="loader-wrap">
      <div class="ball-spinner"></div>
      <p>Готуємо товар до перегляду...</p>
    </div>
  </div>
</template>

<style scoped>
.product-page { max-width: 1300px; margin: 0 auto; padding: 40px 20px; color: white; }

/* КНОПКА НАЗАД */
.back-btn {
  background: rgba(255, 255, 255, 0.05); border: 1px solid rgba(255, 255, 255, 0.1);
  padding: 12px 24px; border-radius: 14px; color: #94a3b8; font-weight: 800;
  cursor: pointer; transition: 0.3s; margin-bottom: 30px;
}
.back-btn:hover { border-color: #00ff88; color: #00ff88; transform: translateX(-5px); }

/* LAYOUT */
.product-layout { display: grid; grid-template-columns: 1.2fr 1fr; gap: 40px; align-items: start; }

.glass-card {
  background: rgba(17, 24, 39, 0.7); backdrop-filter: blur(20px);
  border: 1px solid rgba(255, 255, 255, 0.1); border-radius: 32px;
  box-shadow: 0 20px 50px rgba(0, 0, 0, 0.3);
}

/* ГАЛЕРЕЯ */
.main-image-wrapper {
  aspect-ratio: 1/1; display: flex; align-items: center; justify-content: center;
  position: relative; overflow: hidden; padding: 40px;
}
.main-img { max-width: 100%; max-height: 100%; object-fit: contain; transition: 0.5s; }
.main-image-wrapper:hover .main-img { transform: scale(1.05) rotate(-2deg); }

.promo-tag-big {
  position: absolute; top: 25px; left: 25px; background: #ef4444; color: white;
  padding: 8px 20px; border-radius: 12px; font-weight: 900; z-index: 5;
  box-shadow: 0 10px 20px rgba(239, 68, 68, 0.4);
}

.nav-arrow {
  position: absolute; top: 50%; transform: translateY(-50%);
  background: rgba(0, 0, 0, 0.5); border: none; color: white;
  width: 50px; height: 50px; border-radius: 50%; cursor: pointer; transition: 0.3s;
}
.nav-arrow:hover { background: #00ff88; color: #0f172a; }
.prev { left: 20px; } .next { right: 20px; }

.thumbnails-grid { display: flex; gap: 15px; margin-top: 20px; overflow-x: auto; padding-bottom: 10px; }
.thumb-box { width: 100px; height: 100px; padding: 10px; cursor: pointer; transition: 0.3s; flex-shrink: 0; }
.thumb-box.active { border-color: #00ff88; background: rgba(0, 255, 136, 0.05); }
.thumb-img { width: 100%; height: 100%; object-fit: contain; }

/* ІНФОРМАЦІЯ */
.info-glass { padding: 40px; margin-bottom: 25px; }
.category-path { color: #00ff88; font-weight: 800; text-transform: uppercase; font-size: 0.85rem; letter-spacing: 1px; }
.product-title { font-size: 2.5rem; font-weight: 900; margin: 10px 0 25px; line-height: 1.2; }

.price-box { display: flex; justify-content: space-between; align-items: flex-end; margin-bottom: 40px; }
.price-values { display: flex; flex-direction: column; }
.old-price-val { text-decoration: line-through; color: #64748b; font-size: 1.2rem; font-weight: 800; }
.current-price { font-size: 3rem; font-weight: 900; }
.promo-color { color: #00ff88; }

.stock-badge { padding: 6px 16px; border-radius: 20px; font-weight: 800; font-size: 0.85rem; }
.stock-badge.in { background: rgba(0, 255, 136, 0.1); color: #00ff88; border: 1px solid rgba(0, 255, 136, 0.3); }
.stock-badge.out { background: rgba(239, 68, 68, 0.1); color: #ef4444; border: 1px solid rgba(239, 68, 68, 0.3); }

/* ВИБІР РОЗМІРУ */
.size-selector-block { margin-bottom: 40px; }
.size-header { display: flex; justify-content: space-between; margin-bottom: 15px; }
.size-header h3 { font-size: 1.1rem; font-weight: 800; color: white; margin: 0; }
.selected-val { color: #00ff88; font-weight: 900; }

.sizes-container { display: grid; grid-template-columns: repeat(auto-fill, minmax(70px, 1fr)); gap: 12px; }
.size-chip {
  background: rgba(255, 255, 255, 0.05); border: 1px solid rgba(255, 255, 255, 0.1);
  padding: 15px 0; border-radius: 14px; color: white; font-weight: 800; cursor: pointer; transition: 0.3s;
}
.size-chip:hover { border-color: #00ff88; color: #00ff88; }
.size-chip.active { background: #00ff88; color: #0f172a; border-color: #00ff88; box-shadow: 0 0 20px rgba(0, 255, 136, 0.3); }

.one-size-info {
  background: rgba(99, 102, 241, 0.1); border: 1px solid rgba(99, 102, 241, 0.3);
  padding: 20px; border-radius: 16px; color: #818cf8; font-weight: 800; display: flex; gap: 10px;
}

/* КНОПКА КУПИТИ */
.add-to-cart-btn {
  width: 100%; background: white; color: #0f172a; border: none; padding: 22px;
  border-radius: 20px; font-weight: 900; font-size: 1.2rem; cursor: pointer; transition: 0.4s;
}
.add-to-cart-btn:hover { background: #00ff88; transform: translateY(-5px); box-shadow: 0 15px 30px rgba(0, 255, 136, 0.3); }
.btn-disabled { opacity: 0.5; cursor: not-allowed; filter: grayscale(1); }

/* ОПИС */
.description-glass { padding: 40px; }
.description-glass h3 { margin-top: 0; font-size: 1.4rem; color: #00ff88; margin-bottom: 20px; }
.description-glass p { color: #94a3b8; line-height: 1.8; font-size: 1.05rem; }

/* LOADERS */
.loader-wrap { text-align: center; padding: 100px 0; }
.ball-spinner {
  width: 50px; height: 50px; border: 5px solid rgba(255, 255, 255, 0.1);
  border-top-color: #00ff88; border-radius: 50%; animation: spin 1s linear infinite; margin: 0 auto 20px;
}
@keyframes spin { to { transform: rotate(360deg); } }

@media (max-width: 1000px) {
  .product-layout { grid-template-columns: 1fr; }
  .product-title { font-size: 2rem; }
}
</style>
