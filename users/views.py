from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth import get_user_model
from rest_framework import viewsets, generics, permissions
from rest_framework.permissions import AllowAny, IsAuthenticated
from .serializers import UserSerializer, PaymentSerializer
from rest_framework import viewsets, status
from .models import Payment
from .serializers import PaymentSerializer
from .services import create_stripe_checkout
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import OrderingFilter

User = get_user_model()


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


# CRUD для пользователей
class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer

    def get_permissions(self):
        if self.action == 'create':  # Регистрация
            return [AllowAny()]
        return [IsAuthenticated()]


# Регистрация пользователя
class RegisterView(generics.CreateAPIView):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [AllowAny]

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        return Response(
            UserSerializer(user).data,
            status=status.HTTP_201_CREATED
        )


from rest_framework.response import Response
from rest_framework import status


class PaymentViewSet(viewsets.ModelViewSet):
    queryset = Payment.objects.all()
    serializer_class = PaymentSerializer
    filter_backends = [DjangoFilterBackend, OrderingFilter]
    filterset_fields = ['course', 'lesson', 'payment_method']
    ordering_fields = ['payment_date']
    ordering = ['-payment_date']

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        # Получаем данные для формирования платежа
        course = serializer.validated_data.get('course')
        lesson = serializer.validated_data.get('lesson')
        amount = serializer.validated_data.get('amount')

        # Определяем название и описание (из курса или урока)
        name = course.name if course else (lesson.name if lesson else "Оплата")
        description = course.description if course else (lesson.description if lesson else "Оплата услуг")

        # Формируем абсолютные URL для возврата после оплаты
        success_url = request.build_absolute_uri('/api/users/payments/success/')
        cancel_url = request.build_absolute_uri('/api/users/payments/cancel/')

        try:
            # Вызываем сервис Stripe
            stripe_data = create_stripe_checkout(
                course_name=name,
                course_description=description,
                amount=amount,
                success_url=success_url,
                cancel_url=cancel_url,
            )
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)

        # Сохраняем платеж в нашу БД с данными из Stripe
        payment = serializer.save(
            stripe_product_id=stripe_data['product_id'],
            stripe_price_id=stripe_data['price_id'],
            stripe_session_id=stripe_data['session_id'],
            payment_link=stripe_data['payment_link']
        )

        # Возвращаем пользователю ссылку на оплату
        return Response({
            "message": "Платеж успешно создан",
            "payment_id": payment.id,
            "payment_link": payment.payment_link
        }, status=status.HTTP_201_CREATED)
