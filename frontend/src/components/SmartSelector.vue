<script setup>
import { ref } from 'vue'

const props = defineProps({
  products: { type: Array, required: true }
})
const emit = defineEmits(['close', 'add-to-cart'])

const step = ref(1)
const answers = ref({
  type: null,
  detail: null,
  brand: null // Додали нове поле для бренду
})

const isAnalyzing = ref(false)
const recommendedProduct = ref(null)

// Крок 1: Вибір категорії
const selectType = (type) => {
  answers.value.type = type
  step.value = 2
}

// Крок 2: Вибір покриття / призначення
const selectDetail = (detail) => {
  answers.value.detail = detail
  step.value = 3 // Тепер ідемо на 3-й крок (Бренд)
}

// Крок 3: Вибір бренду
const selectBrand = (brand) => {
  answers.value.brand = brand
  step.value = 4 // Запускаємо аналіз
  isAnalyzing.value = true

  setTimeout(() => {
    analyzeAndRecommend()
    isAnalyzing.value = false
    step.value = 5 // Показуємо результат
  }, 1500)
}

// УДОСКОНАЛЕНИЙ АЛГОРИТМ ПІДБОРУ
const analyzeAndRecommend = () => {
  let filtered = [...props.products]

  // 1. Фільтруємо за головною категорією та деталями
  if (answers.value.type === 'shoes') {
    filtered = filtered.filter(p =>
      p.category_name?.toLowerCase().includes('взуття') ||
      p.category_name?.toLowerCase().includes('бутс') ||
      p.category_name?.toLowerCase().includes('футзалк')
    )

    // Уточнення покриття
    if (answers.value.detail === 'IN') {
      filtered = filtered.filter(p => p.stud_type?.includes('IN') || p.name.toLowerCase().includes('sala') || p.name.toLowerCase().includes('gato') || p.category_name?.toLowerCase().includes('футзалк'))
    } else if (answers.value.detail === 'FG') {
      filtered = filtered.filter(p => p.stud_type?.includes('FG') || p.name.toLowerCase().includes('elite') || p.category_name?.toLowerCase().includes('бутс'))
    } else if (answers.value.detail === 'TF') {
      filtered = filtered.filter(p => p.stud_type?.includes('TF') || p.name.toLowerCase().includes('сороконіж'))
    }
  }
  else if (answers.value.type === 'ball') {
    filtered = filtered.filter(p => p.category_name?.toLowerCase().includes('м\'яч') || p.category_name?.toLowerCase().includes('мяч'))
  }
  else if (answers.value.type === 'accessories') {
    filtered = filtered.filter(p => p.category_name?.toLowerCase().includes('гетри') || p.category_name?.toLowerCase().includes('форм'))
  }

  // 2. Фільтруємо за БРЕНДОМ (якщо обрано конкретний)
  if (answers.value.brand !== 'any') {
    const brandFiltered = filtered.filter(p => p.name.toLowerCase().includes(answers.value.brand.toLowerCase()))

    // РОЗУМНА ПЕРЕВІРКА: Якщо такого бренду для цього покриття немає,
    // ми не видаємо пустий екран, а залишаємо попередній список (інші бренди для цього покриття)
    if (brandFiltered.length > 0) {
      filtered = brandFiltered
    }
  }

  // 3. З того, що залишилося, обираємо найкраще (наприклад, сортуємо за ціною як показником преміальності)
  if (filtered.length > 0) {
    recommendedProduct.value = filtered.sort((a, b) => b.price - a.price)[0]
  } else {
    // Бекап-варіант, якщо взагалі нічого не підійшло
    recommendedProduct.value = props.products[0]
  }
}
</script>

<template>
  <div class="modal-overlay" @click.self="emit('close')">
    <div class="ai-panel">

      <button class="close-btn" @click="emit('close')">✕</button>

      <div class="ai-header">
        <div class="ai-avatar">👋</div>
        <h2>Твій футбольний гід</h2>
        <p v-if="step < 4">Дай відповідь на пару питань, і я допоможу з вибором.</p>
      </div>

      <div v-if="step === 1" class="question-block">
        <h3>Що саме ти шукаєш сьогодні?</h3>
        <div class="options-grid">
          <button @click="selectType('shoes')">👟 Ігрове взуття</button>
          <button @click="selectType('ball')">⚽ Футбольний м'яч</button>
          <button @click="selectType('accessories')">🧦 Форма та аксесуари</button>
        </div>
      </div>

      <div v-if="step === 2 && answers.type === 'shoes'" class="question-block">
        <h3>На якому покритті ти граєш найчастіше?</h3>
        <div class="options-grid">
          <button @click="selectDetail('FG')">🌱 Натуральний газон (Бутси FG)</button>
          <button @click="selectDetail('TF')">🟢 Штучне поле (Сороконіжки TF)</button>
          <button @click="selectDetail('IN')">🏟️ Паркет / Зал (Футзалки IN)</button>
        </div>
      </div>

      <div v-if="step === 2 && answers.type === 'ball'" class="question-block">
        <h3>Для кого підбираємо м'яч?</h3>
        <div class="options-grid">
          <button @click="selectDetail('size5')">👨 Дорослі (Розмір 5, Професійний)</button>
          <button @click="selectDetail('size4')">👦 Діти / Юнаки (Розмір 3-4, Легкий)</button>
        </div>
      </div>

      <div v-if="step === 2 && answers.type === 'accessories'" class="question-block">
        <h3>Що саме тебе цікавить?</h3>
        <div class="options-grid">
          <button @click="selectDetail('socks')">🧦 Ігрові гетри</button>
          <button @click="selectDetail('kit')">👕 Футбольна форма</button>
        </div>
      </div>

      <div v-if="step === 3" class="question-block">
        <h3>Чи є у тебе улюблений бренд?</h3>
        <div class="options-grid brand-options">
          <button @click="selectBrand('Nike')">✔️ Nike</button>
          <button @click="selectBrand('Adidas')">✔️ Adidas</button>
          <button @click="selectBrand('Puma')">✔️ Puma</button>
          <button @click="selectBrand('Joma')">✔️ Joma</button>
          <button @click="selectBrand('any')" class="neutral-btn">🤷 Не має значення</button>
        </div>
      </div>

      <div v-if="step === 4" class="analyzing-block">
        <div class="radar-spinner"></div>
        <h3>Переглядаю каталог...</h3>
        <p>Підбираю ідеальний варіант за твоїми критеріями</p>
      </div>

      <div v-if="step === 5" class="result-block">
        <h3>🎯 Знайшов чудовий варіант:</h3>

        <div v-if="recommendedProduct" class="rec-card">
          <div class="rec-img">
            <img v-if="recommendedProduct.image" :src="recommendedProduct.image" :alt="recommendedProduct.name">
            <span v-else>⭐</span>
          </div>
          <div class="rec-info">
            <h4>{{ recommendedProduct.name }}</h4>
            <p class="rec-price">{{ recommendedProduct.price }} ₴</p>
            <button class="add-btn" @click="emit('add-to-cart', recommendedProduct); emit('close')">
              Беру! Додати в кошик
            </button>
          </div>
        </div>

        <button class="restart-btn" @click="step = 1">Почати спочатку</button>
      </div>

    </div>
  </div>
</template>

<style scoped>
.modal-overlay {
  position: fixed; top: 0; left: 0; width: 100vw; height: 100vh;
  background: rgba(15, 23, 42, 0.7); backdrop-filter: blur(10px);
  display: flex; justify-content: center; align-items: center; z-index: 9999;
}

.ai-panel {
  background: white; width: 90%; max-width: 600px;
  border-radius: 32px; padding: 40px; box-shadow: 0 25px 50px rgba(0,0,0,0.2);
  position: relative; animation: popIn 0.4s cubic-bezier(0.175, 0.885, 0.32, 1.275);
}

@keyframes popIn {
  0% { opacity: 0; transform: scale(0.9); }
  100% { opacity: 1; transform: scale(1); }
}

.close-btn {
  position: absolute; top: 20px; right: 20px; background: #f1f5f9;
  border: none; width: 40px; height: 40px; border-radius: 50%;
  font-size: 1.2rem; cursor: pointer; transition: 0.2s; color: #64748b;
}
.close-btn:hover { background: #ef4444; color: white; transform: rotate(90deg); }

.ai-header { text-align: center; margin-bottom: 30px; }
.ai-avatar { font-size: 4rem; display: inline-block; animation: float 3s ease-in-out infinite; filter: drop-shadow(0 10px 15px rgba(99, 102, 241, 0.15)); }

@keyframes float {
  0%, 100% { transform: translateY(0); }
  50% { transform: translateY(-10px); }
}

.ai-header h2 { margin: 10px 0 5px 0; font-size: 1.8rem; font-weight: 900; color: #0f172a; }
.ai-header p { color: #64748b; margin: 0; }

.question-block h3 { text-align: center; font-size: 1.3rem; margin-bottom: 20px; color: #1e293b; }

.options-grid { display: flex; flex-direction: column; gap: 15px; }
.options-grid button {
  background: white; border: 2px solid #e2e8f0; padding: 18px 25px;
  border-radius: 20px; font-size: 1.1rem; font-weight: 700; color: #334155;
  cursor: pointer; transition: 0.3s; text-align: left;
}
.options-grid button:hover { border-color: #6366f1; background: #e0e7ff; color: #4f46e5; transform: translateX(10px); }

/* Спеціальний стиль для сітки брендів */
.brand-options { display: grid; grid-template-columns: 1fr 1fr; gap: 10px; }
.brand-options button { padding: 15px; text-align: center; }
.brand-options .neutral-btn { grid-column: 1 / -1; background: #f8fafc; border-style: dashed; }
.brand-options .neutral-btn:hover { background: #f1f5f9; border-color: #94a3b8; color: #475569; transform: none; }

/* АНАЛІЗУВАННЯ */
.analyzing-block { text-align: center; padding: 40px 0; }
.radar-spinner {
  width: 80px; height: 80px; border: 4px solid #e0e7ff; border-top-color: #6366f1;
  border-radius: 50%; margin: 0 auto 20px; animation: spin 1s linear infinite;
}
@keyframes spin { to { transform: rotate(360deg); } }

/* РЕЗУЛЬТАТ */
.result-block h3 { text-align: center; color: #10b981; font-size: 1.5rem; margin-bottom: 25px; }
.rec-card { background: #f8fafc; border: 2px solid #e2e8f0; border-radius: 24px; padding: 20px; display: flex; gap: 20px; align-items: center; margin-bottom: 20px; }
.rec-img { width: 120px; height: 120px; background: white; border-radius: 16px; display: flex; align-items: center; justify-content: center; font-size: 3rem; overflow: hidden; box-shadow: 0 10px 20px rgba(0,0,0,0.05); }
.rec-img img { width: 100%; height: 100%; object-fit: contain; padding: 10px; }
.rec-info h4 { margin: 0 0 10px 0; font-size: 1.2rem; font-weight: 800; color: #0f172a; }
.rec-price { font-size: 1.5rem; font-weight: 900; color: #6366f1; margin: 0 0 15px 0; }

.add-btn { background: #0f172a; color: white; border: none; padding: 12px 20px; border-radius: 14px; font-weight: 800; cursor: pointer; transition: 0.2s; width: 100%; }
.add-btn:hover { background: #00ff88; color: #0f172a; }

.restart-btn { width: 100%; background: transparent; border: none; color: #94a3b8; font-weight: 700; cursor: pointer; padding: 10px; }
.restart-btn:hover { color: #64748b; text-decoration: underline; }
</style>
