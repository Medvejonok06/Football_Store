<script setup>
import { ref, computed, watch, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useCartStore } from '../stores/cart'
import { useAuthStore } from '../stores/auth'
import axios from 'axios'
import AppNotification from '../components/AppNotification.vue'

const router = useRouter()
const cartStore = useCartStore()
const authStore = useAuthStore()

// --- СТАН ДЛЯ ПОМИЛОК (ЗБОКУ) ---
const notification = ref({
  show: false,
  message: '',
  type: 'error'
})

const showToast = (msg, type = 'error') => {
  notification.value.show = false
  setTimeout(() => {
    notification.value.message = msg
    notification.value.type = type
    notification.value.show = true
  }, 10)
}

// --- СТАН ДЛЯ МОДАЛЬНОГО ВІКНА УСПІХУ (ПО ЦЕНТРУ) ---
const showSuccessModal = ref(false)

const handleSuccessOk = () => {
  showSuccessModal.value = false
  router.push('/') // Повертаємо в каталог тільки після кліку "ОК"
}

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

// --- ОФОРМЛЕННЯ ЗАМОВЛЕННЯ ---
const submitOrder = async () => {
  if (!selectedCity.value || !selectedWarehouse.value || !customer.value.phone) {
    showToast('Будь ласка, заповніть всі обов\'язкові поля!', 'error')
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

    if (response.status === 200 || response.status === 201) {
      cartStore.clearCart()
      showSuccessModal.value = true
    }
  } catch (e) {
    console.error('Помилка при оформленні замовлення:', e)
    showToast('❌ Виникла помилка. Спробуйте ще раз.', 'error')
  }
}
</script>

<template>
  <div class="checkout-layout">

    <AppNotification
      v-if="notification.show"
      :message="notification.message"
      :type="notification.type"
      @close="notification.show = false"
    />

    <Transition name="fade">
      <div v-if="showSuccessModal" class="modal-backdrop">
        <div class="modal-glass success-modal">
          <div class="icon-circle">✅</div>
          <h3 class="modal-title">Замовлення успішно оформлено!</h3>
          <p class="modal-msg">
            Дякуємо за ваш вибір. Наш менеджер незабаром зв'яжеться з вами для уточнення деталей замовлення.
          </p>
          <button class="ok-btn" @click="handleSuccessOk">Зрозуміло, в каталог</button>
        </div>
      </div>
    </Transition>

    <div class="header-simple">
      <button class="back-btn outline-btn" @click="router.push('/')">
        ← Назад до каталогу
      </button>
      <h1>Оформлення замовлення</h1>
    </div>

    <!-- ПОРОЖНІЙ КОШИК -->
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

    <!-- ЗАПОВНЕНИЙ КОШИК -->
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
            <h2>Доставка НП</h2>
          </div>
          <div class="input-wrapper city-search-wrapper">
            <label>Населений пункт *</label>
            <input v-model="citySearchQuery" @input="handleCityInput" type="text" placeholder="Введіть назву міста..." autocomplete="off">
            <div v-if="isSearchingCity" class="loading-indicator">⏳ Шукаємо...</div>
            <ul v-if="cities.length > 0 && !selectedCity" class="city-dropdown">
              <li v-for="city in cities" :key="city.Ref" @click="selectCity(city)">
                <span class="city-name">{{ city.MainDescription }}, </span>
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

              <div class="item-price-actions">
                <span class="item-price">{{ item.price * (item.quantity || 1) }} ₴</span>
                <button @click.prevent="cartStore.removeFromCart(item.id)" class="remove-btn" title="Видалити товар">
                  <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                    <polyline points="3 6 5 6 21 6"></polyline>
                    <path d="M19 6v14a2 2 0 0 1-2 2H7a2 2 0 0 1-2-2V6m3 0V4a2 2 0 0 1 2-2h4a2 2 0 0 1 2 2v2"></path>
                    <line x1="10" y1="11" x2="10" y2="17"></line>
                    <line x1="14" y1="11" x2="14" y2="17"></line>
                  </svg>
                </button>
              </div>
            </div>
          </div>

          <div class="totals">
            <div class="tot-row grand-total">
              <span>До сплати</span>
              <span>{{ cartTotal }} ₴</span>
            </div>
          </div>
          <button class="submit-btn" @click.prevent="submitOrder">Підтвердити 🚀</button>
        </div>
      </aside>
    </div>
  </div>
</template>

<style scoped>
/* СТИЛІ ДЛЯ НОВОГО МОДАЛЬНОГО ВІКНА ПО ЦЕНТРУ */
.modal-backdrop {
  position: fixed;
  top: 0;
  left: 0;
  width: 100vw;
  height: 100vh;
  background: rgba(15, 23, 42, 0.6);
  backdrop-filter: blur(10px);
  -webkit-backdrop-filter: blur(10px);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 999999;
}

.success-modal {
  background: white;
  border-radius: 32px;
  padding: 40px;
  width: 90%;
  max-width: 450px;
  text-align: center;
  box-shadow: 0 30px 60px rgba(0, 0, 0, 0.2);
  transform: translateY(0);
}

.icon-circle {
  width: 90px;
  height: 90px;
  background: #e0fae9;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 3rem;
  margin: 0 auto 20px;
  box-shadow: 0 10px 25px rgba(0, 255, 136, 0.2);
}

.modal-title {
  margin: 0 0 15px 0;
  font-size: 1.6rem;
  font-weight: 900;
  color: #0f172a;
}

.modal-msg {
  margin: 0 0 30px 0;
  color: #64748b;
  font-weight: 600;
  font-size: 1.05rem;
  line-height: 1.5;
}

.ok-btn {
  width: 100%;
  background: #0f172a;
  color: white;
  border: none;
  padding: 16px;
  border-radius: 16px;
  font-weight: 800;
  font-size: 1.05rem;
  cursor: pointer;
  transition: all 0.3s ease;
  box-shadow: 0 10px 20px rgba(15, 23, 42, 0.15);
}
.ok-btn:hover {
  background: #00ff88;
  color: #0f172a;
  transform: translateY(-3px);
  box-shadow: 0 15px 25px rgba(0, 255, 136, 0.3);
}

.fade-enter-active, .fade-leave-active { transition: opacity 0.3s ease, transform 0.3s ease; }
.fade-enter-from, .fade-leave-to { opacity: 0; }
.fade-enter-from .success-modal, .fade-leave-to .success-modal { transform: scale(0.9) translateY(20px); }

/* ОСНОВНІ СТИЛІ СТОРІНКИ */
.checkout-layout { max-width: 1200px; margin: 0 auto; padding: 20px; color: #0f172a; }
.header-simple { display: flex; align-items: center; gap: 20px; margin-bottom: 40px; }

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

/* ТУТ ВИПРАВЛЕНО ЗДАВЛЕННЯ БОКОВОЇ ПАНЕЛІ (Тепер права колонка фіксована 380px) */
.checkout-grid { display: grid; grid-template-columns: 1fr 380px; gap: 40px; }

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

/* ТУТ ДОДАНО ВІДСТУПИ МІЖ СЛОВОМ ТА ЦІНОЮ В КАРТКАХ ДОСТАВКИ */
.type-card .text {
  display: flex;
  flex-direction: column;
  gap: 4px;
}
.type-card .text strong {
  font-size: 1.05rem;
  color: #0f172a;
}
.type-card .text span {
  font-size: 0.85rem;
  color: #64748b;
}

.summary-card { background: #0f172a; color: white; padding: 30px; border-radius: 24px; position: sticky; top: 20px; box-sizing: border-box; }

.items-list { margin-bottom: 20px; }
.summary-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: 15px;
  margin-bottom: 15px;
  padding-bottom: 15px;
  border-bottom: 1px solid rgba(255, 255, 255, 0.05);
}
.item-info { display: flex; flex-direction: column; gap: 4px; flex: 1; }
.item-name {
  display: -webkit-box; -webkit-line-clamp: 2; line-clamp: 2;
  -webkit-box-orient: vertical; overflow: hidden; font-weight: 600; line-height: 1.4;
}
.item-qty { color: #94a3b8; font-size: 0.85rem; font-weight: 700; }

.item-price-actions { display: flex; align-items: center; gap: 12px; }
.item-price { font-weight: 800; font-size: 1.1rem; }

.remove-btn {
  background: rgba(239, 68, 68, 0.1);
  color: #ef4444;
  border: none;
  width: 32px;
  height: 32px;
  border-radius: 8px;
  display: flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  transition: all 0.3s ease;
}
.remove-btn:hover {
  background: #ef4444;
  color: white;
  transform: translateY(-2px) rotate(5deg);
  box-shadow: 0 5px 15px rgba(239, 68, 68, 0.3);
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
