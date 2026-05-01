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
const isWarehouseOpen = ref(false)

const selectWarehouseItem = (w) => {
  selectedWarehouse.value = w
  isWarehouseOpen.value = false
}
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
                <!-- Зміна ціни на Безкоштовно -->
                <span v-if="cartStore.isFreeDelivery" class="free-shipping-text">Безкоштовно</span>
                <span v-else>Від 70 ₴</span>
              </div>
            </label>
            <label class="type-card" :class="{ active: deliveryType === 'postmat' }">
              <input type="radio" value="postmat" v-model="deliveryType">
              <span class="icon">📦</span>
              <div class="text">
                <strong>Поштомат</strong>
                <!-- Зміна ціни на Безкоштовно -->
                <span v-if="cartStore.isFreeDelivery" class="free-shipping-text">Безкоштовно</span>
                <span v-else>Від 50 ₴</span>
              </div>
            </label>
          </div>

          <div class="input-wrapper" v-if="selectedCity && !isLoadingWarehouses">
            <label>{{ deliveryType === 'postmat' ? 'Оберіть поштомат *' : 'Оберіть відділення *' }}</label>
            <div class="custom-select-wrapper">
              <div class="custom-select-trigger" @click="isWarehouseOpen = !isWarehouseOpen" :class="{ 'is-open': isWarehouseOpen }">
                <span class="selected-text">{{ selectedWarehouse ? selectedWarehouse.Description : 'Оберіть зі списку...' }}</span>
                <span class="arrow">▼</span>
              </div>

              <Transition name="fade">
                <ul v-if="isWarehouseOpen" class="custom-options-list">
                  <li
                    v-for="w in filteredWarehouses"
                    :key="w.Ref"
                    @click="selectWarehouseItem(w)"
                    :class="{ 'selected': selectedWarehouse?.Ref === w.Ref }"
                  >
                    {{ w.Description }}
                  </li>
                </ul>
              </Transition>
            </div>
          </div>
        </section>
      </div>

      <aside class="summary-column">
        <div class="summary-card">
          <h2>Разом до сплати</h2>

          <!-- ДОДАНО: ПРОГРЕС-БАР БЕЗКОШТОВНОЇ ДОСТАВКИ -->
          <div class="delivery-promo glass-card">
            <div class="promo-header">
              <span class="icon">{{ cartStore.isFreeDelivery ? '🚀' : '📦' }}</span>
              <span v-if="cartStore.isFreeDelivery" class="status-text success">
                Вітаємо! Безкоштовна доставка активована
              </span>
              <span v-else class="status-text">
                До безкоштовної доставки: <strong>{{ cartStore.amountToFreeDelivery }} ₴</strong>
              </span>
            </div>

            <div class="progress-container">
              <div
                class="progress-fill"
                :style="{ width: cartStore.deliveryProgress + '%' }"
                :class="{ 'is-complete': cartStore.isFreeDelivery }"
              ></div>
            </div>

            <p class="promo-hint">
              * Безкоштовна доставка діє при замовленні товарів без знижок на суму від 5000 ₴
            </p>
          </div>

          <div class="items-list">
            <div class="summary-item" v-for="item in cartStore.items" :key="item.id">
              <div class="item-info">
                <span class="item-name">{{ item.name }}</span>
                <span class="item-meta">
                  <span class="item-qty">x{{ item.quantity || 1 }}</span>
                  <span v-if="item.size || item.selectedSize" class="item-size">
                    • Розмір: {{ item.size || item.selectedSize }}
                  </span>
                </span>
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
/* --- МОДАЛЬНЕ ВІКНО УСПІХУ (ТЕМНЕ СКЛО) --- */
.modal-backdrop {
  position: fixed; top: 0; left: 0; width: 100vw; height: 100vh;
  background: rgba(11, 15, 25, 0.8); backdrop-filter: blur(12px);
  display: flex; align-items: center; justify-content: center; z-index: 999999;
}

.success-modal {
  background: rgba(17, 24, 39, 0.95); border: 1px solid rgba(255, 255, 255, 0.12);
  border-radius: 32px; padding: 40px; width: 90%; max-width: 450px; text-align: center;
  box-shadow: 0 30px 60px rgba(0, 0, 0, 0.5), 0 0 40px rgba(0, 255, 136, 0.1);
}

.icon-circle {
  width: 90px; height: 90px; margin: 0 auto 20px;
  background: rgba(0, 255, 136, 0.1); border: 1px solid rgba(0, 255, 136, 0.3);
  border-radius: 50%; display: flex; align-items: center; justify-content: center; font-size: 3rem;
  box-shadow: 0 10px 25px rgba(0, 255, 136, 0.2);
}

.modal-title { margin: 0 0 15px 0; font-size: 1.6rem; font-weight: 900; color: white; }
.modal-msg { margin: 0 0 30px 0; color: #94a3b8; font-weight: 600; font-size: 1.05rem; line-height: 1.5; }

.ok-btn {
  width: 100%; background: white; color: #0f172a; border: none; padding: 16px; border-radius: 16px;
  font-weight: 900; font-size: 1.05rem; cursor: pointer; transition: 0.3s;
}
.ok-btn:hover { background: #00ff88; transform: translateY(-3px); box-shadow: 0 15px 25px rgba(0, 255, 136, 0.3); }

.fade-enter-active, .fade-leave-active { transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1); }
.fade-enter-from, .fade-leave-to { opacity: 0; transform: scale(0.95) translateY(20px); }

/* --- ОСНОВНІ СТИЛІ СТОРІНКИ --- */
.checkout-layout { max-width: 1200px; margin: 0 auto; padding: 20px; color: #f3f4f6; }
.header-simple { display: flex; align-items: center; gap: 20px; margin-bottom: 40px; }

/* КНОПКА "НАЗАД" */
.back-btn {
  background: rgba(255, 255, 255, 0.05); border: 1px solid rgba(255, 255, 255, 0.1);
  padding: 10px 20px; border-radius: 12px; font-weight: 800; font-size: 0.95rem;
  color: #94a3b8; cursor: pointer; transition: 0.3s;
}
.back-btn:hover {
  border-color: #00ff88; color: #00ff88; background: rgba(0, 255, 136, 0.05); transform: translateX(-5px);
}

h1 { font-size: 2rem; font-weight: 900; color: white; margin: 0; }

/* --- ПОРОЖНІЙ КОШИК (GLASSMORPHISM) --- */
.glass-panel {
  background: rgba(17, 24, 39, 0.7); backdrop-filter: blur(15px);
  border: 1px solid rgba(255, 255, 255, 0.1); border-radius: 32px;
  box-shadow: 0 20px 50px rgba(0, 0, 0, 0.4);
}

.gradient-border { position: relative; }
.gradient-border::before {
  content: ""; position: absolute; inset: 0; border-radius: 32px; padding: 1px;
  background: linear-gradient(135deg, rgba(99, 102, 241, 0.4), rgba(0, 255, 136, 0.4));
  -webkit-mask: linear-gradient(#fff 0 0) content-box, linear-gradient(#fff 0 0);
  mask: linear-gradient(#fff 0 0) content-box, linear-gradient(#fff 0 0);
  -webkit-mask-composite: xor; mask-composite: exclude; pointer-events: none;
}

.empty-state-container { text-align: center; padding: 100px 30px; margin-top: 20px; }
.empty-state-content { max-width: 500px; margin: 0 auto; display: flex; flex-direction: column; align-items: center; }

.icon-box { position: relative; margin-bottom: 30px; }
.main-icon { font-size: 6rem; position: relative; z-index: 2; display: block; animation: float 3s ease-in-out infinite; }
.purple-glow { filter: drop-shadow(0 10px 25px rgba(0, 255, 136, 0.3)); }

@keyframes float { 0% { transform: translateY(0px); } 50% { transform: translateY(-10px); } 100% { transform: translateY(0px); } }

.empty-title { font-size: 2.2rem; font-weight: 900; color: white; margin: 0 0 15px 0; }
.empty-text { font-size: 1.1rem; color: #94a3b8; margin: 0 0 40px 0; line-height: 1.6; }

/* ГОЛОВНА КНОПКА CTA */
.return-btn {
  background: linear-gradient(135deg, #00ff88, #10b981); color: #0f172a; border: none;
  padding: 18px 36px; border-radius: 18px; font-weight: 900; font-size: 1.1rem;
  cursor: pointer; transition: all 0.3s ease; display: flex; align-items: center; gap: 12px;
  box-shadow: 0 10px 25px rgba(0, 255, 136, 0.3); text-transform: uppercase; letter-spacing: 0.5px;
}
.return-btn:hover { transform: translateY(-3px); box-shadow: 0 15px 35px rgba(0, 255, 136, 0.5); }
.btn-arrow { opacity: 0.7; transition: 0.3s; font-size: 1.3rem; }
.return-btn:hover .btn-arrow { opacity: 1; transform: translateX(6px); }

/* --- ЗАПОВНЕНИЙ КОШИК (АПГРЕЙД ДЛЯ ФОРМ) --- */
.checkout-grid { display: grid; grid-template-columns: 1fr 380px; gap: 40px; }

.checkout-card {
  background: rgba(17, 24, 39, 0.7); backdrop-filter: blur(10px);
  padding: 30px; border-radius: 24px; border: 1px solid rgba(255, 255, 255, 0.1); margin-bottom: 20px;
}

.card-header { display: flex; align-items: center; gap: 15px; margin-bottom: 25px; }
.card-header h2 { color: white; margin: 0; }
.step-num { width: 32px; height: 32px; background: rgba(99, 102, 241, 0.2); color: #818cf8; border: 1px solid rgba(99, 102, 241, 0.5); border-radius: 50%; display: flex; align-items: center; justify-content: center; font-weight: 800; }

.form-grid { display: grid; grid-template-columns: 1fr 1fr; gap: 15px; }
.input-wrapper { display: flex; flex-direction: column; gap: 8px; position: relative; }
.input-wrapper label { color: #cbd5e1; font-weight: 600; font-size: 0.9rem; }
.input-wrapper input, .modern-select {
  padding: 14px; border: 1px solid rgba(255, 255, 255, 0.1); border-radius: 12px;
  font-family: inherit; font-size: 0.95rem; background: rgba(0, 0, 0, 0.3); color: white; transition: 0.3s;
}
.input-wrapper input:focus, .modern-select:focus { border-color: #00ff88; outline: none; background: rgba(0, 0, 0, 0.5); box-shadow: 0 0 10px rgba(0, 255, 136, 0.1); }
.modern-select option { background: #0f172a; color: white; }

.city-dropdown {
  position: absolute; top: 100%; left: 0; width: 100%; background: #1e293b;
  border: 1px solid rgba(255, 255, 255, 0.1); border-radius: 12px; z-index: 100; list-style: none; padding: 5px; box-shadow: 0 15px 30px rgba(0,0,0,0.5); color: white;
}
.city-dropdown li { padding: 10px; cursor: pointer; border-radius: 8px; transition: 0.2s; }
.city-dropdown li:hover { background: rgba(255, 255, 255, 0.05); color: #00ff88; }
.city-region { color: #94a3b8; font-size: 0.85rem; }

.delivery-types { display: grid; grid-template-columns: 1fr 1fr; gap: 15px; margin: 20px 0; }
.type-card {
  padding: 15px; border: 1px solid rgba(255, 255, 255, 0.1); border-radius: 14px; cursor: pointer;
  display: flex; align-items: center; gap: 12px; transition: 0.3s; background: rgba(0, 0, 0, 0.3); color: white;
}
.type-card.active { border-color: #00ff88; background: rgba(0, 255, 136, 0.05); }
.type-card input { display: none; }
.type-card .text { display: flex; flex-direction: column; gap: 4px; }
.type-card .text strong { font-size: 1.05rem; color: white; }
.type-card .text span { font-size: 0.85rem; color: #94a3b8; }
.free-shipping-text { color: #00ff88 !important; font-weight: 800; text-shadow: 0 0 8px rgba(0, 255, 136, 0.3); }

/* ПРАВА КОЛОНКА (СУМА) */
.summary-card { background: rgba(17, 24, 39, 0.9); border: 1px solid rgba(255, 255, 255, 0.12); padding: 30px; border-radius: 24px; position: sticky; top: 20px; box-sizing: border-box; backdrop-filter: blur(15px); }
.summary-card h2 { color: white; margin-top: 0; }

/* --- DELIVERY PROMO (ПРОГРЕС-БАР ДОСТАВКИ) --- */
.delivery-promo {
  padding: 20px;
  margin-bottom: 25px;
  background: rgba(255, 255, 255, 0.03) !important;
  border-radius: 20px !important;
}

.promo-header {
  display: flex;
  align-items: center;
  gap: 12px;
  margin-bottom: 12px;
}

.status-text {
  font-size: 0.95rem;
  font-weight: 700;
  color: #94a3b8;
}

.status-text.success {
  color: #00ff88;
  text-shadow: 0 0 10px rgba(0, 255, 136, 0.3);
}

.progress-container {
  width: 100%;
  height: 8px;
  background: rgba(0, 0, 0, 0.3);
  border-radius: 10px;
  overflow: hidden;
  border: 1px solid rgba(255, 255, 255, 0.05);
}

.progress-fill {
  height: 100%;
  background: linear-gradient(90deg, #6366f1, #a855f7);
  transition: width 0.6s cubic-bezier(0.175, 0.885, 0.32, 1.275);
  border-radius: 10px;
}

.progress-fill.is-complete {
  background: #00ff88;
  box-shadow: 0 0 15px rgba(0, 255, 136, 0.6);
}

.promo-hint {
  margin-top: 10px;
  font-size: 0.75rem;
  color: #64748b;
  font-style: italic;
  line-height: 1.4;
}

.items-list { margin-bottom: 20px; }
.summary-item { display: flex; justify-content: space-between; align-items: center; gap: 15px; margin-bottom: 15px; padding-bottom: 15px; border-bottom: 1px dashed rgba(255, 255, 255, 0.1); }
.item-info { display: flex; flex-direction: column; gap: 4px; flex: 1; }
.item-name { display: -webkit-box; -webkit-line-clamp: 2; line-clamp: 2; -webkit-box-orient: vertical; overflow: hidden; font-weight: 600; line-height: 1.4; color: white; }
.item-meta {
  display: flex;
  align-items: center;
  gap: 8px;
}

.item-qty {
  color: #94a3b8;
  font-size: 0.85rem;
  font-weight: 700;
}

.item-size {
  color: #00ff88;
  font-size: 0.85rem;
  font-weight: 800;
  background: rgba(0, 255, 136, 0.1);
  padding: 2px 8px;
  border-radius: 6px;
}

.item-price-actions { display: flex; align-items: center; gap: 12px; }
.item-price { font-weight: 800; font-size: 1.1rem; color: white; }

.remove-btn {
  background: rgba(239, 68, 68, 0.1); color: #ef4444; border: 1px solid rgba(239, 68, 68, 0.3);
  width: 32px; height: 32px; border-radius: 8px; display: flex; align-items: center; justify-content: center; cursor: pointer; transition: 0.3s ease;
}
.remove-btn:hover { background: #ef4444; color: white; transform: translateY(-2px) rotate(5deg); box-shadow: 0 5px 15px rgba(239, 68, 68, 0.3); }

.grand-total { font-size: 1.5rem; font-weight: 900; border-top: 1px solid rgba(255,255,255,0.1); padding-top: 20px; margin-top: 15px; display: flex; justify-content: space-between; color: white; }
.submit-btn { width: 100%; background: #00ff88; color: #0f172a; border: none; padding: 18px; border-radius: 14px; font-weight: 900; font-size: 1.1rem; cursor: pointer; margin-top: 25px; transition: 0.3s; text-transform: uppercase; letter-spacing: 0.5px; }
.submit-btn:hover { transform: translateY(-3px); box-shadow: 0 10px 25px rgba(0, 255, 136, 0.4); }

.forms-column {
  min-width: 0;
}

.modern-select {
  width: 100%;
  max-width: 100%;
  text-overflow: ellipsis;
  overflow: hidden;
  white-space: nowrap;
}

/* --- КАСТОМНИЙ ВИПАДАЮЧИЙ СПИСОК НП --- */
.custom-select-wrapper {
  position: relative;
  width: 100%;
}

.custom-select-trigger {
  padding: 14px;
  border: 1px solid rgba(255, 255, 255, 0.1);
  border-radius: 12px;
  background: rgba(0, 0, 0, 0.3);
  color: white;
  font-size: 0.95rem;
  cursor: pointer;
  display: flex;
  justify-content: space-between;
  align-items: center;
  transition: 0.3s;
}

.custom-select-trigger:hover, .custom-select-trigger.is-open {
  border-color: #00ff88;
  background: rgba(0, 0, 0, 0.5);
  box-shadow: 0 0 10px rgba(0, 255, 136, 0.1);
}

.selected-text {
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
  padding-right: 10px;
}

.arrow {
  font-size: 0.8rem;
  color: #94a3b8;
  transition: transform 0.3s ease;
}

.custom-select-trigger.is-open .arrow {
  transform: rotate(180deg);
  color: #00ff88;
}

.custom-options-list {
  position: absolute;
  top: calc(100% + 8px);
  left: 0;
  width: 100%;
  max-height: 250px;
  overflow-y: auto;
  background: #1e293b;
  border: 1px solid rgba(255, 255, 255, 0.1);
  border-radius: 12px;
  z-index: 1000;
  list-style: none;
  padding: 5px;
  margin: 0;
  box-shadow: 0 15px 35px rgba(0, 0, 0, 0.6);
}

.custom-options-list li {
  padding: 12px 15px;
  color: #cbd5e1;
  font-size: 0.9rem;
  cursor: pointer;
  border-radius: 8px;
  transition: 0.2s;
  line-height: 1.4;
}

.custom-options-list li:hover {
  background: rgba(0, 255, 136, 0.1);
  color: #00ff88;
}

.custom-options-list li.selected {
  background: rgba(99, 102, 241, 0.15);
  color: white;
  font-weight: bold;
  border-left: 3px solid #6366f1;
}

.custom-options-list::-webkit-scrollbar {
  width: 6px;
}
.custom-options-list::-webkit-scrollbar-track {
  background: rgba(0, 0, 0, 0.2);
  border-radius: 10px;
}
.custom-options-list::-webkit-scrollbar-thumb {
  background: rgba(255, 255, 255, 0.2);
  border-radius: 10px;
}
.custom-options-list::-webkit-scrollbar-thumb:hover {
  background: #00ff88;
}

@media (max-width: 900px) {
  .checkout-grid { grid-template-columns: 1fr; }
  .empty-state-container { padding: 60px 20px; }
  .empty-title { font-size: 1.8rem; }
  .return-btn { width: 100%; justify-content: center; }
  .form-grid { grid-template-columns: 1fr; }
}
</style>
