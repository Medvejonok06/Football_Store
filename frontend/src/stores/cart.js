import { ref, computed } from 'vue'
import { defineStore } from 'pinia'

export const useCartStore = defineStore('cart', () => {
  const items = ref([])

  // --- БАЗОВІ ОБЧИСЛЕННЯ ---

  // Загальна кількість товарів у кошику
  const cartCount = computed(() => {
    return items.value.reduce((total, item) => total + (item.quantity || 1), 0)
  })

  // Загальна сума кошика (всі товари)
  const cartTotal = computed(() => {
    return items.value.reduce((total, item) => total + (item.price * (item.quantity || 1)), 0)
  })

  // --- ЛОГІКА БЕЗКОШТОВНОЇ ДОСТАВКИ (NEW) ---

  // Сума товарів БЕЗ акції (знижки -20%)
  const nonPromoTotal = computed(() => {
    return items.value
      .filter(item => !item.is_promo)
      .reduce((total, item) => total + (item.price * (item.quantity || 1)), 0)
  })

  // Чи активована безкоштовна доставка (поріг 5000 грн)
  const isFreeDelivery = computed(() => {
    return nonPromoTotal.value >= 5000
  })

  // Скільки ще залишилося добрати неакційних товарів
  const amountToFreeDelivery = computed(() => {
    const remaining = 5000 - nonPromoTotal.value
    return remaining > 0 ? remaining : 0
  })

  // Відсоток прогресу для смужки (Progress Bar)
  const deliveryProgress = computed(() => {
    const progress = (nonPromoTotal.value / 5000) * 100
    return progress > 100 ? 100 : progress
  })

  // --- МЕТОДИ ---

  // Додавання в кошик
  function addToCart(product) {
    const existingItem = items.value.find(item => item.id === product.id)
    if (existingItem) {
      existingItem.quantity++
    } else {
      // Зберігаємо всі поля, включаючи is_promo та selectedSize
      items.value.push({ ...product, quantity: 1 })
    }
  }

  // Видалення з кошика
  function removeFromCart(productId) {
    items.value = items.value.filter(item => item.id !== productId)
  }

  // Очищення всього кошика
  function clearCart() {
    items.value = []
  }

  return {
    items,
    cartCount,
    cartTotal,
    nonPromoTotal,
    isFreeDelivery,
    amountToFreeDelivery,
    deliveryProgress,
    addToCart,
    removeFromCart,
    clearCart
  }
})
