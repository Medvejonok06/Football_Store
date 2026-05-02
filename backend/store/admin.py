from django.contrib import admin
from .models import Category, Product, Order, OrderItem, ProductImage, Size, ProductSize

class ProductImageInline(admin.TabularInline):
    model = ProductImage
    extra = 3 

# Додаємо табличку розмірів всередину сторінки товару
class ProductSizeInline(admin.TabularInline):
    model = ProductSize
    extra = 1

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('id', 'name')
    search_fields = ('name',)

admin.site.register(Size)

@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ('name', 'category', 'price', 'stud_type') # Видалили stock
    list_filter = ('category', 'stud_type')
    search_fields = ('name', 'description')
    inlines = [ProductSizeInline, ProductImageInline] # Вивели таблицю розмірів та галерею
    # Видалили filter_horizontal

class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 0 

@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ('id', 'full_name', 'phone', 'total_price', 'created_at')
    list_filter = ('status', 'created_at')
    inlines = [OrderItemInline]