<script setup>
import { ref, computed, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import axios from 'axios'
import { useCartStore } from '../stores/cart'
import AppNotification from '../components/AppNotification.vue'
import AuthModal from '../components/AuthModal.vue'

const route = useRoute()
const router = useRouter()
const cartStore = useCartStore()

// ПЕРЕВІРКА АВТОРИЗАЦІЇ
const isAuthenticated = ref(!!localStorage.getItem('access_token') || !!localStorage.getItem('token'))

const product = ref(null)
const similarProducts = ref([])
const isLoading = ref(true)
const selectedSize = ref(null)

// --- СТАН ДЛЯ СПОВІЩЕНЬ ТА МОДАЛЬНИХ ВІКОН ---
const notification = ref({ show: false, message: '', type: 'success' })
const showSuccessModal = ref(false)
const showAuthModal = ref(false) // Стан для модалки авторизації

const handleAuthClose = () => {
  showAuthModal.value = false
  // Оновлюємо статус авторизації після закриття модалки
  isAuthenticated.value = !!localStorage.getItem('access_token') || !!localStorage.getItem('token')
}

const showToast = (msg, type = 'success') => {
  notification.value.show = false
  setTimeout(() => {
    notification.value.message = msg
    notification.value.type = type
    notification.value.show = true
  }, 10)
}

const currentImageIndex = ref(0)

// --- ЛОГІКА ДЛЯ РЕАЛЬНИХ РОЗМІРІВ З БАЗИ ---
const availableSizes = computed(() => {
  if (!product.value || !product.value.sizes) return []
  return product.value.sizes
})

const totalStock = computed(() => {
  if (!product.value || !product.value.sizes) return 0
  return product.value.sizes.reduce((sum, item) => sum + item.quantity, 0)
})

const needsSize = computed(() => availableSizes.value.length > 0)

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

  } catch {
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
    showToast('Будь ласка, оберіть розмір! 📏', 'error')
    return
  }

  cartStore.addToCart({
    ...product.value,
    selectedSize: selectedSize.value || 'One Size'
  })

  showSuccessModal.value = true
}

// --- РОЗУМНИЙ АНАЛІЗАТОР ТЕКСТУ ОПИСУ ---
const parsedDescription = computed(() => {
  if (!product.value?.description) return []
  const lines = product.value.description.split('\n').filter(line => line.trim() !== '')

  return lines.map(line => {
    const colonIndex = line.indexOf(':')
    const textAfter = line.substring(colonIndex + 1).trim()

    if (colonIndex > 0 && colonIndex < 40 && textAfter.length > 0) {
      return { type: 'feature', label: line.substring(0, colonIndex + 1), text: textAfter }
    }
    else if (colonIndex > 0 && textAfter.length === 0) {
      return { type: 'subtitle', text: line.trim() }
    }
    else {
      return { type: 'paragraph', text: line.trim() }
    }
  })
})
</script>

<template>
  <div class="product-page">
    <AppNotification
      v-if="notification.show"
      :message="notification.message"
      :type="notification.type"
      @close="notification.show = false"
    />

    <!-- МОДАЛКА АВТОРИЗАЦІЇ -->
    <AuthModal v-if="showAuthModal" @close="handleAuthClose" />

    <!-- МОДАЛКА КОШИКА -->
    <Transition name="fade">
      <div v-if="showSuccessModal" class="modal-backdrop" @click.self="showSuccessModal = false">
        <div class="modal-glass success-modal">
          <div class="icon-circle">✅</div>
          <h3 class="modal-title">Додано до кошика!</h3>
          <p class="modal-msg">
            {{ product.name }} <br>
            <span class="size-text" v-if="needsSize">Розмір: {{ selectedSize }}</span>
          </p>
          <div class="modal-actions">
            <button class="btn-primary" @click="router.push('/checkout')">Оформити замовлення 🚀</button>
            <button class="btn-secondary" @click="showSuccessModal = false">Продовжити покупки</button>
          </div>
        </div>
      </div>
    </Transition>

    <div class="header-simple">
      <button class="back-btn" @click="router.push('/')">← Назад до каталогу</button>
    </div>

    <!-- КОНТЕЙНЕР ДЛЯ ВСЬОГО ТОВАРУ -->
    <div v-if="!isLoading && product" class="product-full-container">

      <!-- ВЕРХНЯ ЧАСТИНА -->
      <div class="product-layout">
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
              <div class="stock-badge" :class="totalStock > 0 ? 'in' : 'out'">
                {{ totalStock > 0 ? 'В наявності' : 'Немає' }}
              </div>
            </div>

            <div class="size-selector-block">
              <div class="size-header">
                <h3>Розмір:</h3>
                <span class="selected-val">{{ selectedSize || 'Оберіть зі списку' }}</span>
              </div>

              <div v-if="needsSize" class="sizes-container">
                <button
                  v-for="sizeObj in availableSizes" :key="sizeObj.size_name"
                  class="size-chip"
                  :class="{
                    active: selectedSize === sizeObj.size_name,
                    'disabled-size': sizeObj.quantity <= 0
                  }"
                  :disabled="sizeObj.quantity <= 0"
                  @click="selectedSize = sizeObj.size_name"
                  :title="sizeObj.quantity <= 0 ? 'Немає в наявності' : `Залишилось: ${sizeObj.quantity} шт.`"
                >
                  {{ sizeObj.size_name }}
                </button>
              </div>
              <div v-else class="one-size-info">
                <span class="info-icon">ℹ️</span>
                Універсальний розмір (One Size)
              </div>
            </div>

            <!-- ЗМІНЕНІ КНОПКИ ДЛЯ АВТОРИЗАЦІЇ -->
            <button
              v-if="!isAuthenticated"
              class="add-to-cart-btn login-required-btn"
              @click="showAuthModal = true"
            >
              Увійдіть, щоб купити 🔒
            </button>

            <button
              v-else
              class="add-to-cart-btn"
              :class="{ 'btn-disabled': totalStock <= 0 || (needsSize && !selectedSize) }"
              @click="addToCart"
              :disabled="totalStock <= 0 || (needsSize && !selectedSize)"
            >
              {{ totalStock > 0 ? (selectedSize || !needsSize ? 'Додати до кошика 🛍️' : 'Оберіть розмір') : 'Товар закінчився' }}
            </button>
          </div>
        </div>
      </div>

      <!-- НИЖНЯ ЧАСТИНА: ОПИС -->
      <div class="description-glass glass-card">
        <div class="desc-header">
          <h3>Опис та характеристики</h3>
        </div>

        <div class="desc-body">
          <template v-for="(item, index) in parsedDescription" :key="index">
            <h4 v-if="item.type === 'subtitle'" class="desc-subtitle">
              {{ item.text }}
            </h4>
            <div v-else-if="item.type === 'feature'" class="feature-row">
              <span class="feature-label">{{ item.label }}</span>
              <span class="feature-text">{{ item.text }}</span>
            </div>
            <p v-else class="desc-paragraph">
              {{ item.text }}
            </p>
          </template>

          <p v-if="!parsedDescription.length" class="desc-empty">
            Детальний опис цієї моделі скоро з'явиться.
          </p>
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
.back-btn { background: rgba(255, 255, 255, 0.05); border: 1px solid rgba(255, 255, 255, 0.1); padding: 12px 24px; border-radius: 14px; color: #94a3b8; font-weight: 800; cursor: pointer; transition: 0.3s; margin-bottom: 30px; }
.back-btn:hover { border-color: #00ff88; color: #00ff88; transform: translateX(-5px); }
.product-layout { display: grid; grid-template-columns: 1fr 1fr; gap: 40px; align-items: start; margin-bottom: 40px; }
.glass-card { background: rgba(17, 24, 39, 0.7); backdrop-filter: blur(20px); border: 1px solid rgba(255, 255, 255, 0.1); border-radius: 32px; box-shadow: 0 20px 50px rgba(0, 0, 0, 0.3); }
.gallery-section { display: flex; flex-direction: column; min-width: 0; }
.main-image-wrapper { width: 100%; aspect-ratio: 1 / 1; display: flex; align-items: center; justify-content: center; position: relative; overflow: hidden; padding: 40px; box-sizing: border-box; }
.main-img { width: 100%; height: 100%; object-fit: contain; transition: 0.5s; }
.main-image-wrapper:hover .main-img { transform: scale(1.05) rotate(-2deg); }
.promo-tag-big { position: absolute; top: 25px; left: 25px; background: #ef4444; color: white; padding: 8px 20px; border-radius: 12px; font-weight: 900; z-index: 5; box-shadow: 0 10px 20px rgba(239, 68, 68, 0.4); }
.nav-arrow { position: absolute; top: 50%; transform: translateY(-50%); background: rgba(0, 0, 0, 0.5); border: none; color: white; width: 50px; height: 50px; border-radius: 50%; cursor: pointer; transition: 0.3s; }
.nav-arrow:hover { background: #00ff88; color: #0f172a; }
.prev { left: 20px; } .next { right: 20px; }
.thumbnails-grid { display: flex; gap: 15px; margin-top: 20px; overflow-x: auto; padding-bottom: 10px; }
.thumb-box { width: 100px; height: 100px; padding: 10px; cursor: pointer; transition: 0.3s; flex-shrink: 0; }
.thumb-box.active { border-color: #00ff88; background: rgba(0, 255, 136, 0.05); }
.thumb-img { width: 100%; height: 100%; object-fit: contain; }
.info-section { display: flex; flex-direction: column; }
.info-glass { padding: 40px; display: flex; flex-direction: column; }
.category-path { color: #00ff88; font-weight: 800; text-transform: uppercase; font-size: 0.85rem; letter-spacing: 1px; }
.product-title { font-size: 2.5rem; font-weight: 900; margin: 10px 0 25px; line-height: 1.2; }
.price-box { display: flex; justify-content: space-between; align-items: center; margin-bottom: 40px; }
.price-values { display: flex; flex-direction: column; white-space: nowrap; }
.old-price-val { text-decoration: line-through; color: #64748b; font-size: 1.2rem; font-weight: 800; }
.current-price { font-size: 3rem; font-weight: 900; }
.promo-color { color: #00ff88; }
.stock-badge { padding: 10px 20px; border-radius: 20px; font-weight: 900; font-size: 0.95rem; white-space: nowrap; flex-shrink: 0; text-transform: uppercase; letter-spacing: 0.5px; }
.stock-badge.in { background: rgba(0, 255, 136, 0.1); color: #00ff88; border: 1px solid rgba(0, 255, 136, 0.3); }
.stock-badge.out { background: rgba(239, 68, 68, 0.1); color: #ef4444; border: 1px solid rgba(239, 68, 68, 0.3); }
.size-selector-block { margin-bottom: 40px; }
.size-header { display: flex; justify-content: space-between; margin-bottom: 20px; }
.size-header h3 { font-size: 1.2rem; font-weight: 800; color: white; margin: 0; }
.selected-val { color: #00ff88; font-weight: 900; font-size: 1.1rem; }
.sizes-container { display: grid; grid-template-columns: repeat(auto-fill, minmax(90px, 1fr)); gap: 15px; }
.size-chip { background: rgba(255, 255, 255, 0.05); border: 1px solid rgba(255, 255, 255, 0.1); padding: 18px 0; border-radius: 16px; color: white; font-weight: 900; font-size: 1.2rem; cursor: pointer; transition: 0.3s; }
.size-chip:hover:not(.disabled-size) { border-color: #00ff88; color: #00ff88; background: rgba(0, 255, 136, 0.05); }
.size-chip.active { background: #00ff88; color: #0f172a; border-color: #00ff88; box-shadow: 0 0 20px rgba(0, 255, 136, 0.3); transform: scale(1.05); }
.disabled-size { opacity: 0.4; cursor: not-allowed; background: rgba(255, 255, 255, 0.02); text-decoration: line-through; color: #64748b; }
.one-size-info { background: rgba(99, 102, 241, 0.1); border: 1px solid rgba(99, 102, 241, 0.3); padding: 20px; border-radius: 16px; color: #818cf8; font-weight: 800; display: flex; gap: 10px; font-size: 1.1rem; }
.add-to-cart-btn { width: 100%; background: white; color: #0f172a; border: none; padding: 22px; border-radius: 20px; font-weight: 900; font-size: 1.2rem; cursor: pointer; transition: 0.4s; }
.add-to-cart-btn:hover:not(:disabled) { background: #00ff88; transform: translateY(-5px); box-shadow: 0 15px 30px rgba(0, 255, 136, 0.3); }
.btn-disabled { opacity: 0.5; cursor: not-allowed; filter: grayscale(1); }
.login-required-btn { background: linear-gradient(135deg, #6366f1, #8b5cf6); color: white; }
.login-required-btn:hover { box-shadow: 0 15px 30px rgba(99, 102, 241, 0.4); }
.description-glass { padding: 50px; width: 100%; box-sizing: border-box; }
.desc-header { border-bottom: 1px solid rgba(255, 255, 255, 0.1); padding-bottom: 20px; margin-bottom: 30px; }
.desc-header h3 { margin: 0; font-size: 1.8rem; color: white; font-weight: 900; }
.desc-body { display: flex; flex-direction: column; gap: 18px; }
.desc-paragraph { color: #94a3b8; line-height: 1.8; font-size: 1.1rem; margin: 0; }
.desc-subtitle { color: #00ff88; font-size: 1.2rem; font-weight: 800; margin: 20px 0 5px; text-transform: uppercase; letter-spacing: 1px; }
.feature-row { display: flex; align-items: center; background: rgba(255, 255, 255, 0.03); padding: 18px 24px; border-radius: 16px; border-left: 4px solid #00ff88; gap: 20px; transition: 0.3s ease; }
.feature-row:hover { background: rgba(255, 255, 255, 0.06); transform: translateX(5px); box-shadow: 0 5px 15px rgba(0, 255, 136, 0.05); }
.feature-label { color: white; font-weight: 800; min-width: 220px; flex-shrink: 0; font-size: 1.05rem; }
.feature-text { color: #cbd5e1; font-size: 1.05rem; line-height: 1.6; margin: 0; }
.desc-empty { color: #64748b; font-style: italic; }
.loader-wrap { text-align: center; padding: 100px 0; }
.ball-spinner { width: 50px; height: 50px; border: 5px solid rgba(255, 255, 255, 0.1); border-top-color: #00ff88; border-radius: 50%; animation: spin 1s linear infinite; margin: 0 auto 20px; }
@keyframes spin { to { transform: rotate(360deg); } }
.modal-backdrop { position: fixed; top: 0; left: 0; width: 100vw; height: 100vh; background: rgba(11, 15, 25, 0.8); backdrop-filter: blur(12px); display: flex; align-items: center; justify-content: center; z-index: 999999; }
.success-modal { background: rgba(17, 24, 39, 0.95); border: 1px solid rgba(255, 255, 255, 0.12); border-radius: 32px; padding: 40px; width: 90%; max-width: 420px; text-align: center; box-shadow: 0 30px 60px rgba(0, 0, 0, 0.5), 0 0 40px rgba(0, 255, 136, 0.1); }
.icon-circle { width: 80px; height: 80px; margin: 0 auto 20px; background: rgba(0, 255, 136, 0.1); border: 1px solid rgba(0, 255, 136, 0.3); border-radius: 50%; display: flex; align-items: center; justify-content: center; font-size: 2.5rem; box-shadow: 0 10px 25px rgba(0, 255, 136, 0.2); }
.modal-title { margin: 0 0 10px 0; font-size: 1.6rem; font-weight: 900; color: white; }
.modal-msg { margin: 0 0 25px 0; color: #94a3b8; font-size: 1.1rem; line-height: 1.5; }
.size-text { color: #00ff88; font-weight: 800; font-size: 0.95rem; display: inline-block; margin-top: 5px; padding: 4px 10px; background: rgba(0, 255, 136, 0.1); border-radius: 8px;}
.modal-actions { display: flex; flex-direction: column; gap: 12px; }
.btn-primary { background: #00ff88; color: #0f172a; border: none; padding: 16px; border-radius: 16px; font-weight: 900; font-size: 1.05rem; cursor: pointer; transition: 0.3s; }
.btn-primary:hover { transform: translateY(-3px); box-shadow: 0 10px 20px rgba(0, 255, 136, 0.3); }
.btn-secondary { background: rgba(255, 255, 255, 0.05); color: white; border: 1px solid rgba(255, 255, 255, 0.1); padding: 16px; border-radius: 16px; font-weight: 800; font-size: 1.05rem; cursor: pointer; transition: 0.3s; }
.btn-secondary:hover { background: rgba(255, 255, 255, 0.1); border-color: #00ff88; color: #00ff88; }
.fade-enter-active, .fade-leave-active { transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1); }
.fade-enter-from, .fade-leave-to { opacity: 0; transform: scale(0.95) translateY(20px); }
@media (max-width: 1000px) { .product-layout { grid-template-columns: 1fr; } .product-title { font-size: 2rem; } }
@media (max-width: 768px) { .description-glass { padding: 30px 20px; } .feature-row { flex-direction: column; gap: 8px; padding: 15px; } .feature-label { min-width: auto; color: #00ff88; } }
</style>
