<script setup>
import { ref, computed, onMounted, watch } from 'vue'
import axios from 'axios'
import { useRouter } from 'vue-router'
import { useCartStore } from '../stores/cart'
import SmartSelector from '../components/SmartSelector.vue'
import AppNotification from '../components/AppNotification.vue'
import AddToCartModal from '../components/AddToCartModal.vue'
import AuthModal from '../components/AuthModal.vue'

const router = useRouter()

// ПЕРЕВІРКА АВТОРИЗАЦІЇ
const isAuthenticated = ref(!!localStorage.getItem('access_token') || !!localStorage.getItem('token'))

// --- ДАНІ ТА СТАН ---
const products = ref([])
const categories = ref([])
const selectedCategory = ref(null)
const isSelectorOpen = ref(false)
const cartStore = useCartStore()
const isLoading = ref(true)

// --- ФІЛЬТРАЦІЯ ТА СОРТУВАННЯ ---
const searchQuery = ref('')
const minPrice = ref(null)
const maxPrice = ref(null)
const selectedBrands = ref([])

// ШИПИ ТА РОЗМІРИ
const selectedStudTypes = ref([])
const availableStudTypes = ['FG', 'TF', 'IC', 'SG', 'AG']
const selectedSizes = ref([])

// МАСИВИ РОЗМІРІВ ДЛЯ ФІЛЬТРА
const shoeSizes = ['36', '37', '38', '39', '40', '41', '42', '43', '44', '45', '46', '47']
const clothingSizes = ['S', 'M', 'L', 'XL', 'XXL']
const sockSizes = ['36-39', '39-42', '42-45', '45-47']

const sortBy = ref('default')
const isSortOpen = ref(false)

const topBrands = ['Nike', 'Adidas', 'Puma', 'Jordan', 'Joma']
const sortOptions = {
  'default': 'За замовчуванням',
  'price-asc': 'Найдешевші',
  'price-desc': 'Найдорожчі',
  'name': 'За назвою (А-Я)'
}

// --- СТАН ДЛЯ МОДАЛОК ТА СПОВІЩЕНЬ ---
const showModal = ref(false)
const lastAddedProduct = ref(null)
const notification = ref({ show: false, message: '', type: 'success' })
const showAuthModal = ref(false) // Стан для модалки авторизації

const handleAuthClose = () => {
  showAuthModal.value = false
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

// --- ДОДАВАННЯ В КОШИК ---
const handleAddToCart = (product) => {
  // ЯКЩО НЕ ЗАЛОГІНЕНИЙ - ВІДКРИВАЄМО AuthModal
  if (!isAuthenticated.value) {
    showAuthModal.value = true
    return
  }

  lastAddedProduct.value = product
  showModal.value = true
}

const confirmAddingToCart = (size) => {
  if (!lastAddedProduct.value) return
  const productWithSize = {
    ...lastAddedProduct.value,
    selectedSize: size
  }
  cartStore.addToCart(productWithSize)
  showToast(`✅ Додано розмір ${size}`, 'success')
}

// --- ЛОГІКА АКЦІЙ ТА ЗАВАНТАЖЕННЯ ---
const applyPromo = (prod) => {
  if (!prod || !prod.name || prod.price === undefined) return prod
  if (prod.name.toLowerCase().includes('nike')) {
    return { ...prod, original_price: prod.price, price: Math.round(Number(prod.price) * 0.8), is_promo: true }
  }
  return prod
}

onMounted(async () => {
  try {
    isLoading.value = true
    const p = await axios.get('http://127.0.0.1:8000/api/products/')
    const rawProducts = Array.isArray(p.data) ? p.data : (p.data.results || [])
    products.value = rawProducts.map(applyPromo)

    const c = await axios.get('http://127.0.0.1:8000/api/categories/')
    categories.value = Array.isArray(c.data) ? c.data : (c.data.results || [])
  } catch (e) {
    console.error('Помилка завантаження:', e)
  } finally {
    isLoading.value = false
  }
})

// --- ДОПОМІЖНІ ФУНКЦІЇ ---
const toggleBrand = (brand) => {
  const index = selectedBrands.value.indexOf(brand)
  if (index === -1) selectedBrands.value.push(brand)
  else selectedBrands.value.splice(index, 1)
}

const toggleSizeFilter = (size) => {
  const index = selectedSizes.value.indexOf(size)
  if (index === -1) selectedSizes.value.push(size)
  else selectedSizes.value.splice(index, 1)
}

watch(selectedCategory, () => {
  selectedSizes.value = []
  selectedStudTypes.value = []
})

const currentSizeOptions = computed(() => {
  if (!selectedCategory.value) return []
  const cat = categories.value.find(c => c.id === selectedCategory.value)
  if (!cat) return []
  const catName = cat.name.toLowerCase()

  if (catName.includes('бутси') || catName.includes('сороконіжки') || catName.includes('футзалки') || catName.includes('взуття')) {
    return shoeSizes
  }
  if (catName.includes('форма') || catName.includes('одяг') || catName.includes('костюм') || catName.includes('футболка') || catName.includes('шорти') || catName.includes('аксесуар')) {
    return clothingSizes
  }
  if (catName.includes('носки') || catName.includes('шкарпетки')) {
    return sockSizes
  }
  return []
})

const filteredProducts = computed(() => {
  if (!products.value) return []
  let result = [...products.value]

  if (selectedCategory.value) result = result.filter(p => p.category === selectedCategory.value)
  if (selectedBrands.value.length > 0) result = result.filter(p => p.name && selectedBrands.value.some(brand => p.name.toLowerCase().includes(brand.toLowerCase())))
  if (searchQuery.value) {
    const q = searchQuery.value.toLowerCase()
    result = result.filter(p => p.name && p.name.toLowerCase().includes(q))
  }
  if (minPrice.value) result = result.filter(p => p.price >= minPrice.value)
  if (maxPrice.value) result = result.filter(p => p.price <= maxPrice.value)
  if (selectedStudTypes.value.length > 0) result = result.filter(p => p.stud_type && selectedStudTypes.value.includes(p.stud_type.toUpperCase()))
  if (selectedSizes.value.length > 0) {
    result = result.filter(p => {
      if (!p.sizes || p.sizes.length === 0) return false;
      return selectedSizes.value.some(selectedSize => {
        const sizeInProduct = p.sizes.find(s => s.size_name === selectedSize);
        return sizeInProduct && sizeInProduct.quantity > 0;
      });
    })
  }

  if (sortBy.value === 'price-asc') result.sort((a, b) => a.price - b.price)
  else if (sortBy.value === 'price-desc') result.sort((a, b) => b.price - a.price)
  else if (sortBy.value === 'name') result.sort((a, b) => (a.name || '').localeCompare(b.name || ''))

  return result
})

const selectSort = (option) => {
  sortBy.value = option
  isSortOpen.value = false
}

const resetFilters = () => {
  selectedCategory.value = null
  selectedBrands.value = []
  selectedStudTypes.value = []
  selectedSizes.value = []
  minPrice.value = null
  maxPrice.value = null
  searchQuery.value = ''
  sortBy.value = 'default'
}
</script>

<template>
  <div class="prom-layout">
    <AppNotification
      v-if="notification.show"
      :message="notification.message"
      :type="notification.type"
      @close="notification.show = false"
    />

    <!-- МОДАЛКА АВТОРИЗАЦІЇ -->
    <AuthModal v-if="showAuthModal" @close="handleAuthClose" />

    <div class="layout-grid">
      <!-- SIDEBAR -->
      <aside class="sidebar-wrapper">
        <div class="sticky-sidebar glass-card">
          <div class="sidebar-header">
            <h3>Фільтри</h3>
            <button class="reset-btn-top clickable-border" @click="resetFilters">Скинути</button>
          </div>

          <div class="scroll-container">
            <div class="filter-group">
              <label class="group-label">💰 Бюджет (₴)</label>
              <div class="dual-inputs">
                <input v-model.number="minPrice" type="number" placeholder="Від">
                <input v-model.number="maxPrice" type="number" placeholder="До">
              </div>
            </div>

            <div class="filter-group">
              <label class="group-label">⚽ Популярні бренди</label>
              <div class="brand-selector">
                <button
                  v-for="brand in topBrands" :key="brand"
                  :class="{ 'active-selection': selectedBrands.includes(brand) }"
                  @click="toggleBrand(brand)"
                  class="brand-btn clickable-border"
                >
                  {{ brand }}
                </button>
              </div>
            </div>

            <div class="filter-group">
              <label class="group-label">📋 Категорії</label>
              <div class="radio-list">
                <label class="radio-item clickable-border" :class="{ 'active-selection': selectedCategory === null }">
                  <input type="radio" :value="null" v-model="selectedCategory">
                  <span class="custom-radio"></span> Усі товари
                </label>
                <label
                  v-for="cat in categories" :key="cat.id"
                  class="radio-item clickable-border"
                  :class="{ 'active-selection': selectedCategory === cat.id }"
                >
                  <input type="radio" :value="cat.id" v-model="selectedCategory">
                  <span class="custom-radio"></span> {{ cat.name }}
                </label>
              </div>
            </div>

            <!-- ДИНАМІЧНИЙ ФІЛЬТР РОЗМІРІВ -->
            <transition name="fade">
              <div v-if="currentSizeOptions.length > 0" class="filter-group">
                <label class="group-label">📏 Розмір (В наявності)</label>
                <div class="size-grid">
                  <button
                    v-for="size in currentSizeOptions" :key="size"
                    class="size-filter-btn clickable-border"
                    :class="{ 'active-selection': selectedSizes.includes(size) }"
                    @click="toggleSizeFilter(size)"
                  >
                    {{ size }}
                  </button>
                </div>
              </div>
            </transition>

            <!-- ФІЛЬТР ТИПУ ПІДОШВИ -->
            <div class="filter-group" v-if="!selectedCategory || currentSizeOptions === shoeSizes">
              <label class="group-label">👟 Тип підошви</label>
              <div class="checkbox-list">
                <label v-for="stud in availableStudTypes" :key="stud" class="custom-checkbox">
                  <input type="checkbox" :value="stud" v-model="selectedStudTypes">
                  <span class="checkmark"></span>
                  <span class="label-text">{{ stud }}</span>
                </label>
              </div>
            </div>

          </div>

          <div class="sidebar-footer">
            <div class="ai-button" @click="isSelectorOpen = true">
              <span class="ai-icon">🤖</span>
              <div class="ai-text">
                <strong>Smart Match</strong>
                <span>Підібрати модель</span>
              </div>
            </div>
          </div>
        </div>
      </aside>

      <!-- MAIN CONTENT -->
      <main class="main-content">
        <header class="content-header glass-card">
          <div class="search-bar">
            <span class="search-icon">🔍</span>
            <input v-model="searchQuery" type="text" placeholder="Пошук моделі...">
          </div>
          <div class="sort-dropdown-wrap">
            <div class="sort-trigger" @click="isSortOpen = !isSortOpen">
              <span class="sort-hint">Сортування:&nbsp;</span>
              <strong>{{ sortOptions[sortBy] }}</strong>
              <span class="arrow" :class="{ open: isSortOpen }">⌄</span>
            </div>
            <transition name="pop">
              <ul v-if="isSortOpen" class="sort-menu glass-card">
                <li v-for="(label, key) in sortOptions" :key="key"
                    @click.stop="selectSort(key)" :class="{ active: sortBy === key }">
                  {{ label }}
                </li>
              </ul>
            </transition>
          </div>
        </header>

        <div v-if="isLoading" class="loader-container">
          <div class="ball-spinner"></div>
          <p>Завантаження асортименту...</p>
        </div>

        <div v-else class="product-grid">
          <div v-for="product in filteredProducts" :key="product.id" class="product-card glass-card">
            <router-link :to="'/product/' + product.id" class="card-inner">
              <div class="image-wrapper">
                <div v-if="product.is_promo" class="promo-tag">АКЦІЯ -20%</div>
                <div class="cat-tag">{{ product.category_name }}</div>
                <img v-if="product.image" :src="product.image" :alt="product.name">
              </div>
              <div class="card-info">
                <h3 class="product-name">{{ product.name }}</h3>
                <div class="card-footer">
                  <div class="price-stack">
                    <span v-if="product.is_promo" class="old-price">{{ product.original_price }} ₴</span>
                    <span class="main-price" :class="{ promo: product.is_promo }">{{ product.price }} ₴</span>
                  </div>
                </div>
              </div>
            </router-link>
          </div>
          <div v-if="filteredProducts.length === 0" class="empty-state">
            <div class="icon-circle">🛒</div>
            <p>За вашими критеріями нічого не знайдено.</p>
          </div>
        </div>
      </main>
    </div>

    <!-- Модалки Smart Match -->
    <SmartSelector v-if="isSelectorOpen" :products="products" @close="isSelectorOpen = false" @add-to-cart="handleAddToCart" />

    <AddToCartModal
      v-if="showModal"
      :product="lastAddedProduct"
      @close="showModal = false"
      @confirm-add="confirmAddingToCart"
    />
  </div>
</template>

<style scoped>
:root { --neon: #00ff88; --indigo: #6366f1; --border: rgba(255, 255, 255, 0.12); }
input::-webkit-outer-spin-button, input::-webkit-inner-spin-button { -webkit-appearance: none; appearance: none; margin: 0; }
input[type=number] { -moz-appearance: textfield; }
.prom-layout { max-width: 1400px; margin: 0 auto; padding: 20px; color: #f3f4f6; }
.layout-grid { display: grid; grid-template-columns: 320px 1fr; gap: 30px; align-items: start; }
.glass-card { background: rgba(17, 24, 39, 0.85); backdrop-filter: blur(25px); border: 1px solid var(--border); border-radius: 24px; box-shadow: 0 10px 40px rgba(0, 0, 0, 0.5); }
.sticky-sidebar { position: sticky; top: 100px; padding: 25px; display: flex; flex-direction: column; height: calc(100vh - 140px); overflow: hidden; }
.scroll-container { flex-grow: 1; overflow-y: auto; padding-right: 10px; margin-bottom: 15px; }
.scroll-container::-webkit-scrollbar { width: 4px; }
.scroll-container::-webkit-scrollbar-thumb { background: var(--border); border-radius: 10px; }
.clickable-border { border: 1.5px solid var(--border); border-radius: 14px; transition: 0.3s; background: rgba(255, 255, 255, 0.02); cursor: pointer; }
.clickable-border:hover { border-color: var(--neon); background: rgba(0, 255, 136, 0.05); }
.active-selection { border-color: var(--neon) !important; background: rgba(0, 255, 136, 0.1) !important; color: white !important; box-shadow: 0 0 15px rgba(0, 255, 136, 0.2); }
.sort-dropdown-wrap { position: relative; min-width: 280px; z-index: 999; }
.sort-trigger { background: rgba(0, 0, 0, 0.2); border: 1px solid var(--border); padding: 14px 20px; border-radius: 16px; display: flex; justify-content: space-between; align-items: center; cursor: pointer; }
.sort-menu { position: absolute; top: calc(100% + 10px); right: 0; width: 100%; z-index: 9999 !important; padding: 10px !important; margin: 0 !important; list-style: none !important; }
.sort-menu li { padding: 12px 18px; border-radius: 12px; font-weight: 700; color: #94a3b8; transition: 0.2s; list-style-type: none !important; }
.sort-menu li:hover { background: rgba(255, 255, 255, 0.05); color: white; }
.sort-menu li.active { background: var(--indigo); color: white; }
.product-grid { display: grid; grid-template-columns: repeat(3, 1fr); gap: 25px; }
.product-card { transition: 0.4s; overflow: hidden; }
.product-card:hover { transform: translateY(-10px); border-color: var(--neon); }
.image-wrapper { background: #1f2937; aspect-ratio: 1/1; border-radius: 20px; margin: 15px; display: flex; align-items: center; justify-content: center; position: relative; overflow: hidden; }
.image-wrapper img { max-width: 85%; max-height: 85%; object-fit: contain; transition: 0.5s; }
.product-card:hover img { transform: scale(1.1) rotate(-3deg); }
.promo-tag { position: absolute; top: 8px; right: 8px; background: #ef4444; color: white; padding: 2px 8px; border-radius: 6px; font-weight: 900; font-size: 0.6rem; z-index: 10; }
.cat-tag { position: absolute; top: 8px; left: 8px; background: white; color: #111827; padding: 3px 8px; border-radius: 8px; font-weight: 900; font-size: 0.65rem; text-transform: uppercase; }
.sidebar-header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 25px; }
.reset-btn-top { background: rgba(255, 26, 26, 0.08); color: #ff1a1a; padding: 8px 16px; font-weight: 800; font-size: 1.2rem; border: none; border-radius: 12px; cursor: pointer; transition: 0.3s; }
.reset-btn-top:hover { background: rgba(255, 26, 26, 0.15); transform: scale(1.05); }
.filter-group { margin-bottom: 30px; }
.group-label { display: block; font-size: 0.8rem; font-weight: 800; color: #94a3b8; text-transform: uppercase; margin-bottom: 15px; }
.dual-inputs { display: flex; gap: 10px; }
.dual-inputs input { width: 100%; padding: 12px; border-radius: 12px; border: 1px solid var(--border); background: rgba(0,0,0,0.3); color: white; font-weight: 700; text-align: center; }
.brand-selector { display: grid; grid-template-columns: 1fr 1fr; gap: 10px; }
.brand-btn { padding: 12px; font-weight: 800; color: white; }
.radio-list { display: flex; flex-direction: column; gap: 10px; }
.radio-item { display: flex; align-items: center; gap: 12px; padding: 12px 14px; color: white; }
.radio-item input { display: none; }
.custom-radio { width: 16px; height: 16px; border: 2px solid var(--border); border-radius: 50%; }
.active-selection .custom-radio { border-color: var(--neon); background: var(--neon); box-shadow: 0 0 8px var(--neon); }
.size-grid { display: grid; grid-template-columns: repeat(auto-fill, minmax(45px, 1fr)); gap: 8px; }
.size-filter-btn { padding: 10px 0; font-weight: 800; color: #cbd5e1; text-align: center; font-size: 0.95rem; }
.checkbox-list { display: flex; flex-direction: column; gap: 12px; }
.custom-checkbox { display: flex; align-items: center; gap: 12px; cursor: pointer; color: #cbd5e1; font-size: 1rem; font-weight: 600; transition: 0.2s; }
.custom-checkbox:hover { color: white; }
.custom-checkbox input { display: none; }
.checkmark { width: 22px; height: 22px; border: 2px solid var(--border); border-radius: 6px; display: flex; align-items: center; justify-content: center; transition: 0.2s; background: rgba(0, 0, 0, 0.2); }
.custom-checkbox input:checked ~ .checkmark { background: var(--neon); border-color: var(--neon); box-shadow: 0 0 10px rgba(0, 255, 136, 0.3); }
.custom-checkbox input:checked ~ .checkmark::after { content: "✓"; color: #0f172a; font-weight: 900; font-size: 14px; }
.sidebar-footer { padding-top: 15px; border-top: 1px solid var(--border); }
.ai-button { background: linear-gradient(135deg, #4f46e5, #7c3aed); padding: 18px; border-radius: 20px; display: flex; align-items: center; gap: 12px; cursor: pointer; transition: 0.3s; }
.ai-text { display: flex; flex-direction: column; align-items: flex-start; gap: 4px; }
.ai-text span { font-size: 0.85rem; color: rgba(255, 255, 255, 0.8); line-height: 1; }
.content-header { display: flex; justify-content: space-between; align-items: center; gap: 30px; padding: 15px 25px; margin-bottom: 25px; position: relative; z-index: 100; }
.search-bar { flex-grow: 1; position: relative; min-width: 0; }
.search-icon { position: absolute; left: 15px; top: 50%; transform: translateY(-50%); opacity: 0.5; }
.search-bar input { width: 100%; padding: 14px 14px 14px 45px; border-radius: 16px; border: 1px solid var(--border); background: rgba(0, 0, 0, 0.2); color: white; box-sizing: border-box; }
.card-info { padding: 0 20px 25px 20px; }
.product-name { font-size: 1.1rem; font-weight: 800; color: white; margin-bottom: 18px; height: 2.6em; overflow: hidden; line-height: 1.3; }
.main-price { font-size: 1.6rem; font-weight: 900; color: white; }
.promo { color: var(--neon); }
.empty-state { text-align: center; padding: 60px 0; grid-column: 1 / -1; color: #94a3b8; }
.empty-state .icon-circle { font-size: 3rem; margin-bottom: 15px; opacity: 0.5; }
.pop-enter-active, .pop-leave-active { transition: all 0.2s; }
.pop-enter-from, .pop-leave-to { opacity: 0; transform: translateY(-10px); }
.fade-enter-active, .fade-leave-active { transition: opacity 0.3s ease; }
.fade-enter-from, .fade-leave-to { opacity: 0; }
.card-inner { text-decoration: none !important; color: inherit; }
.old-price { text-decoration: line-through !important; color: #64748b; font-size: 0.85rem; font-weight: 700; }
</style>
