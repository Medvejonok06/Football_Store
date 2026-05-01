<script setup>
import { ref, computed } from 'vue'

const props = defineProps({
  products: { type: Array, required: true }
})

defineEmits(['close', 'add-to-cart'])

// --- СТАН ОПИТУВАННЯ ---
const step = ref(1)
const filters = ref({
  mainCategory: '',
  shoeType: '',
  brand: ''
})

const topBrands = ['Nike', 'Adidas', 'Puma', 'Jordan', 'Joma']

// Змінна для збереження ЄДИНОГО фінального товару
const recommendedProduct = ref(null)

// --- ЛОГІКА ФІЛЬТРАЦІЇ ---

// Товари, які залишилися ДО вибору бренду
const matchingProducts = computed(() => {
  let res = props.products || []

  if (filters.value.mainCategory === 'Взуття') {
    res = res.filter(p => ['Бутси', 'Футзалки', 'Сороконіжки'].includes(p.category_name))
    if (filters.value.shoeType) {
      res = res.filter(p => p.category_name === filters.value.shoeType)
    }
  } else if (filters.value.mainCategory) {
    res = res.filter(p => p.category_name === filters.value.mainCategory)
  }

  return res
})

// Динамічні бренди: тільки ті, що є в наявності після попередніх кроків
const availableBrands = computed(() => {
  return topBrands.filter(brand =>
    matchingProducts.value.some(p => p.name.toLowerCase().includes(brand.toLowerCase()))
  )
})


// --- НАВІГАЦІЯ ТА ВИБІР ---
const selectMainCategory = (category) => {
  filters.value.mainCategory = category
  if (category === 'Взуття') {
    step.value = 2
  } else {
    step.value = 3
  }
}

const selectShoeType = (type) => {
  filters.value.shoeType = type
  step.value = 3
}

const selectBrand = (brand) => {
  filters.value.brand = brand

  // 1. Беремо копію товарів, що підійшли
  let finalRes = [...matchingProducts.value]

  // 2. Фільтруємо за брендом
  if (brand !== 'any') {
    finalRes = finalRes.filter(p => p.name.toLowerCase().includes(brand.toLowerCase()))
  }

  // 3. ВИБИРАЄМО 1 НАЙКРАЩИЙ ВАРІАНТ (рандомно з тих, що підійшли)
  if (finalRes.length > 0) {
    const randomIndex = Math.floor(Math.random() * finalRes.length)

    // Діагностика в консоль (F12), щоб ти бачив, скільки товарів знайшло
    console.log(`🤖 Алгоритм знайшов моделей: ${finalRes.length}. Випадково обрано індекс: ${randomIndex} (${finalRes[randomIndex].name})`)

    recommendedProduct.value = finalRes[randomIndex]
  } else {
    recommendedProduct.value = null
  }

  step.value = 4
}

const resetSelector = () => {
  filters.value = { mainCategory: '', shoeType: '', brand: '' }
  recommendedProduct.value = null
  step.value = 1
}
</script>

<template>
  <div class="modal-backdrop" @click.self="$emit('close')">
    <div class="modal-glass selector-modal">

      <button class="close-btn" @click="$emit('close')">✕</button>

      <div class="modal-header">
        <span class="bot-icon">🤖</span>
        <h2>Розумний підбір</h2>
        <p v-if="step < 4">Крок {{ step }} з 3</p>
        <p v-else>Алгоритм зробив свій вибір!</p>
      </div>

      <div class="step-container">
        <!-- КРОК 1: ЩО ШУКАЄМО? -->
        <Transition name="slide-fade">
          <div v-if="step === 1" class="step-content">
            <h3>Що саме ти шукаєш?</h3>
            <div class="options-grid">
              <button class="option-card" @click="selectMainCategory('Взуття')">
                <span class="emoji">👟</span>
                <strong>Ігрове взуття</strong>
              </button>
              <button class="option-card" @click="selectMainCategory('Футбольна форма')">
                <span class="emoji">👕</span>
                <strong>Одяг / Форма</strong>
              </button>
              <button class="option-card" @click="selectMainCategory('М\'ячі')">
                <span class="emoji">⚽</span>
                <strong>М'ячі</strong>
              </button>
              <button class="option-card" @click="selectMainCategory('Аксесуари')">
                <span class="emoji">🎒</span>
                <strong>Аксесуари</strong>
              </button>
            </div>
          </div>
        </Transition>

        <!-- КРОК 2: ТИП ПОЛЯ (Тільки для взуття) -->
        <Transition name="slide-fade">
          <div v-if="step === 2" class="step-content">
            <h3>На якому покритті плануєш грати?</h3>

            <!-- СПЕЦІАЛЬНА СІТКА ДЛЯ 3-Х ЕЛЕМЕНТІВ (2 зверху, 1 по центру знизу) -->
            <div class="options-grid-centered">
              <button class="option-card" @click="selectShoeType('Бутси')">
                <span class="emoji">🌱</span>
                <strong>Натуральний газон</strong>
                <span class="sub">Бутси (FG/SG)</span>
              </button>
              <button class="option-card" @click="selectShoeType('Сороконіжки')">
                <span class="emoji">🌿</span>
                <strong>Штучний газон</strong>
                <span class="sub">Сороконіжки (TF)</span>
              </button>
              <button class="option-card" @click="selectShoeType('Футзалки')">
                <span class="emoji">🪵</span>
                <strong>Паркет / Асфальт</strong>
                <span class="sub">Футзалки (IC/IN)</span>
              </button>
            </div>

            <button class="back-link" @click="step = 1">← Назад</button>
          </div>
        </Transition>

        <!-- КРОК 3: БРЕНД -->
        <Transition name="slide-fade">
          <div v-if="step === 3" class="step-content">
            <h3>Чи є улюблений бренд?</h3>

            <div v-if="availableBrands.length === 0" class="no-brands-msg">
              На жаль, за цими критеріями зараз немає товарів 😔
            </div>

            <!-- БРЕНДИ СТОВПЧИКОМ -->
            <div v-else class="brands-column">
              <button
                v-for="brand in availableBrands"
                :key="brand"
                class="brand-btn"
                @click="selectBrand(brand)"
              >
                {{ brand }}
              </button>
              <button class="brand-btn any-btn" @click="selectBrand('any')">
                Не має значення
              </button>
            </div>

            <button class="back-link" @click="filters.mainCategory === 'Взуття' ? step = 2 : step = 1">← Назад</button>
          </div>
        </Transition>

<!-- КРОК 4: РЕЗУЛЬТАТ (ЄДИНА ПРОПОЗИЦІЯ) -->
        <Transition name="slide-fade">
          <div v-if="step === 4" class="step-content results-step">

            <div v-if="!recommendedProduct" class="empty-result">
              <span class="emoji">🕵️‍♂️</span>
              <h3>Нічого не знайдено</h3>
              <p>На жаль, моделі за твоїми критеріями закінчились.</p>
              <button class="reset-btn" @click="resetSelector">Спробувати ще раз</button>
            </div>

            <div v-else class="best-match-container">
              <div class="match-badge">🎯 Ідеальний збіг</div>
              <div class="best-match-card">
                <div class="img-wrapper">
                  <!-- ПЛАШКА АКЦІЇ ДЛЯ БОТА -->
                  <span v-if="recommendedProduct.is_promo" class="promo-tag-bot">-20%</span>

                  <img v-if="recommendedProduct.image" :src="recommendedProduct.image" :alt="recommendedProduct.name" class="main-p-img">
                  <span v-else class="img-placeholder">👟</span>
                </div>

                <div class="p-info">
                  <h4 class="p-name">{{ recommendedProduct.name }}</h4>
                  <p class="p-category">{{ recommendedProduct.category_name }}</p>

                  <!-- ЦІНА ЗІ ЗНИЖКОЮ -->
                  <div class="price-col-bot">
                    <span v-if="recommendedProduct.is_promo" class="old-price-bot">{{ recommendedProduct.original_price }} ₴</span>
                    <span class="p-price" :style="recommendedProduct.is_promo ? 'color: #ef4444' : ''">
                      {{ recommendedProduct.price }} ₴
                    </span>
                  </div>
                </div>

                <button class="add-big-btn" @click="$emit('add-to-cart', recommendedProduct)">
                  Додати до кошика
                </button>
              </div>
            </div>

            <button v-if="recommendedProduct" class="back-link mt-2" @click="resetSelector">↻ Підібрати щось інше</button>
          </div>
        </Transition>
      </div>

    </div>
  </div>
</template>

<style scoped>
.modal-backdrop {
  position: fixed; top: 0; left: 0; width: 100vw; height: 100vh;
  background: rgba(15, 23, 42, 0.6); backdrop-filter: blur(8px);
  display: flex; align-items: center; justify-content: center; z-index: 999999;
}

.selector-modal {
  background: white; border-radius: 32px; padding: 40px;
  width: 90%; max-width: 550px; max-height: 90vh; overflow-y: auto;
  position: relative; box-shadow: 0 30px 60px rgba(0,0,0,0.15);
}

.close-btn {
  position: absolute; top: 20px; right: 20px; background: #f1f5f9;
  border: none; width: 40px; height: 40px; border-radius: 50%;
  font-size: 1.2rem; cursor: pointer; color: #64748b; transition: 0.3s;
}
.close-btn:hover { background: #fee2e2; color: #ef4444; }

.modal-header { text-align: center; margin-bottom: 30px; border-bottom: 2px dashed #e2e8f0; padding-bottom: 20px; }
.bot-icon { font-size: 3rem; display: block; margin-bottom: 10px; }
.modal-header h2 { margin: 0 0 5px 0; color: #0f172a; font-weight: 900; }
.modal-header p { margin: 0; color: #6366f1; font-weight: 800; text-transform: uppercase; font-size: 0.85rem; }

.step-container { position: relative; min-height: 280px; }
.step-content { width: 100%; text-align: center; }
.step-content h3 { margin-bottom: 25px; color: #1e293b; font-weight: 800; font-size: 1.3rem; }

/* СТАНДАРТНА СІТКА НА 2 КОЛОНКИ (Для 4 елементів на Кроці 1) */
.options-grid { display: grid; grid-template-columns: 1fr 1fr; gap: 15px; }

/* СПЕЦІАЛЬНА СІТКА ДЛЯ КРОКУ 2 (3 елементи: 2 зверху, 1 по центру знизу) */
.options-grid-centered {
  display: flex;
  flex-wrap: wrap;
  justify-content: center;
  gap: 15px;
}
.options-grid-centered .option-card {
  width: calc(50% - 7.5px); /* Займає рівно половину, щоб бути як у сітці */
}

.option-card {
  background: #f8fafc; border: 2px solid #e2e8f0; border-radius: 20px;
  padding: 20px 15px; cursor: pointer; transition: all 0.3s ease;
  display: flex; flex-direction: column; align-items: center; gap: 10px;
}
.option-card:hover { border-color: #6366f1; background: white; transform: translateY(-3px); box-shadow: 0 10px 20px rgba(99, 102, 241, 0.1); }
.option-card .emoji { font-size: 2.5rem; }
.option-card strong { font-size: 1.1rem; color: #0f172a; }
.option-card .sub { font-size: 0.85rem; color: #64748b; font-weight: 600; }

/* БРЕНДИ СТОВПЧИКОМ */
.brands-column {
  display: flex;
  flex-direction: column;
  gap: 12px;
  max-width: 280px;
  margin: 0 auto;
}
.brand-btn {
  background: white; border: 2px solid #e2e8f0; padding: 14px 24px;
  border-radius: 14px; font-weight: 800; font-size: 1.05rem; color: #0f172a;
  cursor: pointer; transition: 0.3s; width: 100%;
}
.brand-btn:hover { border-color: #0f172a; background: #0f172a; color: white; transform: translateY(-2px); }
.any-btn { border-color: #6366f1; color: #6366f1; }
.any-btn:hover { background: #6366f1; border-color: #6366f1; color: white; }

.back-link { margin-top: 30px; background: none; border: none; color: #94a3b8; font-weight: 700; cursor: pointer; transition: 0.2s; }
.back-link:hover { color: #0f172a; }

/* СТИЛЬ ДЛЯ ЄДИНОЇ ПРОПОЗИЦІЇ (BEST MATCH) */
.best-match-container {
  position: relative;
  margin: 25px auto 0;
  max-width: 320px;
}
.match-badge {
  position: absolute; top: -15px; left: 50%; transform: translateX(-50%);
  background: #6366f1; color: white; padding: 6px 18px; border-radius: 20px;
  font-weight: 800; font-size: 0.85rem; z-index: 2;
  box-shadow: 0 5px 15px rgba(99, 102, 241, 0.3);
}
.best-match-card {
  background: white; border: 2px solid #e2e8f0; border-radius: 28px;
  padding: 35px 25px 25px; text-align: center; transition: 0.3s;
  box-shadow: 0 10px 30px rgba(0,0,0,0.05);
}
.best-match-card:hover { border-color: #6366f1; transform: translateY(-5px); box-shadow: 0 20px 40px rgba(99, 102, 241, 0.15); }

.img-wrapper { height: 160px; display: flex; align-items: center; justify-content: center; margin-bottom: 20px; }
.main-p-img { max-width: 100%; max-height: 100%; object-fit: contain; }
.img-placeholder { font-size: 4rem; }

.p-name { font-size: 1.3rem; font-weight: 900; color: #0f172a; margin: 0 0 5px 0; line-height: 1.3; }
.p-category { color: #64748b; font-size: 0.95rem; margin: 0 0 15px 0; font-weight: 600; text-transform: uppercase; letter-spacing: 0.5px; }
.p-price { display: block; font-size: 1.8rem; font-weight: 900; color: #0f172a; margin-bottom: 25px; }

.add-big-btn {
  width: 100%; background: #0f172a; color: white; border: none;
  padding: 16px; border-radius: 16px; font-weight: 800; font-size: 1.05rem;
  cursor: pointer; transition: 0.3s; box-shadow: 0 10px 20px rgba(15, 23, 42, 0.15);
}
.add-big-btn:hover { background: #00ff88; color: #0f172a; transform: translateY(-2px); box-shadow: 0 15px 25px rgba(0, 255, 136, 0.3); }

.empty-result .emoji { font-size: 4rem; display: block; margin-bottom: 15px; }
.reset-btn { margin-top: 20px; background: #f1f5f9; color: #0f172a; border: none; padding: 12px 24px; border-radius: 14px; font-weight: 800; cursor: pointer; transition: 0.2s; }
.reset-btn:hover { background: #e2e8f0; }

.mt-2 { margin-top: 15px; }

/* АНІМАЦІЯ ПЕРЕХОДІВ МІЖ КРОКАМИ */
.slide-fade-enter-active, .slide-fade-leave-active { transition: all 0.3s ease; position: absolute; width: 100%; }
.slide-fade-enter-from { opacity: 0; transform: translateX(30px); }
.slide-fade-leave-to { opacity: 0; transform: translateX(-30px); }

.promo-tag-bot { position: absolute; top: 15px; right: 15px; background: #ef4444; color: white; padding: 5px 12px; border-radius: 20px; font-size: 0.85rem; font-weight: 900; z-index: 2; box-shadow: 0 4px 10px rgba(239,68,68,0.3); }
.price-col-bot { display: flex; flex-direction: column; align-items: center; margin-bottom: 25px; }
.old-price-bot { text-decoration: line-through; color: #94a3b8; font-size: 1rem; font-weight: 800; line-height: 1; margin-bottom: 5px; }
</style>
