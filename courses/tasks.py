from celery import shared_task
from django.core.mail import send_mail
from datetime import timedelta
from django.utils import timezone
from django.contrib.auth import get_user_model
from .models import Course

@shared_task
def send_course_update_email(user_email, course_name):
    send_mail(
        subject=f"Курс '{course_name}' обновлен!",
        message=f"Материалы курса '{course_name}' были обновлены. Проверьте обновленные уроки!",
        from_email='noreply@yourdomain.com',
        recipient_list=[user_email],
    )

@shared_task
def deactivate_inactive_users():
    User = get_user_model()
    one_month_ago = timezone.now() - timedelta(days=30)
    inactive_users = User.objects.filter(last_login__lt=one_month_ago, is_active=True)
    inactive_users.update(is_active=False)