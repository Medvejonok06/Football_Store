<script setup>
import { useRouter } from 'vue-router'
const router = useRouter()
</script>

<template>
  <div class="about-page">
    <div class="about-container">
      <section class="hero-section">
        <h1 class="hero-title">Більше ніж просто <span>магазин</span></h1>
        <p class="hero-subtitle">
          Ми поєднуємо пристрасть до футболу з інноваційними технологіями, щоб кожен гравець міг знайти свою ідеальну модель.
        </p>
      </section>

      <div class="about-grid">
        <!-- 1. НАША ІСТОРІЯ -->
        <div class="glass-card history-block">
          <div class="card-header">
            <span class="icon-glow">🏆</span>
            <h2>Наша історія</h2>
          </div>
          <div class="rich-text">
            <p>
              Наша подорож розпочалася у 2024 році в самому серці **Чернівців**. FootballPRO виник не просто як бізнес, а як відповідь на реальну проблему: складність пошуку професійного екіпірування, яке б ідеально відповідало індивідуальним особливостям гравця.
            </p>
            <p>
              Ми починали як невелика команда ентузіастів, які проводили години на футбольних полях, аналізуючи потреби спортсменів. Сьогодні ми — прогресивна платформа, що використовує алгоритми штучного інтелекту для аналізу вашого стилю гри.
            </p>
          </div>
          <div class="history-stats">
            <div class="stat-item">
              <strong>2+</strong>
              <span>Роки на ринку</span>
            </div>
            <div class="stat-item">
              <strong>1000+</strong>
              <span>Задоволених гравців</span>
            </div>
          </div>
        </div>

        <!-- 2. ЗВ'ЯЗОК З НАМИ -->
        <div class="glass-card contacts-block">
          <h3 class="section-title">Зв'язок з нами</h3>
          <div class="contact-mini-list">
            <div class="mini-item clickable-border">
              <span class="m-icon">📞</span>
              <div class="m-content">
                <label>Телефон</label>
                <strong>+380 (99) 123-45-67</strong>
              </div>
            </div>
            <div class="mini-item clickable-border">
              <span class="m-icon">📧</span>
              <div class="m-content">
                <label>Email</label>
                <strong>support@footballpro.ua</strong>
              </div>
            </div>
            <div class="mini-item clickable-border">
              <span class="m-icon">📍</span>
              <div class="m-content">
                <label>Адреса</label>
                <strong>м. Чернівці, вул. Університетська, 28</strong>
              </div>
            </div>
          </div>
        </div>

        <!-- 3. ГРАФІК РОБОТИ -->
        <div class="glass-card schedule-block">
          <div class="card-header">
            <span class="icon-glow">🕒</span>
            <h3>Графік роботи</h3>
          </div>
          <ul class="schedule-rows">
            <li><span>Понеділок - П'ятниця</span> <strong>09:00 - 20:00</strong></li>
            <li><span>Субота</span> <strong>10:00 - 18:00</strong></li>
            <li class="off-day"><span>Неділя</span> <strong>Вихідний</strong></li>
          </ul>
          <p class="schedule-note">Онлайн-замовлення приймаються цілодобово 24/7</p>
        </div>

        <!-- 4. ЧОМУ МИ? -->
        <div class="glass-card why-us-block">
          <h3 class="section-title">Чому ми?</h3>
          <div class="rich-text">
            <p>
              Ми віримо, що правильне взуття — це 50% успіху на полі. Саме тому ми розробили систему **Smart Match**, яка допомагає підібрати модель не за картинкою, а за вашими фізичними параметрами.
            </p>
            <p>
              Обираючи FootballPRO, ви отримуєте гарантію оригінальності кожної одиниці товару. Наша мета — дати кожному гравцю відчуття професіонала.
            </p>
          </div>
          <div class="tech-tags">
            <span class="t-badge">Smart Match AI</span>
            <span class="t-badge">Original Gear</span>
            <span class="t-badge">Fast Delivery</span>
          </div>
        </div>
      </div>

      <div class="actions">
        <button class="back-btn" @click="router.push('/')">Повернутись до покупок</button>
      </div>
    </div>
  </div>
</template>

<style scoped>
.about-page { width: 100%; min-height: 100vh; display: flex; justify-content: center; }
.about-container { width: 100%; max-width: 1300px; padding: 60px 20px; color: #e2e8f0; position: relative; z-index: 5; }
.hero-section { text-align: center; margin-bottom: 70px; }
.hero-title { font-size: clamp(2.5rem, 5vw, 3.8rem); font-weight: 900; margin-bottom: 20px; letter-spacing: -2px; }
.hero-title span { color: #6366f1; text-shadow: 0 0 30px rgba(99, 102, 241, 0.4); }
.hero-subtitle { color: #94a3b8; font-size: 1.25rem; max-width: 700px; margin: 0 auto; line-height: 1.6; }

.about-grid { display: grid; grid-template-columns: repeat(2, 1fr); gap: 30px; width: 100%; }
.glass-card { background: rgba(17, 24, 39, 0.9); backdrop-filter: blur(20px); border: 1px solid rgba(255, 255, 255, 0.12); border-radius: 32px; padding: 40px; display: flex; flex-direction: column; box-shadow: 0 20px 50px rgba(0, 0, 0, 0.4); }
.glass-card:hover { border-color: #00ff88; transform: translateY(-5px); transition: 0.3s; }

.rich-text p { margin-bottom: 20px; line-height: 1.7; color: #cbd5e1; font-size: 1rem; }
.history-stats { display: flex; gap: 40px; margin-top: auto; padding-top: 30px; border-top: 1px solid rgba(255, 255, 255, 0.1); }
.stat-item strong { display: block; font-size: 2rem; color: #00ff88; font-weight: 900; }
.stat-item span { font-size: 0.8rem; color: #64748b; text-transform: uppercase; font-weight: 800; }

.mini-item { display: flex; align-items: center; gap: 15px; padding: 15px; background: rgba(0,0,0,0.3); border-radius: 20px; border: 1px solid rgba(255, 255, 255, 0.08); transition: 0.2s; margin-bottom: 10px; }
.mini-item:hover { border-color: #6366f1; background: rgba(99, 102, 241, 0.05); }

.schedule-rows { list-style: none; padding: 0; margin-bottom: 20px; }
.schedule-rows li { display: flex; justify-content: space-between; padding: 15px 0; border-bottom: 1px dashed rgba(255, 255, 255, 0.1); }
.off-day strong { color: #ef4444; }

.tech-tags { display: flex; gap: 12px; margin-top: auto; flex-wrap: wrap; }
.t-badge { padding: 8px 16px; background: rgba(99, 102, 241, 0.1); border: 1px solid rgba(99, 102, 241, 0.3); border-radius: 12px; color: #6366f1; font-size: 0.8rem; font-weight: 800; text-transform: uppercase; }

.back-btn { background: #fff; color: #000; border: none; padding: 18px 45px; border-radius: 20px; font-weight: 900; cursor: pointer; transition: 0.3s; }
.back-btn:hover { background: #00ff88; box-shadow: 0 0 25px rgba(0, 255, 136, 0.5); }

@media (max-width: 1024px) { .about-grid { grid-template-columns: 1fr; } }
</style>
