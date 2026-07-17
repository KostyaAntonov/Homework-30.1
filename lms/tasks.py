from celery import shared_task
from django.core.mail import send_mail
from django.conf import settings
from django.utils import timezone
from datetime import timedelta
from .models import Course, Subscription
from users.models import User


@shared_task
def send_course_update_emails(course_id):
    """
    Задание 2: Отправка писем подписчикам об обновлении курса.
    Проверяет, что курс обновлен менее 4 часов назад (защита от дублей).
    """
    try:
        course = Course.objects.get(id=course_id)

        # Проверка: отправляем только если обновление было менее 4 часов назад
        if (timezone.now() - course.updated_at) < timedelta(hours=4):
            # Выбираем только активных пользователей, чтобы не слать письма заблокированным
            subscriptions = Subscription.objects.filter(
                course_id=course_id,
                user__is_active=True
            ).select_related('user')

            emails = [sub.user.email for sub in subscriptions]

            if emails:
                send_mail(
                    subject=f'Обновление курса: {course.name}',
                    message=f'Здравствуйте!\n\nКурс "{course.name}" был обновлен. Заходите и изучайте новые материалы!',
                    from_email=settings.DEFAULT_FROM_EMAIL,
                    recipient_list=emails,
                    fail_silently=False,
                )
                return f"Успешно отправлено {len(emails)} писем."
        return "Курс обновлен более 4 часов назад или нет подписчиков."

    except Course.DoesNotExist:
        return "Курс не найден."


@shared_task
def deactivate_inactive_users():
    """
    Задание 3: Периодическая задача. Блокирует пользователей,
    которые не заходили более 1 месяца.
    Обновление происходит батчем (одним SQL-запросом), а не в цикле.
    """
    one_month_ago = timezone.now() - timedelta(days=30)

    # Фильтруем неактивных (по логину) и активных (по флагу) пользователей
    # и обновляем их одним запросом (batch update)
    deactivated_count = User.objects.filter(
        last_login__lt=one_month_ago,
        is_active=True
    ).update(is_active=False)

    return f"Заблокировано {deactivated_count} неактивных пользователей."