import os
import django
import random

# Налаштовуємо Django для роботи скрипта поза сервером
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings')
django.setup()

from store.models import Product, Size, ProductSize

def run_seeder():
    print("🧹 Очищаємо старі залишки розмірів...")
    ProductSize.objects.all().delete()
    
    print("📏 Створюємо або отримуємо всі необхідні розмірні сітки...")
    
    # 1. Взуття (36-47)
    shoe_sizes = [Size.objects.get_or_create(name=str(i))[0] for i in range(36, 48)]
    
    # 2. Одяг та аксесуари (S-XXL)
    clothes_sizes = [Size.objects.get_or_create(name=size)[0] for size in ['S', 'M', 'L', 'XL', 'XXL']]
    
    # 3. Шкарпетки/Носки (діапазони)
    sock_sizes = [Size.objects.get_or_create(name=size)[0] for size in ['36-39', '39-42', '42-45', '45-47']]
    
    # 4. М'ячі (Тільки 5)
    ball_size = [Size.objects.get_or_create(name='5')[0]]

    products = Product.objects.all()
    
    print("\n📦 Починаємо розподіл залишків...")
    for product in products:
        cat_name = product.category.name.lower()
        prod_name = product.name.lower() # Тепер дивимось і на назву товару!
        
        # ВИЗНАЧАЄМО КАТЕГОРІЮ (шукаємо ключові слова і в категорії, і в НАЗВІ)
        if any(word in cat_name for word in ['м\'яч', 'мяч']) or any(word in prod_name for word in ['м\'яч', 'мяч']):
            applicable_sizes = ball_size
            
        elif any(word in cat_name for word in ['носк', 'шкарпетк']) or any(word in prod_name for word in ['носк', 'шкарпетк']):
            applicable_sizes = sock_sizes
            
        elif any(word in cat_name for word in ['бутси', 'сороконіжки', 'футзалки', 'взуття']) or any(word in prod_name for word in ['бутси', 'сороконіжки', 'футзалки']):
            applicable_sizes = shoe_sizes
            
        # Якщо нічого з вищепереліченого, вважаємо це одягом/формою
        else:
            applicable_sizes = clothes_sizes
            
        # Генеруємо загальну кількість для товару (від 0 до 100)
        total_quantity = random.randint(0, 100)
        
        # Створюємо словник, де кожному розміру спочатку даємо 0 штук
        distribution = {size: 0 for size in applicable_sizes}
        
        # Розкидаємо загальну кількість по одному випадковому розміру, поки не закінчаться
        for _ in range(total_quantity):
            random_size = random.choice(applicable_sizes)
            distribution[random_size] += 1
            
        # ВАЖЛИВО: Тепер ми зберігаємо ВСІ розміри сітки, навіть якщо кількість = 0! 
        # Це потрібно, щоб фронтенд міг показати їх закресленими (якщо розкупили).
        for size, qty in distribution.items():
            ProductSize.objects.create(
                product=product,
                size=size,
                quantity=qty
            )
            
        print(f"✅ {product.name} | Сітка: {applicable_sizes[0].name}... | Загалом: {total_quantity} шт.")

    print("\n🎉 Готово! Всі товари отримали правильні розміри та випадкові залишки.")

if __name__ == '__main__':
    run_seeder()