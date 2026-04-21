<script setup>
import { ref, computed, onMounted } from 'vue'
import axios from 'axios'
import { useCartStore } from '../stores/cart'
import SmartSelector from '../components/SmartSelector.vue'

const products = ref([])
const categories = ref([])
const selectedCategory = ref(null)
const isSelectorOpen = ref(false)
const cartStore = useCartStore()

const searchQuery = ref('')
const minPrice = ref(null)
const maxPrice = ref(null)
const selectedBrands = ref([])
const sortBy = ref('default')
const isSortOpen = ref(false)

const topBrands = ['Nike', 'Adidas', 'Puma', 'Jordan', 'Joma']

const sortOptions = {
  'default': 'За замовчуванням',
  'price-asc': 'Найдешевші',
  'price-desc': 'Найдорожчі',
  'name': 'За назвою (А-Я)'
}

onMounted(async () => {
  try {
    const p = await axios.get('http://127.0.0.1:8000/api/products/')
    products.value = p.data
    const c = await axios.get('http://127.0.0.1:8000/api/categories/')
    categories.value = c.data
  } catch (e) {
    console.error('Помилка завантаження бази:', e)
  }
})

const toggleBrand = (brand) => {
  const index = selectedBrands.value.indexOf(brand)
  if (index === -1) selectedBrands.value.push(brand)
  else selectedBrands.value.splice(index, 1)
}

const filteredProducts = computed(() => {
  let result = [...products.value]

  if (selectedCategory.value) result = result.filter(p => p.category === selectedCategory.value)
  if (selectedBrands.value.length > 0) {
    result = result.filter(p => selectedBrands.value.some(brand => p.name.toLowerCase().includes(brand.toLowerCase())))
  }
  if (searchQuery.value) result = result.filter(p => p.name.toLowerCase().includes(searchQuery.value.toLowerCase()))
  if (minPrice.value) result = result.filter(p => p.price >= minPrice.value)
  if (maxPrice.value) result = result.filter(p => p.price <= maxPrice.value)

  if (sortBy.value === 'price-asc') result.sort((a, b) => a.price - b.price)
  else if (sortBy.value === 'price-desc') result.sort((a, b) => b.price - a.price)
  else if (sortBy.value === 'name') result.sort((a, b) => a.name.localeCompare(b.name))

  return result
})

const selectSort = (option) => {
  sortBy.value = option
  isSortOpen.value = false
}

const resetFilters = () => {
  selectedCategory.value = null
  selectedBrands.value = []
  minPrice.value = null
  maxPrice.value = null
  searchQuery.value = ''
  sortBy.value = 'default'
}
</script>

<template>
  <div class="prom-layout">
    <section class="top-controls">
      <div class="search-box">
        <span class="icon">🔍</span>
        <input v-model="searchQuery" type="text" placeholder="Знайти модель, колір або бренд...">
      </div>

      <div class="sort-container">
        <div class="custom-select" @click="isSortOpen = !isSortOpen">
          <span class="label">Сортування:</span>
          <div class="trigger">
            {{ sortOptions[sortBy] }}
            <span class="arrow" :class="{ open: isSortOpen }">⌄</span>
          </div>
          <transition name="slide">
            <ul v-if="isSortOpen" class="options">
              <li v-for="(label, key) in sortOptions" :key="key"
                  @click.stop="selectSort(key)" :class="{ active: sortBy === key }">
                {{ label }}
              </li>
            </ul>
          </transition>
        </div>
      </div>
    </section>

    <div class="main-content">
      <aside class="filters-sidebar">

        <div class="filter-group">
          <h4>💰 Діапазон ціни</h4>
          <div class="price-inputs">
            <div class="input-wrapper">
              <input v-model.number="minPrice" type="number" placeholder="Від">
              <span class="currency">₴</span>
            </div>
            <span class="dash">—</span>
            <div class="input-wrapper">
              <input v-model.number="maxPrice" type="number" placeholder="До">
              <span class="currency">₴</span>
            </div>
          </div>
        </div>

        <div class="filter-group">
          <h4>⚽ Бренди</h4>
          <div class="brand-grid">
            <button
              v-for="brand in topBrands" :key="brand"
              :class="{ active: selectedBrands.includes(brand) }"
              @click="toggleBrand(brand)"
              class="brand-pill"
            >
              <span class="check-mark" v-if="selectedBrands.includes(brand)">✓</span>
              {{ brand }}
            </button>
          </div>
        </div>

        <div class="filter-group">
          <h4>📋 Категорії</h4>
          <div class="list-options">
            <label class="radio-item">
              <input type="radio" :value="null" v-model="selectedCategory">
              <span>Всі товари</span>
            </label>
            <label v-for="cat in categories" :key="cat.id" class="radio-item">
              <input type="radio" :value="cat.id" v-model="selectedCategory">
              <span>{{ cat.name }}</span>
            </label>
          </div>
        </div>

        <button class="reset-btn" @click="resetFilters">Скинути все</button>

        <div class="ai-promo" @click="isSelectorOpen = true">
          <span>🤖</span>
          <p>Не знаєш, що обрати? <br><strong>Пройди опитування</strong>, і алгоритм підбере тобі ідеальну модель!</p>
        </div>
      </aside>

      <main class="products-area">
        <div v-if="filteredProducts.length === 0" class="empty">
          <p>Нічого не знайдено 🕵️‍♂️ Спробуйте змінити фільтри</p>
        </div>
        <transition-group name="fade-grid" tag="div" class="grid">
          <div v-for="product in filteredProducts" :key="product.id" class="p-card">
            <router-link :to="'/product/' + product.id" class="card-body">
              <div class="img-wrap">
                <span class="tag">{{ product.category_name }}</span>
                <img v-if="product.image" :src="product.image" :alt="product.name" class="product-image">
                <div v-else class="icon-placeholder">👟</div>
              </div>
              <div class="info">
                <h3>{{ product.name }}</h3>
                <p class="studs">{{ product.stud_type || 'Elite Quality' }}</p>
                <div class="card-footer">
                  <span class="price">{{ product.price }} ₴</span>
                  <button class="add-btn" @click.prevent="cartStore.addToCart(product)">
                    <svg width="20" height="20" fill="none" stroke="currentColor" stroke-width="3" viewBox="0 0 24 24"><path d="M12 5v14M5 12h14"></path></svg>
                  </button>
                </div>
              </div>
            </router-link>
          </div>
        </transition-group>
      </main>
    </div>

    <SmartSelector v-if="isSelectorOpen" :products="products" @close="isSelectorOpen = false" @add-to-cart="cartStore.addToCart" />
  </div>
</template>

<style scoped>
.ai-promo { margin-top: 25px; padding: 20px 15px; background: #f8fafc; border: 2px dashed #6366f1; border-radius: 20px; cursor: pointer; text-align: center; transition: 0.3s; }
.ai-promo:hover { background: #e0e7ff; transform: translateY(-5px); box-shadow: 0 10px 20px rgba(99, 102, 241, 0.15); }
.ai-promo span { font-size: 2.5rem; display: block; margin-bottom: 10px; }
.ai-promo p { font-size: 0.9rem; line-height: 1.4; margin: 0; color: #475569; }
.ai-promo strong { color: #6366f1; }

.prom-layout { max-width: 1300px; margin: 0 auto; }
.top-controls { display: flex; gap: 20px; margin-bottom: 30px; align-items: center; background: white; padding: 15px 25px; border-radius: 24px; box-shadow: 0 10px 30px rgba(0,0,0,0.05); }
.search-box { flex-grow: 1; position: relative; display: flex; align-items: center; }
.search-box .icon { position: absolute; left: 15px; opacity: 0.5; }
.search-box input { width: 100%; padding: 14px 45px; border: 2px solid #f1f5f9; border-radius: 16px; font-size: 1rem; font-family: inherit; transition: 0.3s; }
.search-box input:focus { border-color: #6366f1; outline: none; background: #f8fafc; }

/* КАСТОМНИЙ ДРОПДАУН СОРТУВАННЯ */
.custom-select { position: relative; cursor: pointer; display: flex; align-items: center; gap: 10px; min-width: 260px; }
.custom-select .label { font-weight: 700; color: #64748b; font-size: 0.9rem; }
.custom-select .trigger { background: #f1f5f9; padding: 12px 18px; border-radius: 14px; font-weight: 800; display: flex; justify-content: space-between; flex-grow: 1; border: 1px solid #e2e8f0; }
.custom-select .options { position: absolute; top: 100%; right: 0; width: 100%; background: white; border-radius: 16px; box-shadow: 0 20px 40px rgba(0,0,0,0.1); z-index: 100; list-style: none; padding: 8px; margin-top: 10px; border: 1px solid #f1f5f9; }
.custom-select .options li { padding: 12px; border-radius: 10px; font-weight: 600; transition: 0.2s; }
.custom-select .options li:hover { background: #f1f5f9; color: #6366f1; }
.custom-select .options li.active { background: #6366f1; color: white; }

.main-content { display: grid; grid-template-columns: 300px 1fr; gap: 40px; }

/* САЙДБАР */
.filters-sidebar { background: white; padding: 30px; border-radius: 32px; box-shadow: 0 10px 30px rgba(0,0,0,0.05); position: sticky; top: 100px; height: calc(100vh - 130px); overflow-y: auto; }
.filters-sidebar::-webkit-scrollbar { width: 6px; }
.filters-sidebar::-webkit-scrollbar-track { background: transparent; }
.filters-sidebar::-webkit-scrollbar-thumb { background: #cbd5e1; border-radius: 10px; }
.filters-sidebar::-webkit-scrollbar-thumb:hover { background: #94a3b8; }
.filter-group { margin-bottom: 30px; }
.filter-group h4 { margin-bottom: 15px; font-weight: 800; color: #1e293b; }

/* ПОЛЯ ЦІНИ */
.price-inputs { display: flex; align-items: center; gap: 12px; }
.input-wrapper { position: relative; flex: 1; }
.input-wrapper input { width: 100%; padding: 12px 30px 12px 15px; border: 2px solid #f1f5f9; background: #f8fafc; border-radius: 14px; font-family: inherit; font-weight: 700; font-size: 0.95rem; color: #0f172a; transition: all 0.3s ease; box-sizing: border-box; }
.input-wrapper input:focus { outline: none; border-color: #6366f1; background: white; box-shadow: 0 0 0 4px rgba(99, 102, 241, 0.1); }
.input-wrapper input::-webkit-outer-spin-button,
.input-wrapper input::-webkit-inner-spin-button {
  -webkit-appearance: none;
  appearance: none; /* ДОДАЛИ СЮДИ */
  margin: 0;
}
.input-wrapper input[type=number] {
  -moz-appearance: textfield;
  appearance: textfield; /* І ДОДАЛИ СЮДИ */
}
.input-wrapper .currency { position: absolute; right: 12px; top: 50%; transform: translateY(-50%); color: #94a3b8; font-weight: 800; pointer-events: none; }
.dash { color: #cbd5e1; font-weight: 900; }

.brand-grid { display: grid; grid-template-columns: 1fr 1fr; gap: 10px; }
.brand-pill { background: #f8fafc; border: 1px solid #e2e8f0; padding: 10px 8px; border-radius: 12px; font-weight: 700; cursor: pointer; transition: 0.2s; font-size: 0.85rem; display: flex; align-items: center; justify-content: center; gap: 5px; }
.brand-pill.active { background: #6366f1; color: white; border-color: #6366f1; box-shadow: 0 4px 12px rgba(99, 102, 241, 0.3); }

.radio-item { display: flex; align-items: center; gap: 12px; margin-bottom: 10px; cursor: pointer; font-weight: 600; color: #475569; }
.radio-item input { accent-color: #6366f1; width: 18px; height: 18px; }
.reset-btn { width: 100%; padding: 14px; background: #fee2e2; color: #ef4444; border: none; border-radius: 14px; cursor: pointer; font-weight: 800; transition: 0.2s; }

.grid { display: grid; grid-template-columns: repeat(auto-fill, minmax(280px, 1fr)); gap: 25px; }
.p-card { background: white; border-radius: 32px; padding: 15px; border: 1px solid #f1f5f9; transition: 0.4s; }
.p-card:hover { transform: translateY(-10px); box-shadow: 0 30px 60px rgba(0,0,0,0.08); }
.card-body { text-decoration: none; color: inherit; }

.img-wrap { background: #f8fafc; height: 220px; border-radius: 24px; display: flex; align-items: center; justify-content: center; font-size: 5rem; position: relative; overflow: hidden; }
.tag { position: absolute; top: 15px; left: 15px; background: white; padding: 5px 12px; border-radius: 20px; font-size: 0.75rem; font-weight: 800; color: #6366f1; z-index: 2; box-shadow: 0 4px 10px rgba(0,0,0,0.05); }

.product-image { width: 100%; height: 100%; object-fit: contain; padding: 15px; transition: 0.3s; }
.p-card:hover .product-image { transform: scale(1.05); }

.info { padding: 20px 5px; }
.info h3 { margin: 0 0 8px 0; font-size: 1.2rem; font-weight: 800; color: #0f172a; }
.studs { color: #94a3b8; font-weight: 700; font-size: 0.9rem; margin-bottom: 20px; }
.card-footer { display: flex; justify-content: space-between; align-items: center; }
.price { font-size: 1.6rem; font-weight: 900; color: #0f172a; }
.add-btn { width: 48px; height: 48px; background: #0f172a; color: white; border: none; border-radius: 16px; cursor: pointer; transition: 0.3s; display: flex; align-items: center; justify-content: center; }
.add-btn:hover { background: #00ff88; color: #0f172a; transform: scale(1.1); }

.slide-enter-active, .slide-leave-active { transition: 0.3s ease; }
.slide-enter-from, .slide-leave-to { opacity: 0; transform: translateY(-10px); }
.fade-grid-enter-active { transition: 0.5s ease; }
.fade-grid-enter-from { opacity: 0; transform: scale(0.9); }
</style>
