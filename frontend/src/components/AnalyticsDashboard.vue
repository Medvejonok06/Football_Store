<script setup>
import { ref, onMounted } from 'vue'

const emit = defineEmits(['close'])

// Статистика (можеш підставити сюди дані з бекенду, зараз тут красиві демо-дані)
const stats = ref({
  totalRevenue: 16696,
  totalOrders: 12,
  averageCheck: 1391
})

// Дані для графіка з різними кольорами
const chartData = ref([
  { label: 'Бутси (FG)', value: 8500, color: 'linear-gradient(135deg, #6366f1, #a855f7)' },
  { label: 'Футзалки', value: 4200, color: 'linear-gradient(135deg, #00ff88, #0ea5e9)' },
  { label: 'М\'ячі', value: 2100, color: 'linear-gradient(135deg, #f59e0b, #ef4444)' },
  { label: 'Форма', value: 1500, color: 'linear-gradient(135deg, #ec4899, #8b5cf6)' },
  { label: 'Гетри', value: 396, color: 'linear-gradient(135deg, #14b8a6, #3b82f6)' }
])

// Рахуємо максимум для висоти стовпців
const maxValue = Math.max(...chartData.value.map(d => d.value))
</script>

<template>
  <div class="modal-overlay" @click.self="emit('close')">
    <div class="dashboard-panel">
      <div class="dash-header">
        <div class="title-group">
          <span class="icon">📈</span>
          <h2>Панель аналітики</h2>
        </div>
        <button class="close-btn" @click="emit('close')">✕</button>
      </div>

      <div class="kpi-grid">
        <div class="kpi-card">
          <div class="kpi-icon revenue-icon">💰</div>
          <div>
            <p class="kpi-label">Загальний дохід</p>
            <p class="kpi-value">{{ stats.totalRevenue }} ₴</p>
          </div>
        </div>
        <div class="kpi-card">
          <div class="kpi-icon orders-icon">📦</div>
          <div>
            <p class="kpi-label">Кількість замовлень</p>
            <p class="kpi-value">{{ stats.totalOrders }}</p>
          </div>
        </div>
        <div class="kpi-card">
          <div class="kpi-icon avg-icon">📊</div>
          <div>
            <p class="kpi-label">Середній чек</p>
            <p class="kpi-value">{{ stats.averageCheck }} ₴</p>
          </div>
        </div>
      </div>

      <div class="chart-section">
        <h3>Дохід за категоріями</h3>
        <div class="bar-chart">
          <div
            v-for="(item, index) in chartData"
            :key="index"
            class="bar-wrapper"
          >
            <span class="bar-value">{{ item.value }} ₴</span>
            <div class="bar-track">
              <div
                class="bar-fill"
                :style="{
                  height: `${(item.value / maxValue) * 100}%`,
                  background: item.color
                }"
              ></div>
            </div>
            <span class="bar-label">{{ item.label }}</span>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<style scoped>
.modal-overlay {
  position: fixed; top: 0; left: 0; width: 100vw; height: 100vh;
  background: rgba(15, 23, 42, 0.6); backdrop-filter: blur(8px);
  display: flex; justify-content: center; align-items: center; z-index: 9999;
}

.dashboard-panel {
  background: #ffffff; width: 90%; max-width: 900px;
  border-radius: 32px; padding: 40px; box-shadow: 0 25px 50px rgba(0,0,0,0.15);
  animation: slideUp 0.4s cubic-bezier(0.175, 0.885, 0.32, 1.275);
}

@keyframes slideUp {
  from { opacity: 0; transform: translateY(40px) scale(0.95); }
  to { opacity: 1; transform: translateY(0) scale(1); }
}

.dash-header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 30px; }
.title-group { display: flex; align-items: center; gap: 15px; }
.title-group .icon { font-size: 2.5rem; }
.title-group h2 { margin: 0; font-size: 1.8rem; font-weight: 900; color: #0f172a; }

.close-btn {
  background: #f1f5f9; border: none; width: 45px; height: 45px;
  border-radius: 50%; font-size: 1.2rem; cursor: pointer; transition: 0.2s; color: #64748b;
}
.close-btn:hover { background: #ef4444; color: white; transform: rotate(90deg); }

/* KPI CARDS */
.kpi-grid { display: grid; grid-template-columns: repeat(3, 1fr); gap: 20px; margin-bottom: 40px; }
.kpi-card { background: #f8fafc; padding: 25px; border-radius: 24px; display: flex; align-items: center; gap: 20px; border: 1px solid #e2e8f0; transition: 0.3s; }
.kpi-card:hover { transform: translateY(-5px); box-shadow: 0 10px 20px rgba(0,0,0,0.05); }

.kpi-icon { width: 60px; height: 60px; border-radius: 18px; display: flex; justify-content: center; align-items: center; font-size: 1.8rem; }
.revenue-icon { background: #dcfce7; color: #16a34a; }
.orders-icon { background: #e0e7ff; color: #4f46e5; }
.avg-icon { background: #fef3c7; color: #d97706; }

.kpi-label { margin: 0 0 5px 0; font-size: 0.9rem; color: #64748b; font-weight: 700; text-transform: uppercase; }
.kpi-value { margin: 0; font-size: 1.8rem; font-weight: 900; color: #0f172a; }

/* CHART SECTION */
.chart-section { background: #0f172a; padding: 30px; border-radius: 24px; color: white; }
.chart-section h3 { margin: 0 0 30px 0; font-size: 1.3rem; font-weight: 800; }

.bar-chart { display: flex; justify-content: space-around; align-items: flex-end; height: 250px; padding-bottom: 20px; border-bottom: 2px solid rgba(255,255,255,0.1); }
.bar-wrapper { display: flex; flex-direction: column; align-items: center; gap: 10px; flex: 1; height: 100%; justify-content: flex-end; }
.bar-track { width: 40px; height: 100%; background: rgba(255,255,255,0.05); border-radius: 10px; display: flex; align-items: flex-end; position: relative; overflow: hidden; }

.bar-fill {
  width: 100%; border-radius: 10px;
  animation: growUp 1s cubic-bezier(0.175, 0.885, 0.32, 1.275);
  box-shadow: 0 0 20px rgba(255,255,255,0.1);
}

@keyframes growUp { from { height: 0; } }

.bar-value { font-size: 0.85rem; font-weight: 800; color: #94a3b8; }
.bar-label { font-size: 0.8rem; font-weight: 700; color: white; text-align: center; margin-top: 10px; }
</style>
