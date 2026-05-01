import { ref, computed } from 'vue'
import { defineStore } from 'pinia'

export const useCartStore = defineStore('cart', () => {
  const items = ref([])

  // Рахуємо загальну кількість товарів
  const cartCount = computed(() => {
    return items.value.reduce((total, item) => total + (item.quantity || 1), 0)
  })

  // Рахуємо загальну суму кошика
  const cartTotal = computed(() => {
    return items.value.reduce((total, item) => total + (item.price * (item.quantity || 1)), 0)
  })

  // Додавання в кошик
  function addToCart(product) {
    const existingItem = items.value.find(item => item.id === product.id)
    if (existingItem) {
      existingItem.quantity++
    } else {
      items.value.push({ ...product, quantity: 1 })
    }
  }

  // ВИДАЛЕННЯ З КОШИКА
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
    addToCart,
    removeFromCart,
    clearCart
  }
})
