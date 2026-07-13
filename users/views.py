from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import User, Payment
from rest_framework import viewsets
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import OrderingFilter
from .serializers import PaymentSerializer


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    list_display = ('email', 'phone', 'city', 'is_staff')
    fieldsets = (
        (None, {'fields': ('email', 'password')}),
        ('Личная информация', {'fields': ('phone', 'city', 'avatar')}),
        ('Права', {'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions')}),
    )
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email', 'password1', 'password2'),
        }),
    )
    search_fields = ('email',)
    ordering = ('email',)


@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    list_display = ('user', 'amount', 'payment_method', 'payment_date', 'course', 'lesson')
    list_filter = ('payment_method', 'payment_date')


class PaymentViewSet(viewsets.ModelViewSet):
    queryset = Payment.objects.all()
    serializer_class = PaymentSerializer

    # Подключаем бэкенды фильтрации и сортировки
    filter_backends = [DjangoFilterBackend, OrderingFilter]

    # Поля, по которым можно фильтровать
    filterset_fields = ['course', 'lesson', 'payment_method']

    # Поля, по которым можно сортировать
    ordering_fields = ['payment_date']

    # Сортировка по умолчанию (сначала новые)
    ordering = ['-payment_date']
