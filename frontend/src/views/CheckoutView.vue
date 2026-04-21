<script setup>
import { ref, computed, watch, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useCartStore } from '../stores/cart'
import { useAuthStore } from '../stores/auth'
import axios from 'axios'

const router = useRouter()
const cartStore = useCartStore()
const authStore = useAuthStore()

// --- КЛЮЧ АПІ НОВОЇ ПОШТИ (Тягнемо з .env файлу) ---
const NP_API_KEY = import.meta.env.VITE_NP_API_KEY

// --- ДАНІ КОРИСТУВАЧА ---
const customer = ref({
  firstName: '',
  lastName: '',
  phone: '',
  email: authStore.email || ''
})

// Автозаповнення, якщо користувач авторизований
onMounted(() => {
  if (authStore.isAuthenticated) {
    customer.value.firstName = authStore.username || ''
  }
})

// --- ЛОГІКА ДОСТАВКИ (НОВА ПОШТА) ---
const citySearchQuery = ref('')
const cities = ref([])
const isSearchingCity = ref(false)
const selectedCity = ref(null)

const deliveryType = ref('branch') // 'branch' (Відділення) або 'postmat' (Поштомат)
const warehouses = ref([])
const selectedWarehouse = ref(null)
const isLoadingWarehouses = ref(false)

let debounceTimeout = null

// 1. Пошук міст
const searchCity = () => {
  clearTimeout(debounceTimeout)
  if (citySearchQuery.value.length < 2) {
    cities.value = []
    return
  }

  debounceTimeout = setTimeout(async () => {
    isSearchingCity.value = true
    try {
      // ВИПРАВЛЕННЯ: Використовуємо fetch замість axios для запитів до НП
      const res = await fetch('https://api.novaposhta.ua/v2.0/json/', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          apiKey: NP_API_KEY,
          modelName: 'Address',
          calledMethod: 'searchSettlements',
          methodProperties: {
            CityName: citySearchQuery.value,
            Limit: "50"
          }
        })
      })
      const data = await res.json()

      if (data.success && data.data.length > 0) {
        cities.value = data.data[0].Addresses
      } else {
        cities.value = []
      }
    } catch (e) {
      console.error('Помилка пошуку міст:', e)
    } finally {
      isSearchingCity.value = false
    }
  }, 500)
}

// 2. Вибір міста та завантаження відділень
const selectCity = async (city) => {
  selectedCity.value = city
  citySearchQuery.value = city.Present // Показуємо повну назву в інпуті
  cities.value = [] // Ховаємо випадаючий список
  selectedWarehouse.value = null

  await fetchWarehouses(city.Ref)
}

// 3. Завантаження відділень
const fetchWarehouses = async (settlementRef) => {
  if (!NP_API_KEY) {
    console.error('🚨 КЛЮЧ АПІ НЕ ЗНАЙДЕНО! Переконайся, що файл .env існує, змінна називається VITE_NP_API_KEY.')
    return
  }

  isLoadingWarehouses.value = true
  try {
    // ВИПРАВЛЕННЯ: Використовуємо fetch замість axios для запитів до НП
    const res = await fetch('https://api.novaposhta.ua/v2.0/json/', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        apiKey: NP_API_KEY,
        modelName: 'Address',
        calledMethod: 'getWarehouses',
        methodProperties: {
          SettlementRef: settlementRef
        }
      })
    })
    const data = await res.json()

    if (data.success) {
      warehouses.value = data.data
    } else {
      console.error('Помилка від Нової Пошти:', data.errors)
    }
  } catch (e) {
    console.error('Помилка мережі при завантаженні відділень:', e)
  } finally {
    isLoadingWarehouses.value = false
  }
}

// Скидання вибраного міста, якщо користувач почав вводити нове
const handleCityInput = () => {
  if (selectedCity.value) {
    selectedCity.value = null
    warehouses.value = []
    selectedWarehouse.value = null
  }
  searchCity()
}

// 4. Фільтрація: розділяємо Поштомати та звичайні Відділення
const filteredWarehouses = computed(() => {
  if (!warehouses.value.length) return []

  if (deliveryType.value === 'postmat') {
    return warehouses.value.filter(w => w.Description.toLowerCase().includes('поштомат'))
  } else {
    // Відділення (все, що НЕ поштомат)
    return warehouses.value.filter(w => !w.Description.toLowerCase().includes('поштомат'))
  }
})

// Скидаємо вибране відділення при зміні типу доставки
watch(deliveryType, () => {
  selectedWarehouse.value = null
})

// --- ПІДСУМОК ЗАМОВЛЕННЯ ---
const cartTotal = computed(() => {
  if (cartStore.totalPrice) return cartStore.totalPrice
  return cartStore.items.reduce((sum, item) => sum + (item.price * (item.quantity || 1)), 0)
})

// Відправка замовлення
const submitOrder = async () => {
  if (!selectedCity.value || !selectedWarehouse.value || !customer.value.phone) {
    alert('Будь ласка, заповніть всі обов\'язкові поля доставки та контактів!')
    return
  }

  // Відправляємо дані на наш Django бекенд
  try {
    const orderData = {
      full_name: `${customer.value.firstName} ${customer.value.lastName}`.trim(),
      phone: customer.value.phone,
      city: selectedCity.value.Present,
      nova_poshta: selectedWarehouse.value.Description,
      total_price: cartTotal.value,
      items: cartStore.items.map(item => ({
        id: item.id.toString(),
        quantity: item.quantity || 1
      }))
    }

    const response = await axios.post('http://127.0.0.1:8000/api/checkout/', orderData)

    if (response.status === 200) {
      alert('Замовлення успішно оформлено! 🎉')
      cartStore.clearCart() // Якщо цей метод є у твоєму сторі
      router.push('/')
    }
  } catch (error) {
    console.error('Помилка при оформленні:', error)
    alert('Виникла помилка при збереженні замовлення. Спробуйте ще раз.')
  }
}
</script>

<template>
  <div class="checkout-layout">
    <div class="header-simple">
      <button class="back-btn" @click="router.push('/cart')">← Назад до кошика</button>
      <h1>Оформлення замовлення</h1>
    </div>

    <div class="checkout-grid" v-if="cartStore.items && cartStore.items.length > 0">

      <div class="forms-column">

        <section class="checkout-card">
          <div class="card-header">
            <span class="step-num">1</span>
            <h2>Контактні дані</h2>
          </div>
          <div class="form-grid">
            <div class="input-wrapper">
              <label>Ім'я *</label>
              <input v-model="customer.firstName" type="text" placeholder="Іван" required>
            </div>
            <div class="input-wrapper">
              <label>Прізвище</label>
              <input v-model="customer.lastName" type="text" placeholder="Франко">
            </div>
            <div class="input-wrapper">
              <label>Телефон *</label>
              <input v-model="customer.phone" type="tel" placeholder="+38 (099) 000-00-00" required>
            </div>
            <div class="input-wrapper">
              <label>Email</label>
              <input v-model="customer.email" type="email" placeholder="ivan@example.com">
            </div>
          </div>
        </section>

        <section class="checkout-card">
          <div class="card-header">
            <span class="step-num">2</span>
            <h2>Доставка <img src="https://novaposhta.ua/runtime/cache/320x95/np-logo-ukr.png" alt="NP" class="np-logo"></h2>
          </div>

          <div class="input-wrapper city-search-wrapper">
            <label>Населений пункт *</label>
            <input
              v-model="citySearchQuery"
              @input="handleCityInput"
              type="text"
              placeholder="Почніть вводити назву міста..."
              autocomplete="off"
            >
            <div v-if="isSearchingCity" class="loading-indicator">⏳ Шукаємо...</div>

            <ul v-if="cities.length > 0 && !selectedCity" class="city-dropdown">
              <li v-for="city in cities" :key="city.Ref" @click="selectCity(city)">
                <span class="city-name">{{ city.MainDescription }}</span>
                <span class="city-region">{{ city.Area }} обл., {{ city.SettlementTypeCode }}</span>
              </li>
            </ul>
          </div>

          <div class="delivery-types" v-if="selectedCity">
            <label class="type-card" :class="{ active: deliveryType === 'branch' }">
              <input type="radio" value="branch" v-model="deliveryType">
              <span class="icon">🏢</span>
              <div class="text">
                <strong>У відділення</strong>
                <span>Від 70 ₴</span>
              </div>
            </label>
            <label class="type-card" :class="{ active: deliveryType === 'postmat' }">
              <input type="radio" value="postmat" v-model="deliveryType">
              <span class="icon">📦</span>
              <div class="text">
                <strong>У поштомат</strong>
                <span>Від 50 ₴</span>
              </div>
            </label>
          </div>

          <div class="input-wrapper" v-if="selectedCity && !isLoadingWarehouses">
            <label>{{ deliveryType === 'postmat' ? 'Оберіть поштомат *' : 'Оберіть відділення *' }}</label>
            <select v-model="selectedWarehouse" class="modern-select">
              <option :value="null" disabled>Оберіть зі списку...</option>
              <option v-for="w in filteredWarehouses" :key="w.Ref" :value="w">
                {{ w.Description }}
              </option>
            </select>
            <p v-if="filteredWarehouses.length === 0" class="error-msg">
              У цьому місті немає доступних {{ deliveryType === 'postmat' ? 'поштоматів' : 'відділень' }}.
            </p>
          </div>

          <div v-if="isLoadingWarehouses" class="loading-state">
            Завантаження списку відділень...
          </div>
        </section>

      </div>

      <aside class="summary-column">
        <div class="summary-card">
          <h2>Разом до сплати</h2>

          <div class="items-list">
            <div class="summary-item" v-for="item in cartStore.items" :key="item.id">
              <div class="item-info">
                <span class="item-name">{{ item.name }}</span>
                <span class="item-qty">x{{ item.quantity || 1 }}</span>
              </div>
              <span class="item-price">{{ item.price * (item.quantity || 1) }} ₴</span>
            </div>
          </div>

          <div class="totals">
            <div class="tot-row">
              <span>Вартість товарів</span>
              <span>{{ cartTotal }} ₴</span>
            </div>
            <div class="tot-row">
              <span>Доставка</span>
              <span class="highlight">За тарифами перевізника</span>
            </div>
            <div class="tot-row grand-total">
              <span>До сплати</span>
              <span>{{ cartTotal }} ₴</span>
            </div>
          </div>

          <button class="submit-btn" @click="submitOrder">
            Підтвердити замовлення 🚀
          </button>
        </div>
      </aside>

    </div>

    <div v-else class="empty-state">
      <span class="icon">🛒</span>
      <h2>Ваш кошик порожній</h2>
      <p>Схоже, ви ще не обрали своє ідеальне екіпірування.</p>
      <button class="return-btn" @click="router.push('/')">Повернутися до каталогу</button>
    </div>

  </div>
</template>

<style scoped>
.checkout-layout { max-width: 1200px; margin: 0 auto; padding: 20px; }

.header-simple { display: flex; align-items: center; gap: 20px; margin-bottom: 40px; }
.back-btn { background: #f1f5f9; border: none; padding: 10px 20px; border-radius: 12px; font-weight: 700; color: #64748b; cursor: pointer; transition: 0.2s; }
.back-btn:hover { background: #e2e8f0; color: #0f172a; }
h1 { margin: 0; font-size: 2rem; font-weight: 900; color: #0f172a; }

.checkout-grid { display: grid; grid-template-columns: 1.5fr 1fr; gap: 40px; align-items: start; }

/* ФОРМИ */
.forms-column { display: flex; flex-direction: column; gap: 30px; }
.checkout-card { background: white; padding: 30px; border-radius: 24px; box-shadow: 0 10px 30px rgba(0,0,0,0.03); border: 1px solid #f1f5f9; }

.card-header { display: flex; align-items: center; gap: 15px; margin-bottom: 25px; }
.step-num { width: 36px; height: 36px; background: #0f172a; color: white; border-radius: 50%; display: flex; align-items: center; justify-content: center; font-weight: 800; font-size: 1.1rem; }
.card-header h2 { margin: 0; font-size: 1.4rem; font-weight: 800; display: flex; align-items: center; gap: 15px; }
.np-logo { height: 20px; object-fit: contain; }

.form-grid { display: grid; grid-template-columns: 1fr 1fr; gap: 20px; }
.input-wrapper { display: flex; flex-direction: column; gap: 8px; margin-bottom: 20px; position: relative; }
.input-wrapper label { font-size: 0.9rem; font-weight: 700; color: #475569; }
.input-wrapper input, .modern-select {
  width: 100%; padding: 14px 18px; border: 2px solid #e2e8f0; border-radius: 14px;
  font-family: inherit; font-size: 1rem; transition: 0.3s; background: #f8fafc; color: #0f172a; box-sizing: border-box;
}
.input-wrapper input:focus, .modern-select:focus { outline: none; border-color: #6366f1; background: white; box-shadow: 0 0 0 4px rgba(99, 102, 241, 0.1); }

/* АВТОКОМПЛІТ МІСТ */
.city-dropdown {
  position: absolute; top: calc(100% + 5px); left: 0; width: 100%; background: white;
  border-radius: 14px; box-shadow: 0 10px 30px rgba(0,0,0,0.1); border: 1px solid #e2e8f0;
  max-height: 250px; overflow-y: auto; z-index: 10; list-style: none; padding: 5px; margin: 0;
}
.city-dropdown li { padding: 12px 15px; border-radius: 10px; cursor: pointer; transition: 0.2s; display: flex; flex-direction: column; }
.city-dropdown li:hover { background: #f8fafc; }
.city-name { font-weight: 700; color: #0f172a; }
.city-region { font-size: 0.8rem; color: #64748b; }
.loading-indicator { position: absolute; right: 15px; top: 40px; font-size: 0.9rem; color: #6366f1; font-weight: 600; }

/* ТИПИ ДОСТАВКИ */
.delivery-types { display: grid; grid-template-columns: 1fr 1fr; gap: 15px; margin-bottom: 25px; }
.type-card {
  display: flex; align-items: center; gap: 15px; padding: 15px 20px; border: 2px solid #e2e8f0;
  border-radius: 16px; cursor: pointer; transition: 0.3s; background: #f8fafc;
}
.type-card input { display: none; }
.type-card .icon { font-size: 1.8rem; }
.type-card .text { display: flex; flex-direction: column; }
.type-card .text strong { color: #0f172a; font-size: 1rem; }
.type-card .text span { color: #64748b; font-size: 0.85rem; font-weight: 600; }
.type-card.active { border-color: #ef4444; background: #fef2f2; }

/* ПРАВА КОЛОНКА */
.summary-column { position: sticky; top: 100px; }
.summary-card { background: #0f172a; color: white; padding: 30px; border-radius: 32px; box-shadow: 0 20px 40px rgba(0,0,0,0.1); }
.summary-card h2 { margin: 0 0 25px 0; font-size: 1.5rem; font-weight: 800; }

.items-list { border-bottom: 1px solid rgba(255,255,255,0.1); padding-bottom: 20px; margin-bottom: 20px; display: flex; flex-direction: column; gap: 15px; }
.summary-item { display: flex; justify-content: space-between; align-items: center; }
.item-info { display: flex; flex-direction: column; gap: 4px; }
.item-name { font-weight: 600; font-size: 0.95rem; }
.item-qty { font-size: 0.8rem; color: #94a3b8; }
.item-price { font-weight: 800; color: #00ff88; }

.totals { display: flex; flex-direction: column; gap: 12px; margin-bottom: 30px; }
.tot-row { display: flex; justify-content: space-between; font-weight: 600; color: #cbd5e1; font-size: 0.95rem; }
.tot-row .highlight { color: #3b82f6; }
.grand-total { font-size: 1.4rem; font-weight: 900; color: white; margin-top: 10px; padding-top: 15px; border-top: 1px solid rgba(255,255,255,0.1); }

.submit-btn { width: 100%; background: #00ff88; color: #0f172a; border: none; padding: 20px; border-radius: 18px; font-size: 1.2rem; font-weight: 900; cursor: pointer; transition: 0.3s; }
.submit-btn:hover { transform: translateY(-3px); box-shadow: 0 10px 25px rgba(0,255,136,0.3); }

/* ПУСТИЙ КОШИК */
.empty-state { text-align: center; padding: 100px 20px; background: white; border-radius: 32px; }
.empty-state .icon { font-size: 5rem; display: block; margin-bottom: 20px; }
.empty-state h2 { font-size: 2rem; font-weight: 900; color: #0f172a; margin-bottom: 10px; }
.empty-state p { color: #64748b; font-size: 1.1rem; margin-bottom: 30px; }
.return-btn { background: #0f172a; color: white; border: none; padding: 15px 30px; border-radius: 14px; font-weight: 800; cursor: pointer; font-size: 1.1rem; }

@media (max-width: 900px) {
  .checkout-grid { grid-template-columns: 1fr; }
  .form-grid { grid-template-columns: 1fr; }
}
</style>
