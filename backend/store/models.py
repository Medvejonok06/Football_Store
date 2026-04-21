from django.db import models
from django.contrib.auth.models import User

class Category(models.Model):
    name = models.CharField(max_length=100, verbose_name="Назва категорії")

    class Meta:
        verbose_name = "Категорія"
        verbose_name_plural = "Категорії"

    def __str__(self):
        return self.name

class Product(models.Model):
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name='products', verbose_name="Категорія")
    name = models.CharField(max_length=255, verbose_name="Назва товару")
    price = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Ціна")
    description = models.TextField(blank=True, null=True, verbose_name="Опис")
    stud_type = models.CharField(max_length=50, blank=True, null=True, verbose_name="Тип шипів (FG, TF, IC)")
    stock = models.IntegerField(default=0, verbose_name="Кількість на складі")
    image = models.ImageField(upload_to='products/', blank=True, null=True)

    def __str__(self):
        return self.name

class Order(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
    # НОВІ ПОЛЯ ДЛЯ ДОСТАВКИ:
    full_name = models.CharField(max_length=200, verbose_name="ПІБ", null=True)
    phone = models.CharField(max_length=20, verbose_name="Телефон", null=True)
    city = models.CharField(max_length=100, verbose_name="Місто", null=True)
    nova_poshta = models.CharField(max_length=100, verbose_name="Відділення НП", null=True)
    
    status = models.CharField(max_length=20, default='New')
    total_price = models.DecimalField(max_digits=10, decimal_places=2)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Замовлення {self.id} - {self.full_name}"

class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='items')
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.IntegerField(default=1, verbose_name="Кількість")

    def __str__(self):
        return f"{self.quantity} x {self.product.name}"
    
class ProductImage(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='images')
    image = models.ImageField(upload_to='products/gallery/')

    def __str__(self):
        return f"Фото для {self.product.name}"