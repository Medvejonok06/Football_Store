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
  notification.value.message = msg
  notification.value.type = type
  notification.value.show = true
}

const currentImageIndex = ref(0)

// МАСИВИ РОЗМІРІВ
const shoeSizes = [36, 37, 38, 39, 40, 41, 42, 43, 44, 45, 46, 47]
const clothingSizes = ['S', 'M', 'L', 'XL', 'XXL']
const sockSizes = ['36-39', '39-42', '42-45', '45-48']

// ДОПОМІЖНІ ЗМІННІ З ПЕРЕВІРКОЮ НА ПУСТІ ЗНАЧЕННЯ
const catName = computed(() => (product.value?.category_name || '').toLowerCase())
const prodName = computed(() => (product.value?.name || '').toLowerCase())

// ЛОГІКА КАТЕГОРІЙ
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
  return catName.value.includes('носки') || catName.value.includes('шкарпетки') ||
         prodName.value.includes('носки') || prodName.value.includes('шкарпетки')
})

const isBallCategory = computed(() => {
  return catName.value.includes('м\'яч') || catName.value.includes('мяч') ||
         prodName.value.includes('м\'яч') || prodName.value.includes('мяч')
})

const needsSize = computed(() => isShoeCategory.value || isClothingCategory.value || isSocksCategory.value)

const currentSizes = computed(() => {
  if (isSocksCategory.value) return sockSizes
  if (isShoeCategory.value) return shoeSizes
  if (isClothingCategory.value) return clothingSizes
  return []
})

const sizeLabelText = computed(() => isShoeCategory.value ? 'Розмір (EU):' : 'Розмір:')

// --- 🎁 ПРОМО-АКЦІЯ З ПЕРЕВІРКОЮ ---
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
  if (!route.params.id) {
    isLoading.value = false
    return
  }

  isLoading.value = true
  selectedSize.value = null
  currentImageIndex.value = 0

  try {
    const res = await axios.get(`http://127.0.0.1:8000/api/products/${route.params.id}/`)
    product.value = applyPromo(res.data)

    const allRes = await axios.get('http://127.0.0.1:8000/api/products/')
    const allProductsRaw = Array.isArray(allRes.data) ? allRes.data : (allRes.data.results || [])

    similarProducts.value = allProductsRaw.filter(p => {
      const isSameCategory = String(p.category) === String(product.value.category) ||
                             (p.category_name && p.category_name === product.value.category_name)
      return isSameCategory && String(p.id) !== String(product.value.id)
    }).map(applyPromo)

  } catch (error) {
    console.error("Помилка завантаження:", error)
    showToast('Не вдалося завантажити товар', 'error')
  } finally {
    // isLoading ОБОВ'ЯЗКОВО має стати false тут
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
  return images.filter(img => img) // прибираємо пусті
})

const currentImage = computed(() => allImages.value[currentImageIndex.value] || '')

const nextImage = () => currentImageIndex.value = (currentImageIndex.value + 1) % allImages.value.length
const prevImage = () => currentImageIndex.value = (currentImageIndex.value - 1 + allImages.value.length) % allImages.value.length
const setMainImage = (index) => currentImageIndex.value = index

const addToCart = (itemToBuy = null, size = null) => {
  const targetProduct = itemToBuy || product.value
  const targetSize = size || selectedSize.value

  if (!itemToBuy && !targetSize && needsSize.value) {
    showToast('Будь ласка, оберіть розмір! 📏', 'info')
    return
  }

  cartStore.addToCart({
    id: targetSize ? `${targetProduct.id}-${targetSize}` : targetProduct.id,
    originalId: targetProduct.id,
    name: targetProduct.name,
    price: targetProduct.price,
    image: targetProduct.image,
    size: needsSize.value ? (targetSize || 'Не обрано') : (isBallCategory.value ? '5' : 'One Size'),
    quantity: 1
  })

  showToast(`✅ ${targetProduct.name} додано до кошика!`, 'success')
}

const cartButtonText = computed(() => {
  if (!needsSize.value) return 'Додати в кошик'
  return selectedSize.value ? 'Додати в кошик' : 'Оберіть розмір'
})
</script>

<template>
  <div class="product-page">
    <div class="header-simple">
      <button class="back-btn" @click="router.push('/')">← Назад до каталогу</button>
    </div>

    <AppNotification
      v-if="notification.show"
      :message="notification.message"
      :type="notification.type"
      @close="notification.show = false"
    />

    <div v-if="!isLoading && product" class="product-layout">
      <div class="product-top-row">
        <div class="product-gallery">
          <div class="main-image-box">
            <button v-if="allImages.length > 1" class="gallery-arrow prev" @click="prevImage">❮</button>
            <img :src="currentImage" :alt="product.name" class="main-img">
            <button v-if="allImages.length > 1" class="gallery-arrow next" @click="nextImage">❯</button>
          </div>
          <div class="thumbnails" v-if="allImages.length > 1">
            <img v-for="(img, index) in allImages" :key="index" :src="img" class="thumb" :class="{ active: currentImageIndex === index }" @click="setMainImage(index)">
          </div>
        </div>

        <div class="product-info">
          <div v-if="product.is_promo" class="promo-badge-top">🎉 Ювілейна знижка -20%</div>
          <span class="category-badge">{{ product.category_name || 'Товар' }}</span>
          <h1 class="product-title">{{ product.name }}</h1>

          <div class="price-block">
            <div class="price-wrapper">
              <span v-if="product.is_promo" class="old-price">{{ product.original_price }} ₴</span>
              <span class="price" :class="{ 'promo-active': product.is_promo }">{{ product.price }} ₴</span>
            </div>
            <span class="stock-status" :class="product.stock > 0 ? 'in-stock' : 'out-of-stock'">
              {{ product.stock > 0 ? 'В наявності' : 'Немає' }}
            </span>
          </div>

          <div class="size-section">
            <div class="size-header">
              <span class="size-label">{{ sizeLabelText }}</span>
              <span v-if="needsSize" class="size-selected">{{ selectedSize || 'Не обрано' }}</span>
            </div>
            <div v-if="needsSize" class="sizes-grid" :class="{ 'wide-sizes': isClothingCategory || isSocksCategory }">
              <button v-for="size in currentSizes" :key="size" class="size-btn" :class="{ active: selectedSize === size }" @click="selectedSize = size">{{ size }}</button>
            </div>
            <div v-else class="one-size-box">
              <span class="one-size-text">{{ isBallCategory ? 'Розмір: 5 (Стандарт)' : 'One Size (Універсальний)' }}</span>
            </div>
          </div>

          <button class="add-to-cart-btn" :class="{ disabled: (needsSize && !selectedSize) || product.stock <= 0 }" @click="() => addToCart()" :disabled="(needsSize && !selectedSize) || product.stock <= 0">
            {{ product.stock > 0 ? cartButtonText : 'Немає в наявності' }}
          </button>
        </div>
      </div>

      <div class="description-wrapper">
        <div class="desc-header"><h2>Детальна інформація</h2></div>
        <div class="desc-body"><p>{{ product.description || 'Опис відсутній.' }}</p></div>
      </div>
    </div>

    <div v-else-if="isLoading" class="loading-state">
      <div class="spinner"></div>
      <p>Завантаження товару...</p>
    </div>
    <div v-else class="error-state">❌ Товар не знайдено.</div>
  </div>
</template>

<style scoped>
.promo-badge-top { background: #ef4444; color: white; padding: 8px 15px; border-radius: 12px; font-weight: 800; display: inline-block; margin-bottom: 15px; }
.old-price { text-decoration: line-through; color: #94a3b8; font-size: 1.3rem; display: block; }
.promo-active { color: #ef4444 !important; }
.product-page { max-width: 1200px; margin: 0 auto; padding: 20px; }
.product-top-row { display: grid; grid-template-columns: 1fr 1fr; gap: 50px; background: white; padding: 40px; border-radius: 24px; box-shadow: 0 10px 30px rgba(0,0,0,0.03); }
.main-image-box { width: 100%; aspect-ratio: 1/1; background: #f8fafc; border-radius: 20px; position: relative; display: flex; align-items: center; justify-content: center; overflow: hidden; }
.main-img { max-width: 90%; max-height: 90%; object-fit: contain; }
.thumbnails { display: flex; gap: 10px; margin-top: 20px; overflow-x: auto; }
.thumb { width: 70px; height: 70px; border-radius: 10px; cursor: pointer; border: 2px solid transparent; opacity: 0.6; }
.thumb.active { border-color: #6366f1; opacity: 1; }
.price-block { display: flex; justify-content: space-between; align-items: center; margin: 20px 0; border-bottom: 1px solid #f1f5f9; padding-bottom: 20px; }
.price { font-size: 2.5rem; font-weight: 900; color: #10b981; }
.sizes-grid { display: grid; grid-template-columns: repeat(auto-fill, minmax(60px, 1fr)); gap: 10px; margin-top: 15px; }
.size-btn { background: white; border: 2px solid #e2e8f0; border-radius: 12px; padding: 12px 0; font-weight: 700; cursor: pointer; }
.size-btn.active { background: #0f172a; color: white; border-color: #0f172a; }
.add-to-cart-btn { background: #6366f1; color: white; border: none; width: 100%; padding: 20px; border-radius: 16px; font-size: 1.2rem; font-weight: 800; cursor: pointer; transition: 0.3s; }
.add-to-cart-btn.disabled { background: #cbd5e1; cursor: not-allowed; }
.loading-state { text-align: center; padding: 100px; }
.spinner { width: 40px; height: 40px; border: 4px solid #f1f5f9; border-top-color: #6366f1; border-radius: 50%; animation: spin 1s linear infinite; margin: 0 auto 20px; }
@keyframes spin { to { transform: rotate(360deg); } }
</style>
