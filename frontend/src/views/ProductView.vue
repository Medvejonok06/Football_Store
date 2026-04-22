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
const similarStartIndex = ref(0)

const sizes = [36, 37, 38, 39, 40, 41, 42, 43, 44, 45, 46, 47]

const isShoeCategory = computed(() => {
  if (!product.value || !product.value.category_name) return false
  const cat = product.value.category_name.toLowerCase()
  return cat.includes('бутси') || cat.includes('сороконіжки') || cat.includes('футзалки')
})

const fetchData = async () => {
  if (!route.params.id) return

  isLoading.value = true
  selectedSize.value = null
  currentImageIndex.value = 0
  similarStartIndex.value = 0

  try {
    const res = await axios.get(`http://127.0.0.1:8000/api/products/${route.params.id}/`)
    product.value = res.data

    const allRes = await axios.get('http://127.0.0.1:8000/api/products/')

    similarProducts.value = allRes.data.filter(p => {
      const isSameCategory = String(p.category) === String(product.value.category) ||
                             (p.category_name && p.category_name === product.value.category_name)
      return isSameCategory && String(p.id) !== String(product.value.id)
    })

  } catch (error) {
    console.error("Помилка завантаження", error)
    showToast('Помилка при завантаженні товару', 'info')
  } finally {
    isLoading.value = false
    window.scrollTo({ top: 0, behavior: 'smooth' })
  }
}

watch(() => route.params.id, fetchData, { immediate: true })

const allImages = computed(() => {
  if (!product.value) return []
  let images = [product.value.image]
  if (product.value.images && product.value.images.length > 0) {
    images = images.concat(product.value.images.map(img => img.image))
  }
  return images
})

const currentImage = computed(() => {
  if (allImages.value.length === 0) return ''
  return allImages.value[currentImageIndex.value]
})

const nextImage = () => currentImageIndex.value = (currentImageIndex.value + 1) % allImages.value.length
const prevImage = () => currentImageIndex.value = (currentImageIndex.value - 1 + allImages.value.length) % allImages.value.length
const setMainImage = (index) => currentImageIndex.value = index

const nextSimilar = () => {
  if (similarStartIndex.value + 4 < similarProducts.value.length) {
    similarStartIndex.value++
  }
}

const prevSimilar = () => {
  if (similarStartIndex.value > 0) {
    similarStartIndex.value--
  }
}

const addToCart = (itemToBuy = null, size = null) => {
  const targetProduct = itemToBuy || product.value
  const targetSize = size || selectedSize.value

  if (!itemToBuy && !targetSize && isShoeCategory.value) {
    showToast('Будь ласка, оберіть розмір! 👟', 'info')
    return
  }

  cartStore.addToCart({
    id: targetSize ? `${targetProduct.id}-${targetSize}` : targetProduct.id,
    originalId: targetProduct.id,
    name: targetProduct.name,
    price: targetProduct.price,
    image: targetProduct.image,
    size: targetSize || 'Універсальний',
    quantity: 1
  })

  showToast(`${targetProduct.name} додано до кошика!`, 'success')
}

const cartButtonText = computed(() => selectedSize.value || !isShoeCategory.value ? 'Додати в кошик' : 'Оберіть розмір')
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
            <img
              v-for="(img, index) in allImages"
              :key="index"
              :src="img"
              class="thumb"
              :class="{ active: currentImageIndex === index }"
              @click="setMainImage(index)"
            >
          </div>
        </div>

        <div class="product-info">
          <span class="category-badge">{{ product.category_name || 'Футбольне взуття' }}</span>
          <h1 class="product-title">{{ product.name }}</h1>

          <div class="price-block">
            <span class="price">{{ product.price }} ₴</span>
            <span class="stock-status" :class="product.stock > 0 ? 'in-stock' : 'out-of-stock'">
              {{ product.stock > 0 ? 'В наявності' : 'Немає в наявності' }}
            </span>
          </div>

          <div class="size-section" v-if="isShoeCategory">
            <div class="size-header">
              <div class="size-labels-group">
                <span class="size-label">Розмір (EU):</span>
                <span class="size-selected">{{ selectedSize ? selectedSize : 'Не обрано' }}</span>
              </div>
            </div>
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
          </div>

          <button
            class="add-to-cart-btn"
            :class="{ disabled: (isShoeCategory && !selectedSize) || product.stock <= 0 }"
            @click="() => addToCart()"
            :disabled="(isShoeCategory && !selectedSize) || product.stock <= 0"
          >
            {{ product.stock > 0 ? cartButtonText : 'Немає в наявності' }}
          </button>
        </div>
      </div>

      <div class="description-wrapper">
        <div class="desc-header">
          <span class="desc-icon">📄</span>
          <h2>Детальна інформація</h2>
        </div>
        <div class="desc-body">
          <p>{{ product.description || 'Опис для цього товару поки не додано.' }}</p>

          <div v-if="isShoeCategory" class="inline-size-chart-container">
            <h3 class="chart-title">📏 Таблиця розмірів</h3>
            <img src="/size-chart.jpg" alt="Таблиця розмірів FootballPRO" class="inline-size-chart">
          </div>
        </div>
      </div>

      <div class="similar-section" v-if="similarProducts.length > 0">
        <div class="similar-header">
          <h2>🔥 Схожі моделі</h2>
          <div class="slider-controls" v-if="similarProducts.length > 4">
            <button class="slider-btn" @click="prevSimilar" :disabled="similarStartIndex === 0">❮</button>
            <button class="slider-btn" @click="nextSimilar" :disabled="similarStartIndex + 4 >= similarProducts.length">❯</button>
          </div>
        </div>

        <div class="carousel-viewport">
          <div class="carousel-track" :style="{ '--index': similarStartIndex }">
            <div v-for="sim in similarProducts" :key="sim.id" class="carousel-card p-card">
              <router-link :to="'/product/' + sim.id" class="card-body">
                <div class="img-wrap">
                  <span class="tag">{{ sim.category_name || sim.stud_type }}</span>
                  <img v-if="sim.image" :src="sim.image" :alt="sim.name" class="product-image">
                  <div v-else class="icon-placeholder">👟</div>
                </div>
                <div class="info">
                  <h3>{{ sim.name }}</h3>
                  <p class="studs">{{ sim.stud_type || 'Elite Quality' }}</p>
                </div>
              </router-link>
              <div class="card-footer">
                <span class="price-small">{{ sim.price }} ₴</span>
                <button class="add-btn-small" @click.prevent="addToCart(sim)" title="Додати в кошик">
                  <svg width="18" height="18" fill="none" stroke="currentColor" stroke-width="3" viewBox="0 0 24 24"><path d="M12 5v14M5 12h14"></path></svg>
                </button>
              </div>
            </div>
          </div>
        </div>
      </div>

    </div>

    <div v-else-if="isLoading" class="loading-state">
      <div class="spinner"></div>
      <p>Завантаження інформації про товар...</p>
    </div>
    <div v-else class="error-state">❌ Товар не знайдено або сталася помилка.</div>

  </div>
</template>

<style scoped>
.product-page { max-width: 1200px; margin: 0 auto; padding: 20px; }
.header-simple { margin-bottom: 30px; }
.back-btn { background: #f1f5f9; border: none; padding: 10px 20px; border-radius: 12px; font-weight: 700; color: #64748b; cursor: pointer; transition: 0.2s; }
.back-btn:hover { background: #e2e8f0; color: #0f172a; }

.product-top-row { display: grid; grid-template-columns: 1fr 1fr; gap: 50px; background: white; padding: 40px; border-radius: 24px; box-shadow: 0 10px 30px rgba(0,0,0,0.03); align-items: start; }

.product-gallery { display: flex; flex-direction: column; gap: 20px; }
.main-image-box { width: 100%; aspect-ratio: 1 / 1; background: #f8fafc; border-radius: 20px; overflow: hidden; display: flex; align-items: center; justify-content: center; border: 1px solid #f1f5f9; position: relative; }
.main-img { max-width: 90%; max-height: 90%; object-fit: contain; mix-blend-mode: multiply; }

.gallery-arrow { position: absolute; top: 50%; transform: translateY(-50%); background: rgba(255, 255, 255, 0.9); backdrop-filter: blur(4px); border: 1px solid #e2e8f0; width: 44px; height: 44px; border-radius: 50%; display: flex; align-items: center; justify-content: center; font-size: 1.2rem; color: #0f172a; cursor: pointer; box-shadow: 0 4px 15px rgba(0,0,0,0.1); transition: 0.3s; z-index: 10; }
.gallery-arrow:hover { background: #0f172a; color: white; border-color: #0f172a; transform: translateY(-50%) scale(1.1); }
.gallery-arrow.prev { left: 15px; }
.gallery-arrow.next { right: 15px; }

.thumbnails { display: flex; gap: 15px; overflow-x: auto; padding-bottom: 10px; }
.thumbnails::-webkit-scrollbar { height: 6px; }
.thumbnails::-webkit-scrollbar-thumb { background: #cbd5e1; border-radius: 10px; }
.thumb { width: 80px; height: 80px; border-radius: 12px; object-fit: cover; cursor: pointer; border: 2px solid transparent; background: #f8fafc; transition: 0.2s; opacity: 0.6; }
.thumb:hover { opacity: 1; }
.thumb.active { border-color: #6366f1; opacity: 1; }

.product-info { display: flex; flex-direction: column; }
.category-badge { background: #e0e7ff; color: #4f46e5; padding: 6px 12px; border-radius: 20px; font-size: 0.85rem; font-weight: 800; display: inline-block; align-self: flex-start; margin-bottom: 15px; text-transform: uppercase; letter-spacing: 0.5px; }
.product-title { font-size: 2.2rem; font-weight: 900; color: #0f172a; margin: 0 0 20px 0; line-height: 1.2; }

.price-block { display: flex; align-items: center; gap: 20px; margin-bottom: 30px; padding-bottom: 30px; border-bottom: 1px solid #f1f5f9; }
.price { font-size: 2.5rem; font-weight: 900; color: #10b981; }
.stock-status { font-weight: 700; font-size: 0.9rem; padding: 6px 12px; border-radius: 8px; }
.in-stock { background: #d1fae5; color: #059669; }
.out-of-stock { background: #fee2e2; color: #ef4444; }

.size-section { margin-bottom: 40px; }
.size-header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 15px; }
.size-labels-group { display: flex; gap: 10px; }
.size-label { font-weight: 800; color: #0f172a; }
.size-selected { font-weight: 700; color: #6366f1; }

.sizes-grid { display: grid; grid-template-columns: repeat(auto-fill, minmax(60px, 1fr)); gap: 10px; }
.size-btn { background: white; border: 2px solid #e2e8f0; border-radius: 12px; padding: 12px 0; font-size: 1rem; font-weight: 700; color: #475569; cursor: pointer; transition: 0.2s; font-family: inherit; }
.size-btn:hover { border-color: #94a3b8; color: #0f172a; }
.size-btn.active { background: #0f172a; color: white; border-color: #0f172a; box-shadow: 0 4px 10px rgba(15, 23, 42, 0.2); }

.add-to-cart-btn { background: #6366f1; color: white; border: none; width: 100%; padding: 20px; border-radius: 16px; font-size: 1.2rem; font-weight: 800; cursor: pointer; transition: 0.3s; box-shadow: 0 10px 20px rgba(99, 102, 241, 0.3); }
.add-to-cart-btn:hover:not(.disabled) { transform: translateY(-3px); box-shadow: 0 15px 25px rgba(99, 102, 241, 0.4); }
.add-to-cart-btn.disabled { background: #cbd5e1; color: #94a3b8; cursor: not-allowed; box-shadow: none; transform: none; }

.description-wrapper { background: white; padding: 40px; border-radius: 24px; box-shadow: 0 10px 30px rgba(0,0,0,0.03); margin-top: 40px; }
.desc-header { display: flex; align-items: center; gap: 15px; border-bottom: 2px solid #f1f5f9; padding-bottom: 20px; margin-bottom: 25px; }
.desc-icon { font-size: 2rem; background: #f8fafc; padding: 12px; border-radius: 16px; display: flex; justify-content: center; align-items: center; border: 1px solid #f1f5f9; }
.desc-header h2 { margin: 0; font-size: 1.6rem; font-weight: 900; color: #0f172a; }
.desc-body { font-size: 1.05rem; line-height: 1.9; color: #334155; max-width: 900px; }
.desc-body p { margin: 0; white-space: pre-wrap; }

/* ВБУДОВАНА ТАБЛИЦЯ РОЗМІРІВ */
.inline-size-chart-container { margin-top: 40px; padding-top: 30px; border-top: 1px dashed #e2e8f0; }
.chart-title { font-size: 1.3rem; font-weight: 800; color: #0f172a; margin-bottom: 20px; }
.inline-size-chart { width: 100%; max-width: 700px; border-radius: 16px; border: 1px solid #f1f5f9; box-shadow: 0 4px 15px rgba(0,0,0,0.03); display: block; }

.similar-section { margin-top: 60px; padding-bottom: 40px; }
.similar-header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 25px; }
.similar-header h2 { font-size: 1.8rem; font-weight: 900; color: #0f172a; margin: 0; }

.slider-controls { display: flex; gap: 10px; }
.slider-btn { width: 44px; height: 44px; border-radius: 14px; background: white; border: 2px solid #f1f5f9; font-size: 1.2rem; color: #0f172a; cursor: pointer; display: flex; align-items: center; justify-content: center; transition: 0.2s; box-shadow: 0 4px 10px rgba(0,0,0,0.02); }
.slider-btn:not(:disabled):hover { background: #0f172a; color: white; border-color: #0f172a; transform: translateY(-2px); }
.slider-btn:disabled { color: #cbd5e1; cursor: not-allowed; background: #f8fafc; box-shadow: none; }

.carousel-viewport { overflow: hidden; width: 100%; padding: 15px 0; box-sizing: border-box; }

.carousel-track {
  display: flex;
  gap: 20px;
  will-change: transform;
  transition: transform 0.6s cubic-bezier(0.22, 1, 0.36, 1);
  align-items: stretch;
  transform: translateX(calc(var(--index) * -1 * (calc((100% - 60px) / 4) + 20px)));
}

.carousel-card {
  flex: 0 0 calc((100% - 60px) / 4);
  width: calc((100% - 60px) / 4);
  max-width: calc((100% - 60px) / 4);
}

.p-card { background: white; border-radius: 24px; padding: 15px; border: 1px solid #f1f5f9; transition: 0.3s; display: flex; flex-direction: column; height: 100%; box-shadow: 0 5px 15px rgba(0,0,0,0.02); box-sizing: border-box; }
.p-card:hover { transform: translateY(-5px); box-shadow: 0 15px 30px rgba(0,0,0,0.06); border-color: #e2e8f0; }
.card-body { text-decoration: none; color: inherit; display: flex; flex-direction: column; flex-grow: 1; }
.img-wrap { width: 100%; aspect-ratio: 1 / 1; background: #f8fafc; border-radius: 16px; display: flex; align-items: center; justify-content: center; position: relative; overflow: hidden; margin-bottom: 12px; }
.tag { position: absolute; top: 10px; left: 10px; background: rgba(255, 255, 255, 0.9); padding: 4px 8px; border-radius: 10px; font-size: 0.7rem; font-weight: 800; color: #6366f1; z-index: 2; }
.product-image { max-width: 90%; max-height: 90%; object-fit: contain; mix-blend-mode: multiply; transition: 0.3s; }
.p-card:hover .product-image { transform: scale(1.05); }

.info { padding: 5px; flex-grow: 1; }
.info h3 { margin: 0 0 5px 0; font-size: 1rem; font-weight: 800; color: #0f172a; display: -webkit-box; -webkit-line-clamp: 2; -webkit-box-orient: vertical; line-clamp: 2; overflow: hidden; }
.studs { color: #94a3b8; font-weight: 700; font-size: 0.8rem; margin: 0; text-transform: uppercase; }

.card-footer { display: flex; justify-content: space-between; align-items: center; padding: 10px 5px 0 5px; margin-top: auto; }
.price-small { font-size: 1.2rem; font-weight: 900; color: #0f172a; }
.add-btn-small { width: 36px; height: 36px; background: #0f172a; color: white; border: none; border-radius: 10px; cursor: pointer; transition: 0.3s; display: flex; align-items: center; justify-content: center; }
.add-btn-small:hover { background: #00ff88; color: #0f172a; transform: scale(1.1) rotate(90deg); }

.loading-state, .error-state { text-align: center; padding: 100px; font-size: 1.2rem; font-weight: 700; color: #64748b; background: white; border-radius: 24px; margin-top: 40px; box-shadow: 0 10px 30px rgba(0,0,0,0.03); }
.spinner { width: 40px; height: 40px; border: 4px solid #f1f5f9; border-top-color: #6366f1; border-radius: 50%; animation: spin 1s linear infinite; margin: 0 auto 15px auto; }
@keyframes spin { to { transform: rotate(360deg); } }

@media (max-width: 1000px) {
  .product-top-row { grid-template-columns: 1fr; gap: 30px; padding: 20px; }
  .description-wrapper { padding: 20px; }

  .carousel-track { transform: translateX(calc(var(--index) * -1 * (calc((100% - 20px) / 2) + 20px))); }
  .carousel-card { flex: 0 0 calc((100% - 20px) / 2); width: calc((100% - 20px) / 2); max-width: calc((100% - 20px) / 2); }
}
</style>
