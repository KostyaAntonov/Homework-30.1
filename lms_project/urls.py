from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/lms/', include('lms.urls')),  # Эндпоинты курсов и уроков
    path('api/users/', include('users.urls')),  # Эндпоинты платежей
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
