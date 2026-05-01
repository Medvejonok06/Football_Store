<script setup>
import { ref, computed, onMounted } from 'vue'
import axios from 'axios'
import { useAuthStore } from '../stores/auth'
// 1. Імпортуємо нову модалку
import AdminModal from './AdminModal.vue'

import { Bar } from 'vue-chartjs'
import { Chart as ChartJS, Title, Tooltip, Legend, BarElement, CategoryScale, LinearScale } from 'chart.js'

ChartJS.register(Title, Tooltip, Legend, BarElement, CategoryScale, LinearScale)

const emit = defineEmits(['close'])
const authStore = useAuthStore()

const activeTab = ref('analytics')
const orders = ref([])
const analyticsData = ref(null)
const isLoading = ref(true)
const editingOrder = ref(null)

// 2. Змінні для керування модалкою
const isSuccessModalOpen = ref(false)
const modalMessage = ref('')

onMounted(async () => {
  if (!authStore.isAdmin) {
    emit('close')
    return
  }
  await fetchOrders()
  await fetchAnalytics()
  isLoading.value = false
})

const fetchOrders = async () => {
  try {
    const res = await axios.get('http://127.0.0.1:8000/api/admin-orders/')
    orders.value = res.data
  } catch (e) { console.error('Помилка замовлень', e) }
}

const fetchAnalytics = async () => {
  try {
    const res = await axios.get('http://127.0.0.1:8000/api/analytics/')
    analyticsData.value = res.data
  } catch (e) { console.error('Помилка аналітики', e) }
}

const chartData = computed(() => {
  if (!analyticsData.value || !analyticsData.value.chart_labels) return null
  return {
    labels: analyticsData.value.chart_labels,
    datasets: [
      {
        label: 'Продано одиниць',
        backgroundColor: (context) => {
          const chart = context.chart;
          const { ctx, chartArea } = chart;
          if (!chartArea) return 'rgba(0, 255, 136, 0.5)';

          const gradient = ctx.createLinearGradient(0, chartArea.bottom, 0, chartArea.top);
          gradient.addColorStop(0, 'rgba(0, 255, 136, 0.02)');
          gradient.addColorStop(0.5, 'rgba(0, 255, 136, 0.3)');
          gradient.addColorStop(1, 'rgba(0, 255, 136, 0.9)');
          return gradient;
        },
        borderColor: '#00ff88',
        borderWidth: { top: 3, right: 0, bottom: 0, left: 0 },
        borderRadius: 6,
        borderSkipped: 'bottom',
        barPercentage: 0.45,
        hoverBackgroundColor: '#00ff88',
        data: analyticsData.value.chart_data
      }
    ]
  }
})

const chartOptions = {
  responsive: true,
  maintainAspectRatio: false,
  animation: { y: { duration: 1500, easing: 'easeOutQuart' } },
  plugins: {
    legend: { display: false },
    tooltip: {
      backgroundColor: 'rgba(11, 17, 33, 0.95)',
      titleColor: '#94a3b8',
      bodyColor: '#00ff88',
      borderColor: 'rgba(0, 255, 136, 0.3)',
      borderWidth: 1,
      padding: 15,
      displayColors: false,
      titleFont: { size: 13, family: 'sans-serif' },
      bodyFont: { size: 18, weight: '900' },
      cornerRadius: 12,
    }
  },
  scales: {
    y: {
      beginAtZero: true,
      grid: { color: 'rgba(255, 255, 255, 0.03)', drawBorder: false },
      ticks: { stepSize: 1, font: { weight: '600', color: '#64748b' }, padding: 15 },
      border: { display: false }
    },
    x: {
      grid: { display: false },
      ticks: { font: { weight: '700', color: '#94a3b8' }, padding: 10 },
      border: { color: 'rgba(255, 255, 255, 0.1)' }
    }
  }
}

const editOrder = (order) => { editingOrder.value = { ...order } }

// 3. Оновлена функція збереження
const saveOrder = async () => {
  try {
    await axios.patch(`http://127.0.0.1:8000/api/admin-orders/${editingOrder.value.id}/`, {
      full_name: editingOrder.value.full_name,
      phone: editingOrder.value.phone,
      city: editingOrder.value.city,
      nova_poshta: editingOrder.value.nova_poshta,
      status: editingOrder.value.status
    })
    const index = orders.value.findIndex(o => o.id === editingOrder.value.id)
    if (index !== -1) orders.value[index] = { ...editingOrder.value }

    // Закриваємо режим редагування
    editingOrder.value = null

    // ВИКЛИКАЄМО МОДАЛКУ ЗАМІСТЬ ALERT
    modalMessage.value = "Замовлення успішно оновлено! Всі дані збережені в базі."
    isSuccessModalOpen.value = true

  } catch (e) {
    console.error(e)
    modalMessage.value = "Сталася помилка при збереженні даних. Спробуйте ще раз."
    isSuccessModalOpen.value = true
  }
}

const deleteOrder = async (id) => {
  if (!confirm('Ви впевнені, що хочете видалити це замовлення?')) return
  try {
    await axios.delete(`http://127.0.0.1:8000/api/admin-orders/${id}/`)
    orders.value = orders.value.filter(o => o.id !== id)
    editingOrder.value = null
    await fetchAnalytics()

    modalMessage.value = "Замовлення було назавжди видалено з системи."
    isSuccessModalOpen.value = true
  } catch (e) {
    console.error(e)
    alert('❌ Помилка при видаленні')
  }
}

const formatDate = (dateString) => {
  if (!dateString) return 'Невідомо'
  return new Date(dateString).toLocaleDateString('uk-UA', { day: '2-digit', month: '2-digit', year: 'numeric', hour: '2-digit', minute:'2-digit' })
}
</script>

<template>
  <div class="modal-overlay" @click.self="emit('close')">
    <div class="admin-panel dark-theme">
      <button class="close-btn" @click="emit('close')">✕</button>

      <div class="panel-header">
        <h2><span class="neon-icon">👨‍💻</span> Command Center</h2>
        <div class="tabs">
          <button :class="{ active: activeTab === 'analytics' }" @click="activeTab = 'analytics'; editingOrder = null">📊 Аналітика</button>
          <button :class="{ active: activeTab === 'orders' }" @click="activeTab = 'orders'; editingOrder = null">📦 Замовлення</button>
        </div>
      </div>

      <div class="panel-content" v-if="!isLoading">

        <div v-if="activeTab === 'analytics' && analyticsData" class="analytics-tab">
          <div class="analytics-top-cards">
            <div class="stat-card glass-panel gradient-border">
              <div class="stat-icon cyan-glow">💰</div>
              <div class="stat-info">
                <h3>Загальний дохід</h3>
                <p class="revenue text-neon-green">{{ analyticsData.total_revenue }} ₴</p>
              </div>
            </div>
            <div class="stat-card glass-panel">
              <div class="stat-icon purple-glow">📦</div>
              <div class="stat-info">
                <h3>Всього замовлень</h3>
                <p class="revenue text-neon-cyan">{{ orders.length }}</p>
              </div>
            </div>
          </div>

          <div class="chart-card glass-panel">
            <div class="chart-header">
              <h3>📈 Розподіл продажів за категоріями</h3>
              <span class="badge">Live Data</span>
            </div>
            <div class="chart-wrapper">
              <Bar v-if="chartData" :data="chartData" :options="chartOptions" />
              <div v-else class="empty-chart">Немає даних для графіка</div>
            </div>
          </div>
        </div>

        <div v-if="activeTab === 'orders'" class="orders-tab">

          <div v-if="editingOrder" class="edit-mode glass-panel">
            <button class="back-btn" @click="editingOrder = null">← Повернутися</button>

            <div class="edit-grid">
              <div class="edit-section">
                <div class="section-header-flex">
                  <h3 class="section-title-flex">Клієнт</h3>
                </div>
                <div class="form-group"><label>ПІБ</label><input type="text" v-model="editingOrder.full_name" class="dark-input"></div>
                <div class="form-group"><label>Телефон</label><input type="text" v-model="editingOrder.phone" class="dark-input"></div>
                <div class="form-group"><label>Місто</label><input type="text" v-model="editingOrder.city" class="dark-input"></div>
                <div class="form-group"><label>Відділення</label><input type="text" v-model="editingOrder.nova_poshta" class="dark-input"></div>
                <div class="form-group">
                  <label>Статус</label>
                  <select v-model="editingOrder.status" class="dark-input">
                    <option value="Нове">Нове</option>
                    <option value="Відправлено">Відправлено</option>
                    <option value="Виконано">Виконано</option>
                  </select>
                </div>
              </div>

              <div class="edit-section">
                <div class="section-header-flex">
                  <h3 class="section-title-flex">Замовлення #{{ editingOrder.id }}</h3>
                  <span class="badge-date">{{ formatDate(editingOrder.created_at) }}</span>
                </div>

                <div class="items-box dark-box">
                  <div v-if="editingOrder.items && editingOrder.items.length > 0">
                    <div class="item-row" v-for="(item, idx) in editingOrder.items" :key="idx">
                      <span>{{ item.product_name }}</span><strong class="text-neon-cyan">x{{ item.quantity }}</strong>
                    </div>
                  </div>
                  <div v-else class="empty-items">
                    Список товарів порожній 🥺 (старе замовлення без збереженої історії)
                  </div>
                </div>

                <div class="total-row">
                  <span class="total-label">Разом до сплати:</span>
                  <h2 class="edit-total text-neon-green">{{ editingOrder.total_price }} ₴</h2>
                </div>

                <div class="action-buttons">
                  <button class="btn-save" @click="saveOrder">Зберегти зміни</button>
                  <button class="btn-delete" @click="deleteOrder(editingOrder.id)">Видалити</button>
                </div>
              </div>
            </div>
          </div>

          <div v-else class="glass-panel table-wrapper">
            <table class="modern-table clickable-table">
              <thead>
                <tr>
                  <th>ID / Дата</th><th>Доставка</th><th>Товари</th><th>Сума</th><th>Статус</th>
                </tr>
              </thead>
              <tbody>
                <tr v-for="order in orders" :key="order.id" @click="editOrder(order)">
                  <td><strong class="text-white">#{{ order.id }}</strong><br><span class="date">{{ formatDate(order.created_at) }}</span></td>
                  <td><strong class="text-white">{{ order.full_name }}</strong><br><span class="delivery">{{ order.city }}</span></td>
                  <td><ul class="item-list"><li v-for="(item, idx) in order.items" :key="idx">{{ item.product_name }}</li></ul></td>
                  <td class="price text-neon-green">{{ order.total_price }} ₴</td>
                  <td><span :class="['status-badge', `status-${order.status === 'Нове' ? 'new' : order.status === 'Відправлено' ? 'shipped' : 'done'}`]">{{ order.status }}</span></td>
                </tr>
                <tr v-if="orders.length === 0"><td colspan="5" class="empty">Немає замовлень</td></tr>
              </tbody>
            </table>
          </div>
        </div>

      </div>
      <div v-else class="loading text-neon-cyan">Отримання даних... ⏳</div>
    </div>

    <!-- 4. ДОДАЄМО КОМПОНЕНТ МОДАЛКИ В КІНЕЦЬ ТЕМПЛЕЙТУ -->
    <AdminModal
      :show="isSuccessModalOpen"
      title="Повідомлення системи"
      :message="modalMessage"
      @close="isSuccessModalOpen = false"
    />
  </div>
</template>

<style scoped>
/* Стилі залишаються без змін, як у тебе були */
.modal-overlay { position: fixed; top: 0; left: 0; width: 100vw; height: 100vh; background: rgba(5, 8, 15, 0.85); backdrop-filter: blur(12px); display: flex; justify-content: center; align-items: center; z-index: 9999; }
.admin-panel.dark-theme { background: #0b1121; width: 95%; max-width: 1100px; height: 85vh; border-radius: 24px; border: 1px solid rgba(255, 255, 255, 0.05); box-shadow: 0 30px 60px rgba(0, 0, 0, 0.5), inset 0 1px 0 rgba(255, 255, 255, 0.1); position: relative; display: flex; flex-direction: column; overflow: hidden; animation: slideDown 0.4s cubic-bezier(0.16, 1, 0.3, 1); color: #cbd5e1; }
@keyframes slideDown { 0% { opacity: 0; transform: translateY(-40px) scale(0.98); } 100% { opacity: 1; transform: translateY(0) scale(1); } }
.glass-panel { background: rgba(255, 255, 255, 0.02); backdrop-filter: blur(20px); border: 1px solid rgba(255, 255, 255, 0.05); border-radius: 20px; padding: 25px; box-shadow: 0 10px 30px rgba(0, 0, 0, 0.2); }
.panel-header { background: rgba(11, 17, 33, 0.8); padding: 25px 30px; border-bottom: 1px solid rgba(255, 255, 255, 0.05); display: flex; justify-content: space-between; align-items: center; }
.panel-header h2 { margin: 0; font-size: 1.5rem; color: #fff; font-weight: 800; letter-spacing: 0.5px; }
.neon-icon { text-shadow: 0 0 15px rgba(0, 255, 136, 0.5); }
.tabs { display: flex; gap: 10px; }
.tabs button { background: rgba(255, 255, 255, 0.05); border: 1px solid transparent; padding: 10px 20px; border-radius: 12px; font-weight: 700; color: #94a3b8; cursor: pointer; transition: all 0.3s ease; }
.tabs button:hover { background: rgba(255, 255, 255, 0.1); color: #fff; }
.tabs button.active { background: rgba(0, 255, 136, 0.1); color: #00ff88; border-color: rgba(0, 255, 136, 0.3); box-shadow: 0 0 20px rgba(0, 255, 136, 0.1); }
.close-btn { position: absolute; top: 25px; right: 30px; background: rgba(255, 255, 255, 0.05); border: 1px solid rgba(255, 255, 255, 0.1); width: 40px; height: 40px; border-radius: 50%; color: #fff; font-size: 1.2rem; cursor: pointer; transition: 0.3s; z-index: 10; display: flex; align-items: center; justify-content: center; }
.close-btn:hover { background: #ef4444; border-color: #ef4444; box-shadow: 0 0 15px rgba(239, 68, 68, 0.4); }
.panel-content { flex: 1; padding: 30px; overflow-y: auto; }
.analytics-top-cards { display: grid; grid-template-columns: 1fr 1fr; gap: 25px; margin-bottom: 30px; }
.stat-card { display: flex; align-items: center; gap: 20px; position: relative; overflow: hidden; }
.gradient-border::before { content: ''; position: absolute; top: 0; left: 0; width: 100%; height: 2px; background: linear-gradient(90deg, #00ff88, #00ebd3); }
.stat-icon { font-size: 2.5rem; width: 60px; height: 60px; display: flex; justify-content: center; align-items: center; border-radius: 14px; background: rgba(255, 255, 255, 0.05); }
.cyan-glow { box-shadow: inset 0 0 20px rgba(0, 255, 136, 0.1); }
.purple-glow { box-shadow: inset 0 0 20px rgba(168, 85, 247, 0.1); }
.stat-info h3 { margin: 0 0 5px 0; font-size: 0.85rem; color: #94a3b8; font-weight: 700; text-transform: uppercase; letter-spacing: 1px; }
.revenue { font-size: 2.2rem; font-weight: 900; margin: 0; }
.chart-card { padding: 25px; }
.chart-header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 20px; }
.chart-header h3 { margin: 0; color: #fff; font-weight: 800; font-size: 1.1rem; }
.badge { background: rgba(0, 255, 136, 0.1); color: #00ff88; padding: 4px 10px; border-radius: 20px; font-size: 0.75rem; font-weight: 800; border: 1px solid rgba(0, 255, 136, 0.3); }
.chart-wrapper { height: 320px; width: 100%; }
.table-wrapper { padding: 0; overflow: hidden; }
.modern-table { width: 100%; border-collapse: collapse; text-align: left; }
.modern-table th { background: rgba(0, 0, 0, 0.2); color: #94a3b8; padding: 18px 20px; font-size: 0.85rem; font-weight: 700; text-transform: uppercase; letter-spacing: 1px; border-bottom: 1px solid rgba(255, 255, 255, 0.05); }
.modern-table td { padding: 18px 20px; border-bottom: 1px solid rgba(255, 255, 255, 0.03); vertical-align: middle; }
.clickable-table tbody tr { cursor: pointer; transition: 0.2s; }
.clickable-table tbody tr:hover { background: rgba(255, 255, 255, 0.03); }
.date, .delivery { font-size: 0.8rem; color: #64748b; margin-top: 4px; display: block; }
.item-list { margin: 0; padding-left: 15px; font-size: 0.85rem; color: #cbd5e1; }
.price { font-weight: 900; font-size: 1.1rem; }
.status-badge { padding: 6px 12px; border-radius: 8px; font-weight: 800; font-size: 0.75rem; text-transform: uppercase; letter-spacing: 0.5px; }
.status-new { background: rgba(245, 158, 11, 0.1); color: #fbbf24; border: 1px solid rgba(245, 158, 11, 0.2); }
.status-shipped { background: rgba(56, 189, 248, 0.1); color: #38bdf8; border: 1px solid rgba(56, 189, 248, 0.2); }
.status-done { background: rgba(0, 255, 136, 0.1); color: #00ff88; border: 1px solid rgba(0, 255, 136, 0.2); }
.edit-mode { padding: 30px; }
.back-btn { background: none; border: none; font-weight: 700; color: #94a3b8; font-size: 0.9rem; cursor: pointer; margin-bottom: 25px; transition: 0.2s; display: flex; align-items: center; gap: 5px; }
.back-btn:hover { color: #fff; transform: translateX(-5px); }

.edit-grid { display: grid; grid-template-columns: 1fr 1fr; gap: 40px; align-items: start; }
.section-header-flex { display: flex; justify-content: space-between; align-items: center; border-bottom: 1px solid rgba(255,255,255,0.1); padding-bottom: 15px; margin-bottom: 25px; height: 35px; box-sizing: border-box; }
.section-title-flex { margin: 0; padding: 0; border: none; color: #fff; font-weight: 800; font-size: 1.17em; line-height: 1; }
.badge-date { background: rgba(255, 255, 255, 0.05); padding: 6px 12px; border-radius: 8px; color: #94a3b8; font-size: 0.85rem; font-weight: 600; border: 1px solid rgba(255,255,255,0.05); }

.form-group { margin-bottom: 20px; }
.form-group label { display: block; font-size: 0.8rem; font-weight: 700; color: #94a3b8; margin-bottom: 8px; text-transform: uppercase; letter-spacing: 1px; }
.dark-input { width: 100%; padding: 14px; background: rgba(0, 0, 0, 0.2); border: 1px solid rgba(255, 255, 255, 0.1); border-radius: 12px; font-family: inherit; font-size: 1rem; color: #fff; transition: 0.3s; box-sizing: border-box; }
.dark-input:focus { outline: none; border-color: #00ff88; background: rgba(0, 255, 136, 0.05); box-shadow: 0 0 0 3px rgba(0, 255, 136, 0.1); }
.dark-box { background: rgba(0, 0, 0, 0.2); padding: 20px; border-radius: 12px; border: 1px solid rgba(255, 255, 255, 0.05); margin-bottom: 25px; }
.item-row { display: flex; justify-content: space-between; padding: 10px 0; border-bottom: 1px dashed rgba(255, 255, 255, 0.1); }
.item-row:last-child { border-bottom: none; }

.empty-items { text-align: center; color: #64748b; font-size: 0.9rem; padding: 10px 0; font-style: italic; white-space: normal; line-height: 1.5; }

.total-row { display: flex; justify-content: space-between; align-items: center; background: rgba(0, 255, 136, 0.05); border: 1px solid rgba(0, 255, 136, 0.1); padding: 15px 20px; border-radius: 12px; margin-bottom: 25px; }
.total-label { color: #94a3b8; font-weight: 700; text-transform: uppercase; font-size: 0.85rem; letter-spacing: 1px; }
.edit-total { margin: 0; font-weight: 900; font-size: 1.8rem; }
.action-buttons { display: flex; gap: 15px; }
.btn-save { flex: 2; padding: 16px; background: #00ff88; color: #0b1121; border: none; border-radius: 12px; font-weight: 800; cursor: pointer; transition: 0.3s; font-size: 1rem; }
.btn-save:hover { box-shadow: 0 0 20px rgba(0, 255, 136, 0.4); transform: translateY(-2px); }
.btn-delete { flex: 1; padding: 16px; background: rgba(239, 68, 68, 0.1); color: #ef4444; border: 1px solid rgba(239, 68, 68, 0.3); border-radius: 12px; font-weight: 800; cursor: pointer; transition: 0.3s; }
.btn-delete:hover { background: #ef4444; color: white; box-shadow: 0 0 20px rgba(239, 68, 68, 0.4); }
.text-white { color: #fff; }
.text-neon-green { color: #00ff88; text-shadow: 0 0 10px rgba(0, 255, 136, 0.3); }
.text-neon-cyan { color: #00ebd3; text-shadow: 0 0 10px rgba(0, 235, 211, 0.3); }
.loading { text-align: center; padding: 50px; font-weight: 800; font-size: 1.2rem; }
</style>
