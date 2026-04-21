import { ref, computed } from 'vue'
import { defineStore } from 'pinia'

export const useCartStore = defineStore('cart', () => {
  const items = ref([])

  const cartCount = computed(() => {
    return items.value.reduce((total, item) => total + item.quantity, 0)
  })

  // НОВЕ: Рахуємо загальну суму кошика
  const cartTotal = computed(() => {
    return items.value.reduce((total, item) => total + (item.price * item.quantity), 0)
  })

  function addToCart(product) {
    const existingItem = items.value.find(item => item.id === product.id)
    if (existingItem) {
      existingItem.quantity++
    } else {
      items.value.push({ ...product, quantity: 1 })
    }
    alert(`Товар "${product.name}" додано!`)
  }

  // НОВЕ: Очищення кошика після успішної покупки
  function clearCart() {
    items.value = []
  }

  return { items, cartCount, cartTotal, addToCart, clearCart }
})
