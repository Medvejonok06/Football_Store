from rest_framework import serializers
from .models import Category, Product, ProductImage, Order, OrderItem, ProductSize
from django.contrib.auth.models import User
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer

# --- НОВИЙ СЕРІАЛІЗАТОР ДЛЯ РОЗМІРІВ ---
class ProductSizeSerializer(serializers.ModelSerializer):
    size_name = serializers.CharField(source='size.name', read_only=True)

    class Meta:
        model = ProductSize
        fields = ['size_name', 'quantity']

class OrderItemSerializer(serializers.ModelSerializer):
    product_name = serializers.ReadOnlyField(source='product.name')
    class Meta:
        model = OrderItem
        fields = ['product_name', 'size', 'quantity'] # Додали size сюди

class OrderSerializer(serializers.ModelSerializer):
    items = serializers.SerializerMethodField()

    class Meta:
        model = Order
        fields = ['id', 'full_name', 'phone', 'city', 'nova_poshta', 'total_price', 'status', 'created_at', 'items']

    def get_items(self, obj):
        if hasattr(obj, 'orderitem_set'):
            items = obj.orderitem_set.all()
        elif hasattr(obj, 'items'):
            items = obj.items.all()
        else:
            return []
        return OrderItemSerializer(items, many=True).data

class MyTokenObtainPairSerializer(TokenObtainPairSerializer):
    @classmethod
    def get_token(cls, user):
        token = super().get_token(user)
        token['is_staff'] = user.is_staff
        return token

    def validate(self, attrs):
        data = super().validate(attrs)
        data['is_staff'] = self.user.is_staff
        data['username'] = self.user.username
        return data

class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, min_length=6)

    class Meta:
        model = User
        fields = ('id', 'username', 'email', 'password')

    def create(self, validated_data):
        user = User.objects.create_user(
            validated_data['username'],
            validated_data.get('email', ''),
            validated_data['password']
        )
        return user

class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ['id', 'name']

class ProductImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductImage
        fields = ['id', 'image']

class ProductSerializer(serializers.ModelSerializer):
    category_name = serializers.ReadOnlyField(source='category.name')
    images = ProductImageSerializer(many=True, read_only=True)
    
    # ВИКОРИСТОВУЄМО ВКАЗАНИЙ СЕРІАЛІЗАТОР (замість SlugRelatedField)
    sizes = ProductSizeSerializer(source='product_sizes', many=True, read_only=True)

    class Meta:
        model = Product
        # Видалили stock
        fields = ['id', 'name', 'category', 'category_name', 'price', 'description', 'stud_type', 'image', 'images', 'sizes']