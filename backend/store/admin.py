from django.contrib import admin
from .models import Category, Product, Order, OrderItem, ProductImage

class ProductImageInline(admin.TabularInline):
    model = ProductImage
    extra = 3 # Скільки порожніх полів для фото показувати за замовчування

# Реєструємо категорію
@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('id', 'name')
    search_fields = ('name',)

# Реєструємо товари (наші бутси/м'ячі)
@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ('name', 'category', 'price', 'stock', 'stud_type') # Які колонки показувати
    list_filter = ('category', 'stud_type') # Зручні фільтри збоку
    search_fields = ('name', 'description') # Пошук по назві
    inlines = [ProductImageInline] # Додаємо галерею

# Робимо так, щоб товари всередині замовлення показувалися зручною табличкою
class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 0 # Не показувати зайві порожні рядки

# Реєструємо самі замовлення
@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ('id', 'full_name', 'phone', 'total_price', 'created_at')
    list_filter = ('status', 'created_at')
    inlines = [OrderItemInline] # Додаємо табличку товарів всередину замовлення

