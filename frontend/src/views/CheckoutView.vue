<script setup>
import { ref, computed, watch, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useCartStore } from '../stores/cart'
import { useAuthStore } from '../stores/auth'
import axios from 'axios'

const router = useRouter()
const cartStore = useCartStore()
const authStore = useAuthStore()

// --- КЛЮЧ АПІ НОВОЇ ПОШТИ ---
const NP_API_KEY = import.meta.env.VITE_NP_API_KEY

// --- ДАНІ КОРИСТУВАЧА ---
const customer = ref({
  firstName: '',
  lastName: '',
  phone: '',
  email: authStore.email || ''
})

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

const deliveryType = ref('branch')
const warehouses = ref([])
const selectedWarehouse = ref(null)
const isLoadingWarehouses = ref(false)

let debounceTimeout = null

const searchCity = () => {
  clearTimeout(debounceTimeout)
  if (citySearchQuery.value.length < 2) {
    cities.value = []
    return
  }

  debounceTimeout = setTimeout(async () => {
    isSearchingCity.value = true
    try {
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

const selectCity = async (city) => {
  selectedCity.value = city
  citySearchQuery.value = city.Present
  cities.value = []
  selectedWarehouse.value = null
  await fetchWarehouses(city.Ref)
}

const fetchWarehouses = async (settlementRef) => {
  if (!NP_API_KEY) return
  isLoadingWarehouses.value = true
  try {
    const res = await fetch('https://api.novaposhta.ua/v2.0/json/', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        apiKey: NP_API_KEY,
        modelName: 'Address',
        calledMethod: 'getWarehouses',
        methodProperties: { SettlementRef: settlementRef }
      })
    })
    const data = await res.json()
    if (data.success) {
      warehouses.value = data.data
    }
  } catch (e) {
    console.error('Помилка завантаження відділень:', e)
  } finally {
    isLoadingWarehouses.value = false
  }
}

const handleCityInput = () => {
  if (selectedCity.value) {
    selectedCity.value = null
    warehouses.value = []
    selectedWarehouse.value = null
  }
  searchCity()
}

const filteredWarehouses = computed(() => {
  if (!warehouses.value.length) return []
  if (deliveryType.value === 'postmat') {
    return warehouses.value.filter(w => w.Description.toLowerCase().includes('поштомат'))
  }
  return warehouses.value.filter(w => !w.Description.toLowerCase().includes('поштомат'))
})

watch(deliveryType, () => {
  selectedWarehouse.value = null
})

const cartTotal = computed(() => {
  return cartStore.items.reduce((sum, item) => sum + (item.price * (item.quantity || 1)), 0)
})

const submitOrder = async () => {
  if (!selectedCity.value || !selectedWarehouse.value || !customer.value.phone) {
    alert('Будь ласка, заповніть всі обов\'язкові поля!')
    return
  }

  try {
    const orderData = {
      full_name: `${customer.value.firstName} ${customer.value.lastName}`.trim(),
      phone: customer.value.phone,
      city: selectedCity.value.Present,
      nova_poshta: selectedWarehouse.value.Description,
      total_price: cartTotal.value,
      items: cartStore.items.map(item => ({ id: item.id.toString(), quantity: item.quantity || 1 }))
    }
    const response = await axios.post('http://127.0.0.1:8000/api/checkout/', orderData)
    if (response.status === 200) {
      alert('Замовлення успішно оформлено! 🎉')
      cartStore.clearCart()
      router.push('/')
    }
  } catch (e) {
    // ТУТ ВИПРАВЛЕНО (e використовується в консолі)
    console.error('Помилка при оформленні замовлення:', e)
    alert('Виникла помилка при збереженні замовлення. Спробуйте ще раз.')
  }
}
</script>

<template>
  <div class="checkout-layout">
    <div class="header-simple">
      <button class="back-btn outline-btn" @click="router.push('/')">
        ← Назад до каталогу
      </button>
      <h1>Оформлення замовлення</h1>
    </div>

    <div v-if="!cartStore.items || cartStore.items.length === 0" class="empty-state-container glass-panel gradient-border">
      <div class="empty-state-content">
        <div class="icon-box purple-glow">
          <span class="main-icon">🛍️</span>
          <span class="dots-decor"></span>
        </div>

        <h2 class="empty-title">Ваш кошик порожній</h2>
        <p class="empty-text">
          Схоже, ви ще не обрали своє ідеальне екіпірування. <br>
          Ваша наступна велика гра чекає в каталозі!
        </p>

        <button class="return-btn" @click="router.push('/')">
          <span class="btn-text">Повернутися до каталогу</span>
          <span class="btn-arrow">→</span>
        </button>
      </div>
    </div>

    <div v-else class="checkout-grid">
      <div class="forms-column">
        <section class="checkout-card">
          <div class="card-header">
            <span class="step-num">1</span>
            <h2>Контактні дані</h2>
          </div>
          <div class="form-grid">
            <div class="input-wrapper">
              <label>Ім'я *</label>
              <input v-model="customer.firstName" type="text" placeholder="Ваше ім'я" required>
            </div>
            <div class="input-wrapper">
              <label>Прізвище</label>
              <input v-model="customer.lastName" type="text" placeholder="Ваше прізвище">
            </div>
            <div class="input-wrapper">
              <label>Телефон *</label>
              <input v-model="customer.phone" type="tel" placeholder="+38 (0__) ___-__-__" required>
            </div>
            <div class="input-wrapper">
              <label>Email</label>
              <input v-model="customer.email" type="email" placeholder="example@mail.com">
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
            <input v-model="citySearchQuery" @input="handleCityInput" type="text" placeholder="Введіть назву міста..." autocomplete="off">
            <div v-if="isSearchingCity" class="loading-indicator">⏳ Шукаємо...</div>
            <ul v-if="cities.length > 0 && !selectedCity" class="city-dropdown">
              <li v-for="city in cities" :key="city.Ref" @click="selectCity(city)">
                <span class="city-name">{{ city.MainDescription }}</span>
                <span class="city-region">{{ city.Area }} обл.</span>
              </li>
            </ul>
          </div>

          <div class="delivery-types" v-if="selectedCity">
            <label class="type-card" :class="{ active: deliveryType === 'branch' }">
              <input type="radio" value="branch" v-model="deliveryType">
              <span class="icon">🏢</span>
              <div class="text">
                <strong>Відділення</strong>
                <span>Від 70 ₴</span>
              </div>
            </label>
            <label class="type-card" :class="{ active: deliveryType === 'postmat' }">
              <input type="radio" value="postmat" v-model="deliveryType">
              <span class="icon">📦</span>
              <div class="text">
                <strong>Поштомат</strong>
                <span>Від 50 ₴</span>
              </div>
            </label>
          </div>

          <div class="input-wrapper" v-if="selectedCity && !isLoadingWarehouses">
            <label>{{ deliveryType === 'postmat' ? 'Оберіть поштомат *' : 'Оберіть відділення *' }}</label>
            <select v-model="selectedWarehouse" class="modern-select">
              <option :value="null" disabled>Оберіть зі списку...</option>
              <option v-for="w in filteredWarehouses" :key="w.Ref" :value="w">{{ w.Description }}</option>
            </select>
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
            <div class="tot-row grand-total">
              <span>До сплати</span>
              <span>{{ cartTotal }} ₴</span>
            </div>
          </div>
          <button class="submit-btn" @click="submitOrder">Підтвердити 🚀</button>
        </div>
      </aside>
    </div>
  </div>
</template>

<style scoped>
.checkout-layout { max-width: 1200px; margin: 0 auto; padding: 20px; color: #0f172a; }
.header-simple { display: flex; align-items: center; gap: 20px; margin-bottom: 40px; }

/* КНОПКА НАЗАД */
.back-btn {
  background: white;
  border: 2px solid #e2e8f0;
  padding: 10px 20px;
  border-radius: 12px;
  font-weight: 800;
  font-size: 0.95rem;
  color: #64748b;
  cursor: pointer;
  transition: 0.3s;
}
.back-btn:hover {
  border-color: #6366f1;
  color: #0f172a;
  transform: translateX(-5px);
}

h1 { font-size: 2rem; font-weight: 900; color: #0f172a; margin: 0; }

/* СУЧАСНИЙ ПОРОЖНІЙ СТАН (GLASSMORPHISM) */
.glass-panel {
  background: rgba(255, 255, 255, 0.6);
  backdrop-filter: blur(15px);
  border: 1px solid rgba(255, 255, 255, 0.3);
  border-radius: 32px;
  box-shadow: 0 15px 35px rgba(0,0,0,0.05);
}

.gradient-border { position: relative; }
.gradient-border::before {
  content: ""; position: absolute; inset: 0; border-radius: 32px; padding: 2px;
  background: linear-gradient(135deg, rgba(99, 102, 241, 0.3), rgba(168, 85, 247, 0.3));
  -webkit-mask: linear-gradient(#fff 0 0) content-box, linear-gradient(#fff 0 0);
  mask: linear-gradient(#fff 0 0) content-box, linear-gradient(#fff 0 0);
  -webkit-mask-composite: xor; mask-composite: exclude; pointer-events: none;
}

.empty-state-container { text-align: center; padding: 100px 30px; margin-top: 20px; }
.empty-state-content { max-width: 500px; margin: 0 auto; display: flex; flex-direction: column; align-items: center; }

.icon-box { position: relative; margin-bottom: 30px; }
.main-icon { font-size: 6rem; position: relative; z-index: 2; display: block; animation: float 3s ease-in-out infinite; }
.purple-glow { filter: drop-shadow(0 10px 20px rgba(168, 85, 247, 0.2)); }

@keyframes float { 0% { transform: translateY(0px); } 50% { transform: translateY(-10px); } 100% { transform: translateY(0px); } }

.empty-title { font-size: 2.2rem; font-weight: 900; color: #0f172a; margin: 0 0 15px 0; }
.empty-text { font-size: 1.1rem; color: #64748b; margin: 0 0 40px 0; line-height: 1.6; }

.return-btn {
  background: #0f172a; color: white; border: none; padding: 18px 36px; border-radius: 18px;
  font-weight: 800; font-size: 1.1rem; cursor: pointer; transition: all 0.3s ease;
  display: flex; align-items: center; gap: 12px; box-shadow: 0 10px 25px rgba(15, 23, 42, 0.15);
}
.return-btn:hover { background: #1e293b; transform: translateY(-3px); box-shadow: 0 15px 35px rgba(15, 23, 42, 0.25); }
.btn-arrow { opacity: 0.5; transition: 0.3s; }
.return-btn:hover .btn-arrow { opacity: 1; transform: translateX(5px); color: #00ff88; }

/* СІТКА ЗАМОВЛЕННЯ */
.checkout-grid { display: grid; grid-template-columns: 1.5fr 1fr; gap: 40px; }
.checkout-card { background: white; padding: 30px; border-radius: 24px; border: 2px solid #f1f5f9; margin-bottom: 20px;}

.card-header { display: flex; align-items: center; gap: 15px; margin-bottom: 20px; }
.step-num { width: 32px; height: 32px; background: #0f172a; color: white; border-radius: 50%; display: flex; align-items: center; justify-content: center; font-weight: 800; }

.form-grid { display: grid; grid-template-columns: 1fr 1fr; gap: 15px; }
.input-wrapper { display: flex; flex-direction: column; gap: 8px; position: relative; }
.input-wrapper input, .modern-select {
  padding: 14px; border: 2px solid #e2e8f0; border-radius: 12px; font-family: inherit; font-size: 0.95rem; background: #f8fafc;
}
.input-wrapper input:focus { border-color: #6366f1; outline: none; background: white; }

.city-dropdown {
  position: absolute; top: 100%; left: 0; width: 100%; background: white;
  border: 2px solid #e2e8f0; border-radius: 12px; z-index: 100; list-style: none; padding: 5px; box-shadow: 0 10px 25px rgba(0,0,0,0.1);
}
.city-dropdown li { padding: 10px; cursor: pointer; border-radius: 8px; }
.city-dropdown li:hover { background: #f1f5f9; }

.delivery-types { display: grid; grid-template-columns: 1fr 1fr; gap: 15px; margin: 20px 0; }
.type-card {
  padding: 15px; border: 2px solid #e2e8f0; border-radius: 14px; cursor: pointer;
  display: flex; align-items: center; gap: 12px; transition: 0.3s; background: #f8fafc;
}
.type-card.active { border-color: #6366f1; background: #f5f7ff; }
.type-card input { display: none; }

.summary-card { background: #0f172a; color: white; padding: 30px; border-radius: 24px; position: sticky; top: 20px; }
.item-name {
  display: -webkit-box; -webkit-line-clamp: 1; line-clamp: 1;
  -webkit-box-orient: vertical; overflow: hidden; font-weight: 600;
}
.grand-total { font-size: 1.5rem; font-weight: 900; border-top: 1px solid rgba(255,255,255,0.1); padding-top: 15px; margin-top: 15px; display: flex; justify-content: space-between; }
.submit-btn { width: 100%; background: #00ff88; color: #0f172a; border: none; padding: 18px; border-radius: 14px; font-weight: 900; font-size: 1.1rem; cursor: pointer; margin-top: 20px; transition: 0.3s; }
.submit-btn:hover { transform: translateY(-3px); box-shadow: 0 8px 20px rgba(0, 255, 136, 0.3); }

@media (max-width: 900px) {
  .checkout-grid { grid-template-columns: 1fr; }
  .empty-state-container { padding: 60px 20px; }
  .empty-title { font-size: 1.8rem; }
  .return-btn { width: 100%; justify-content: center; }
}
</style>
