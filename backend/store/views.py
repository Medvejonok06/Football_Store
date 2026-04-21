from rest_framework import viewsets
from rest_framework.decorators import api_view
from rest_framework.response import Response
from django.contrib.auth.models import User
from .models import Category, Product, Order, OrderItem
from .serializers import CategorySerializer, ProductSerializer
from django.db.models import Sum
from rest_framework import generics
from rest_framework.permissions import AllowAny
from .serializers import RegisterSerializer


class RegisterView(generics.CreateAPIView):
    queryset = User.objects.all()
    permission_classes = (AllowAny,)
    serializer_class = RegisterSerializer
    
# Видаємо список всіх категорій
class CategoryViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer

# Видаємо список всіх товарів
class ProductViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer
    filterset_fields = ['category', 'stud_type']

# НОВА ФУНКЦІЯ: Приймаємо замовлення з кошика
@api_view(['POST'])
def create_order(request):
    try:
        items = request.data.get('items', [])
        total_price = request.data.get('total_price', 0)
        
        # Забираємо дані доставки з фронтенду
        full_name = request.data.get('full_name', '')
        phone = request.data.get('phone', '')
        city = request.data.get('city', '')
        nova_poshta = request.data.get('nova_poshta', '')

        user = User.objects.first()

        # Зберігаємо всі дані в замовлення
        order = Order.objects.create(
            user=user, 
            total_price=total_price,
            full_name=full_name,
            phone=phone,
            city=city,
            nova_poshta=nova_poshta
        )

        for item in items:
            product = Product.objects.get(id=item['id'])
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
    
    # НОВА ФУНКЦІЯ: Збираємо аналітику для дашборду
@api_view(['GET'])
def analytics_data(request):
    try:
        # 1. Рахуємо загальний дохід з усіх замовлень
        total_revenue = Order.objects.aggregate(Sum('total_price'))['total_price__sum'] or 0

        # 2. Рахуємо, скільки товарів кожної категорії продано
        # Беремо всі продані товари, групуємо по назві категорії і рахуємо їх кількість
        category_sales = OrderItem.objects.values('product__category__name') \
            .annotate(total_sold=Sum('quantity')) \
            .order_by('-total_sold')

        # Форматуємо дані так, щоб їх легко зрозумів наш графік на фронтенді
        labels = [item['product__category__name'] for item in category_sales]
        data = [item['total_sold'] for item in category_sales]

        return Response({
            "total_revenue": total_revenue,
            "chart_labels": labels,  # Назви категорій (наприклад: ["Бутси", "М'ячі"])
            "chart_data": data       # Кількість проданих (наприклад: [5, 2])
        })
    except Exception as e:
        return Response({"error": str(e)}, status=400)