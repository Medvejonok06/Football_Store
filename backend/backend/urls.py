from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/', include('store.urls')), # або 'api.urls', залежить від назви твого додатка
]

# ДОДАЄМО ДОЗВІЛ НА ПОКАЗ КАРТИНОК
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)