from rest_framework import viewsets, generics
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework.permissions import AllowAny
from rest_framework_simplejwt.views import TokenObtainPairView
from django.contrib.auth.models import User
from django.db.models import Sum

from .models import Category, Product, Order, OrderItem
from .serializers import (
    CategorySerializer, 
    ProductSerializer, 
    RegisterSerializer, 
    MyTokenObtainPairSerializer, 
    OrderSerializer
)

# --- АВТОРИЗАЦІЯ ---
class MyTokenObtainPairView(TokenObtainPairView):
    serializer_class = MyTokenObtainPairSerializer

class RegisterView(generics.CreateAPIView):
    queryset = User.objects.all()
    permission_classes = (AllowAny,)
    serializer_class = RegisterSerializer

# --- КАТАЛОГ (Товари та Категорії) ---
class CategoryViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer

class ProductViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer
    filterset_fields = ['category', 'stud_type']

# --- СТВОРЕННЯ ЗАМОВЛЕННЯ З КОШИКА ---
@api_view(['POST'])
def create_order(request):
    try:
        items = request.data.get('items', [])
        total_price = request.data.get('total_price', 0)
        
        full_name = request.data.get('full_name', '')
        phone = request.data.get('phone', '')
        city = request.data.get('city', '')
        nova_poshta = request.data.get('nova_poshta', '')

        # Якщо користувач не авторизований, буде None
        user = request.user if request.user.is_authenticated else None

        order = Order.objects.create(
            user=user, 
            total_price=total_price,
            full_name=full_name,
            phone=phone,
            city=city,
            nova_poshta=nova_poshta
        )

        for item in items:
            product = Product.objects.get(id=item['id'].split('-')[0]) # Відрізаємо розмір, якщо він є в ID
            OrderItem.objects.create(
                order=order, 
                product=product, 
                quantity=item['quantity']
            )
            product.stock -= item['quantity']
            product.save()

        return Response({"message": "Замовлення успішно створено!", "order_id": order.id})
    except Exception as e:
        return Response({"error": str(e)}, status=400)

# --- АДМІН-ПАНЕЛЬ: ЗАМОВЛЕННЯ ---
@api_view(['GET'])
def admin_orders(request):
    if not getattr(request.user, 'is_staff', False):
        return Response({"error": "Доступ заборонено"}, status=403)
    
    orders = Order.objects.all().order_by('-id')
    serializer = OrderSerializer(orders, many=True)
    return Response(serializer.data)

@api_view(['PATCH'])
def update_order_status(request, pk):
    if not getattr(request.user, 'is_staff', False):
        return Response({"error": "Доступ заборонено"}, status=403)
    
    try:
        order = Order.objects.get(pk=pk)
        order.status = request.data.get('status', order.status)
        order.save()
        return Response({"message": "Статус оновлено!"})
    except Order.DoesNotExist:
        return Response({"error": "Замовлення не знайдено"}, status=404)

# --- АДМІН-ПАНЕЛЬ: АНАЛІТИКА ---
@api_view(['GET'])
def analytics_data(request):
    try:
        total_revenue = Order.objects.aggregate(Sum('total_price'))['total_price__sum'] or 0

        category_sales = OrderItem.objects.values('product__category__name') \
            .annotate(total_sold=Sum('quantity')) \
            .order_by('-total_sold')

        labels = [item['product__category__name'] for item in category_sales if item['product__category__name']]
        data = [item['total_sold'] for item in category_sales if item['product__category__name']]

        return Response({
            "total_revenue": total_revenue,
            "chart_labels": labels,  
            "chart_data": data       
        })
    except Exception as e:
        return Response({"error": str(e)}, status=400)
    

# Деталі, редагування та видалення замовлення
@api_view(['GET', 'PATCH', 'DELETE'])
def admin_order_detail(request, pk):
    if not getattr(request.user, 'is_staff', False):
        return Response({"error": "Доступ заборонено"}, status=403)
    
    try:
        order = Order.objects.get(pk=pk)
    except Order.DoesNotExist:
        return Response({"error": "Замовлення не знайдено"}, status=404)

    if request.method == 'GET':
        serializer = OrderSerializer(order)
        return Response(serializer.data)

    elif request.method == 'PATCH':
        # Дозволяємо оновлювати ці поля
        allowed_fields = ['full_name', 'phone', 'city', 'nova_poshta', 'status']
        for field in allowed_fields:
            if field in request.data:
                setattr(order, field, request.data[field])
        order.save()
        return Response({"message": "Замовлення оновлено!"})

    elif request.method == 'DELETE':
        order.delete()
        return Response({"message": "Замовлення успішно видалено!"})