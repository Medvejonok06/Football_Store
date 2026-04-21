from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import CategoryViewSet, ProductViewSet, create_order, analytics_data
from rest_framework_simplejwt.views import TokenRefreshView
from .views import RegisterView, MyTokenObtainPairView 
from .views import admin_orders
from .views import CategoryViewSet, ProductViewSet, create_order, analytics_data, admin_orders, admin_order_detail

router = DefaultRouter()
router.register(r'categories', CategoryViewSet)
router.register(r'products', ProductViewSet)

urlpatterns = [
    path('', include(router.urls)),
    path('checkout/', create_order),
    path('analytics/', analytics_data), 
    path('register/', RegisterView.as_view(), name='auth_register'),
    path('login/', MyTokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('admin-orders/', admin_orders),
    path('admin-orders/<int:pk>/', admin_order_detail),
]