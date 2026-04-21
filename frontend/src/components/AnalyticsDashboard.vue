<script setup>
import { ref, onMounted } from 'vue'
import axios from 'axios'
import { useAuthStore } from '../stores/auth'

const emit = defineEmits(['close'])
const authStore = useAuthStore()

const activeTab = ref('orders')
const orders = ref([])
const analyticsData = ref(null)
const isLoading = ref(true)

// Стан для редагування
const editingOrder = ref(null)

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

// Вмикаємо режим редагування (робимо копію об'єкта)
const editOrder = (order) => {
  editingOrder.value = { ...order }
}

// Зберігаємо зміни
const saveOrder = async () => {
  try {
    await axios.patch(`http://127.0.0.1:8000/api/admin-orders/${editingOrder.value.id}/`, {
      full_name: editingOrder.value.full_name,
      phone: editingOrder.value.phone,
      city: editingOrder.value.city,
      nova_poshta: editingOrder.value.nova_poshta,
      status: editingOrder.value.status
    })

    // Оновлюємо локальний список
    const index = orders.value.findIndex(o => o.id === editingOrder.value.id)
    if (index !== -1) orders.value[index] = { ...editingOrder.value }

    editingOrder.value = null // Виходимо з режиму редагування
    alert('✅ Замовлення успішно оновлено!')
  } catch (e) {
    console.error(e)
    alert('❌ Помилка при збереженні')
  }
}

// Видаляємо замовлення
const deleteOrder = async (id) => {
  if (!confirm('Ви впевнені, що хочете видалити це замовлення? Цю дію неможливо скасувати!')) return

  try {
    await axios.delete(`http://127.0.0.1:8000/api/admin-orders/${id}/`)
    orders.value = orders.value.filter(o => o.id !== id)
    editingOrder.value = null
    alert('🗑️ Замовлення видалено')
  } catch (e) {
    console.error(e)
    alert('❌ Помилка при видаленні')
  }
}

const formatDate = (dateString) => {
  if (!dateString) return 'Невідомо'
  const date = new Date(dateString)
  return date.toLocaleDateString('uk-UA', { day: '2-digit', month: '2-digit', year: 'numeric', hour: '2-digit', minute:'2-digit' })
}
</script>

<template>
  <div class="modal-overlay" @click.self="emit('close')">
    <div class="admin-panel">
      <button class="close-btn" @click="emit('close')">✕</button>

      <div class="panel-header">
        <h2>👨‍💻 Панель Управління</h2>
        <div class="tabs">
          <button :class="{ active: activeTab === 'orders' }" @click="activeTab = 'orders'; editingOrder = null">📦 Замовлення</button>
          <button :class="{ active: activeTab === 'analytics' }" @click="activeTab = 'analytics'; editingOrder = null">📊 Аналітика</button>
        </div>
      </div>

      <div class="panel-content" v-if="!isLoading">

        <div v-if="activeTab === 'orders'" class="orders-tab">

          <div v-if="editingOrder" class="edit-mode">
            <button class="back-btn" @click="editingOrder = null">← Назад до списку</button>
            <div class="edit-grid">

              <div class="edit-section">
                <h3>Інформація про клієнта</h3>
                <div class="form-group">
                  <label>ПІБ Клієнта</label>
                  <input type="text" v-model="editingOrder.full_name">
                </div>
                <div class="form-group">
                  <label>Телефон</label>
                  <input type="text" v-model="editingOrder.phone">
                </div>
                <div class="form-group">
                  <label>Місто</label>
                  <input type="text" v-model="editingOrder.city">
                </div>
                <div class="form-group">
                  <label>Відділення НП</label>
                  <input type="text" v-model="editingOrder.nova_poshta">
                </div>
                <div class="form-group">
                  <label>Статус замовлення</label>
                  <select v-model="editingOrder.status" class="status-select">
                    <option value="Нове">Нове</option>
                    <option value="Відправлено">Відправлено</option>
                    <option value="Виконано">Виконано</option>
                  </select>
                </div>
              </div>

              <div class="edit-section">
                <h3>Деталі замовлення #{{ editingOrder.id }}</h3>
                <p class="edit-date">Створено: {{ formatDate(editingOrder.created_at) }}</p>
                <div class="items-box">
                  <div class="item-row" v-for="(item, idx) in editingOrder.items" :key="idx">
                    <span>⚽ {{ item.product_name }}</span>
                    <strong>x{{ item.quantity }}</strong>
                  </div>
                </div>
                <h2 class="edit-total">Сума: {{ editingOrder.total_price }} ₴</h2>

                <div class="action-buttons">
                  <button class="btn-save" @click="saveOrder">💾 Зберегти зміни</button>
                  <button class="btn-delete" @click="deleteOrder(editingOrder.id)">🗑️ Видалити</button>
                </div>
              </div>

            </div>
          </div>

          <table v-else class="modern-table clickable-table">
            <thead>
              <tr>
                <th>ID / Дата</th>
                <th>Клієнт / Доставка</th>
                <th>Товари</th>
                <th>Сума</th>
                <th>Статус</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="order in orders" :key="order.id" @click="editOrder(order)">
                <td>
                  <strong>#{{ order.id }}</strong><br>
                  <span class="date">{{ formatDate(order.created_at) }}</span>
                </td>
                <td>
                  <strong>{{ order.full_name }}</strong> ({{ order.phone }})<br>
                  <span class="delivery">{{ order.city }}, {{ order.nova_poshta }}</span>
                </td>
                <td>
                  <ul class="item-list">
                    <li v-for="(item, idx) in order.items" :key="idx">
                      {{ item.product_name }} <span class="qty">x{{ item.quantity }}</span>
                    </li>
                  </ul>
                </td>
                <td class="price">{{ order.total_price }} ₴</td>
                <td>
                  <span :class="['status-badge', `status-${order.status === 'Нове' ? 'new' : order.status === 'Відправлено' ? 'shipped' : 'done'}`]">
                    {{ order.status }}
                  </span>
                </td>
              </tr>
              <tr v-if="orders.length === 0">
                <td colspan="5" class="empty">Поки немає жодного замовлення 🥺</td>
              </tr>
            </tbody>
          </table>
        </div>

        <div v-if="activeTab === 'analytics' && analyticsData" class="analytics-tab">
          <div class="stat-card">
            <h3>Загальний дохід</h3>
            <p class="revenue">{{ analyticsData.total_revenue }} ₴</p>
          </div>
        </div>

      </div>
      <div v-else class="loading">Завантаження даних бази... ⏳</div>
    </div>
  </div>
</template>

<style scoped>
.modal-overlay { position: fixed; top: 0; left: 0; width: 100vw; height: 100vh; background: rgba(15, 23, 42, 0.7); backdrop-filter: blur(10px); display: flex; justify-content: center; align-items: center; z-index: 9999; }
.admin-panel { background: #f8fafc; width: 95%; max-width: 1100px; height: 85vh; border-radius: 24px; box-shadow: 0 25px 50px rgba(0,0,0,0.2); position: relative; display: flex; flex-direction: column; overflow: hidden; animation: slideDown 0.3s ease-out; }
@keyframes slideDown { 0% { opacity: 0; transform: translateY(-30px); } 100% { opacity: 1; transform: translateY(0); } }
.close-btn { position: absolute; top: 20px; right: 20px; background: white; border: 1px solid #e2e8f0; width: 40px; height: 40px; border-radius: 50%; font-size: 1.2rem; cursor: pointer; transition: 0.2s; z-index: 10; }
.close-btn:hover { background: #ef4444; color: white; border-color: #ef4444; }

.panel-header { background: white; padding: 25px 30px; border-bottom: 1px solid #e2e8f0; }
.panel-header h2 { margin: 0 0 20px 0; font-size: 1.8rem; color: #0f172a; font-weight: 900; }
.tabs { display: flex; gap: 15px; }
.tabs button { background: #f1f5f9; border: none; padding: 12px 24px; border-radius: 12px; font-weight: 700; color: #64748b; cursor: pointer; transition: 0.2s; }
.tabs button:hover { background: #e2e8f0; }
.tabs button.active { background: #0f172a; color: white; }

.panel-content { flex: 1; padding: 30px; overflow-y: auto; }

/* ТАБЛИЦЯ */
.modern-table { width: 100%; border-collapse: collapse; background: white; border-radius: 16px; overflow: hidden; box-shadow: 0 10px 20px rgba(0,0,0,0.02); }
.clickable-table tbody tr { cursor: pointer; transition: 0.2s; }
.clickable-table tbody tr:hover { background: #f8fafc; transform: scale(1.005); box-shadow: 0 4px 10px rgba(0,0,0,0.05); }
.modern-table th { background: #0f172a; color: white; padding: 15px; text-align: left; font-size: 0.9rem; font-weight: 700; }
.modern-table td { padding: 15px; border-bottom: 1px solid #f1f5f9; vertical-align: top; color: #334155; }
.date { font-size: 0.8rem; color: #94a3b8; }
.delivery { font-size: 0.85rem; color: #64748b; }
.item-list { margin: 0; padding-left: 15px; font-size: 0.9rem; }
.qty { font-weight: 800; color: #6366f1; }
.price { font-weight: 900; font-size: 1.1rem; color: #10b981; }
.empty { text-align: center; padding: 40px !important; color: #94a3b8; font-weight: 600; }

.status-badge { padding: 6px 12px; border-radius: 8px; font-weight: 700; font-size: 0.85rem; display: inline-block; }
.status-new { background: #fef3c7; color: #d97706; }
.status-shipped { background: #e0e7ff; color: #4f46e5; }
.status-done { background: #d1fae5; color: #059669; }

/* РЕЖИМ РЕДАГУВАННЯ */
.back-btn { background: none; border: none; font-weight: 800; color: #6366f1; font-size: 1rem; cursor: pointer; margin-bottom: 20px; transition: 0.2s; }
.back-btn:hover { transform: translateX(-5px); color: #4f46e5; }
.edit-grid { display: grid; grid-template-columns: 1fr 1fr; gap: 30px; }
.edit-section { background: white; padding: 25px; border-radius: 16px; box-shadow: 0 10px 20px rgba(0,0,0,0.02); border: 1px solid #f1f5f9; }
.edit-section h3 { margin-top: 0; color: #0f172a; font-weight: 800; border-bottom: 2px solid #f1f5f9; padding-bottom: 10px; margin-bottom: 20px; }

.form-group { margin-bottom: 15px; }
.form-group label { display: block; font-size: 0.85rem; font-weight: 700; color: #64748b; margin-bottom: 5px; }
.form-group input, .form-group select { width: 100%; padding: 12px; border: 2px solid #e2e8f0; border-radius: 10px; font-family: inherit; font-size: 1rem; color: #0f172a; transition: 0.2s; box-sizing: border-box; }
.form-group input:focus, .form-group select:focus { outline: none; border-color: #6366f1; background: #f8fafc; }

.edit-date { color: #64748b; font-size: 0.9rem; margin-bottom: 15px; }
.items-box { background: #f8fafc; padding: 15px; border-radius: 12px; margin-bottom: 20px; }
.item-row { display: flex; justify-content: space-between; padding: 8px 0; border-bottom: 1px dashed #cbd5e1; color: #334155; }
.item-row:last-child { border-bottom: none; }
.edit-total { color: #10b981; font-weight: 900; margin-bottom: 30px; font-size: 1.8rem; }

.action-buttons { display: flex; gap: 15px; }
.btn-save { flex: 2; padding: 15px; background: #0f172a; color: white; border: none; border-radius: 12px; font-weight: 800; cursor: pointer; transition: 0.2s; }
.btn-save:hover { background: #10b981; }
.btn-delete { flex: 1; padding: 15px; background: #fee2e2; color: #ef4444; border: none; border-radius: 12px; font-weight: 800; cursor: pointer; transition: 0.2s; }
.btn-delete:hover { background: #ef4444; color: white; }

.loading { text-align: center; padding: 50px; font-weight: 700; color: #64748b; }
.stat-card { background: white; padding: 30px; border-radius: 16px; display: inline-block; box-shadow: 0 10px 20px rgba(0,0,0,0.02); }
.revenue { font-size: 2.5rem; font-weight: 900; color: #10b981; margin: 10px 0 0 0; }
</style>
