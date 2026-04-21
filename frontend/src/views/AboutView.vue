<script setup>
import { useRouter } from 'vue-router'
const router = useRouter()
</script>

<template>
  <div class="about-page">
    <section class="about-hero">
      <h1>Більше ніж просто <span>магазин</span></h1>
      <p>Ми створюємо майбутнє футбольного екіпірування, поєднуючи професійний спорт та інтелектуальні технології.</p>
    </section>

    <div class="about-grid">
      <div class="about-card story">
        <div class="icon">🏆</div>
        <h3>Наша історія</h3>
        <p>Заснований у 2024 році в Чернівцях, FootballPRO пройшов шлях від маленького стартапу до провідної платформи для футболістів. Ми розуміємо, що кожен гравець унікальний, тому впровадили AI-підбір взуття.</p>
      </div>

      <div class="about-card contacts">
        <h3>Зв'язок з нами</h3>
        <div class="contact-item">
          <span class="c-icon">📞</span>
          <div>
            <p class="label">Телефон</p>
            <p class="value">+380 (99) 123-45-67</p>
          </div>
        </div>
        <div class="contact-item">
          <span class="c-icon">📧</span>
          <div>
            <p class="label">Email</p>
            <p class="value">support@footballpro.ua</p>
          </div>
        </div>
        <div class="contact-item">
          <span class="c-icon">📍</span>
          <div>
            <p class="label">Локація</p>
            <p class="value">м. Чернівці, вул. Університетська, 28</p>
          </div>
        </div>
      </div>

      <div class="about-card schedule">
        <div class="icon">🕒</div>
        <h3>Графік роботи</h3>
        <ul class="schedule-list">
          <li><span>Пн - Пт:</span> <span>09:00 - 20:00</span></li>
          <li><span>Сб:</span> <span>10:00 - 18:00</span></li>
          <li><span>Нд:</span> <span class="closed">Вихідний</span></li>
        </ul>
      </div>

      <div class="about-card values">
        <h3>Чому ми?</h3>
        <div class="values-flex">
          <div class="v-tag">Якість</div>
          <div class="v-tag">Швидкість</div>
          <div class="v-tag">Технологічність</div>
          <div class="v-tag">Довіра</div>
        </div>
      </div>
    </div>

    <div class="back-home">
      <button @click="router.push('/')" class="btn-back">Повернутись до покупок</button>
    </div>
  </div>
</template>

<style scoped>
.about-page { max-width: 1200px; margin: 0 auto; padding-bottom: 60px; }

.about-hero { text-align: center; padding: 60px 0; max-width: 800px; margin: 0 auto; }
.about-hero h1 { font-size: 3.5rem; font-weight: 900; color: #0f172a; margin-bottom: 20px; }
.about-hero h1 span { color: #6366f1; }
.about-hero p { font-size: 1.25rem; color: #64748b; line-height: 1.6; }

/* BENTO GRID */
.about-grid {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  grid-template-rows: auto auto;
  gap: 25px;
}

.about-card {
  background: white;
  padding: 35px;
  border-radius: 32px;
  border: 1px solid rgba(255,255,255,0.3);
  box-shadow: 0 10px 30px rgba(0,0,0,0.04);
  transition: 0.3s;
}
.about-card:hover { transform: translateY(-5px); box-shadow: 0 20px 40px rgba(0,0,0,0.08); }

.about-card h3 { font-size: 1.5rem; font-weight: 800; margin-bottom: 20px; color: #0f172a; }

.story { grid-column: span 2; background: #0f172a; color: white; }
.story h3 { color: #00ff88; }
.story p { line-height: 1.7; opacity: 0.9; font-size: 1.1rem; }
.icon { font-size: 3rem; margin-bottom: 15px; }

.contacts { grid-row: span 2; }
.contact-item { display: flex; gap: 15px; margin-bottom: 25px; align-items: center; }
.c-icon { font-size: 1.5rem; background: #f1f5f9; padding: 12px; border-radius: 14px; }
.label { font-size: 0.8rem; color: #94a3b8; font-weight: 700; text-transform: uppercase; margin: 0; }
.value { font-size: 1rem; font-weight: 700; color: #0f172a; margin: 0; }

.schedule-list { list-style: none; padding: 0; margin: 0; }
.schedule-list li { display: flex; justify-content: space-between; padding: 10px 0; border-bottom: 1px solid #f1f5f9; font-weight: 600; }
.closed { color: #ef4444; }

.values { background: linear-gradient(135deg, #6366f1, #a855f7); color: white; }
.values h3 { color: white; }
.values-flex { display: flex; flex-wrap: wrap; gap: 10px; }
.v-tag { background: rgba(255,255,255,0.2); padding: 8px 15px; border-radius: 100px; font-weight: 700; font-size: 0.9rem; border: 1px solid rgba(255,255,255,0.3); }

.back-home { text-align: center; margin-top: 60px; }
.btn-back { background: #0f172a; color: white; border: none; padding: 16px 35px; border-radius: 18px; font-weight: 800; cursor: pointer; transition: 0.3s; }
.btn-back:hover { background: #1e293b; transform: scale(1.05); }

@media (max-width: 900px) {
  .about-grid { grid-template-columns: 1fr; }
  .story { grid-column: span 1; }
}
</style>
