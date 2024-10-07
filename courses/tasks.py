from celery import shared_task
from datetime import datetime, timedelta
from django.utils import timezone
from django.core.mail import send_mail
from django.contrib.auth import get_user_model
from .models import Course

# Задача для отправки писем об обновлении курса
@shared_task
def send_course_update_email(user_email, course_name):
    send_mail(
        subject=f"Курс '{course_name}' обновлен!",
        message=f"Материалы курса '{course_name}' были обновлены. Проверьте обновленные уроки!",
        from_email='noreply@yourdomain.com',
        recipient_list=[user_email],
        fail_silently=False,
    )

# Задача для деактивации неактивных пользователей
@shared_task
def deactivate_inactive_users():
    User = get_user_model()
    one_month_ago = timezone.now() - timedelta(days=30)
    inactive_users = User.objects.filter(last_login__lt=one_month_ago, is_active=True)
    inactive_users.update(is_active=False)