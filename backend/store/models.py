from django.db import models
from django.contrib.auth.models import User

class Category(models.Model):
    name = models.CharField(max_length=100, verbose_name="Назва категорії")

    class Meta:
        verbose_name = "Категорія"
        verbose_name_plural = "Категорії"

    def __str__(self):
        return self.name

class Size(models.Model):
    name = models.CharField(max_length=20, unique=True, verbose_name="Розмір (напр. 42, M, 39-42)")

    class Meta:
        verbose_name = "Розмір"
        verbose_name_plural = "Розміри"

    def __str__(self):
        return self.name

class Product(models.Model):
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name='products', verbose_name="Категорія")
    name = models.CharField(max_length=255, verbose_name="Назва товару")
    price = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Ціна")
    description = models.TextField(blank=True, null=True, verbose_name="Опис")
    stud_type = models.CharField(max_length=50, blank=True, null=True, verbose_name="Тип шипів (FG, TF, IC)")
    image = models.ImageField(upload_to='products/', blank=True, null=True)
    
    # МИ ВИДАЛИЛИ stock ТА sizes ЗВІДСИ!

    def __str__(self):
        return self.name

# НОВА ТАБЛИЦЯ: Прив'язує розмір до товару + кількість
class ProductSize(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='product_sizes')
    size = models.ForeignKey(Size, on_delete=models.CASCADE)
    quantity = models.IntegerField(default=0, verbose_name="Кількість на складі")

    class Meta:
        verbose_name = "Розмір та кількість"
        verbose_name_plural = "Розміри та кількості"
        unique_together = ('product', 'size') # Щоб випадково не додати два однакових розміри одному товару

    def __str__(self):
        return f"{self.product.name} - Розмір {self.size.name} ({self.quantity} шт.)"

class ProductImage(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='images')
    image = models.ImageField(upload_to='products/gallery/')

    def __str__(self):
        return f"Фото для {self.product.name}"

class Order(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
    full_name = models.CharField(max_length=200, verbose_name="ПІБ", null=True)
    phone = models.CharField(max_length=20, verbose_name="Телефон", null=True)
    city = models.CharField(max_length=100, verbose_name="Місто", null=True)
    nova_poshta = models.CharField(max_length=100, verbose_name="Відділення НП", null=True)
    
    status = models.CharField(max_length=20, default='New')
    total_price = models.DecimalField(max_digits=10, decimal_places=2)
    created_at = models.DateTimeField(auto_now_add=True, null=True)

    def __str__(self):
        return f"Замовлення {self.id} - {self.full_name}"

class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='items')
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    # ДОДАЛИ РОЗМІР, щоб адмін бачив, який розмір треба відправити:
    size = models.CharField(max_length=20, null=True, blank=True, verbose_name="Розмір")
    quantity = models.IntegerField(default=1, verbose_name="Кількість")

    def __str__(self):
        size_str = f" ({self.size})" if self.size else ""
        return f"{self.quantity} x {self.product.name}{size_str}"