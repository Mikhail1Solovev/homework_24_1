import logging
from celery import shared_task
from datetime import datetime, timedelta
from django.utils import timezone
from django.core.mail import send_mail
from django.contrib.auth import get_user_model
from .models import Course

logger = logging.getLogger(__name__)

# Задача для отправки писем об обновлении курса
@shared_task(bind=True)
def send_course_update_email(self, user_email, course_name):
    try:
        send_mail(
            subject=f"Курс '{course_name}' обновлен!",
            message=f"Материалы курса '{course_name}' были обновлены. Проверьте обновленные уроки!",
            from_email='noreply@yourdomain.com',
            recipient_list=[user_email],
            fail_silently=False,
        )
        logger.info(f"Уведомление об обновлении курса '{course_name}' отправлено на {user_email}")
    except Exception as e:
        logger.error(f"Ошибка при отправке письма на {user_email}: {e}")
        self.retry(exc=e, countdown=60, max_retries=3)

# Задача для деактивации неактивных пользователей
@shared_task
def deactivate_inactive_users():
    User = get_user_model()
    one_month_ago = timezone.now() - timedelta(days=30)
    inactive_users = User.objects.filter(last_login__lt=one_month_ago, is_active=True)
    inactive_users.update(is_active=False)
    logger.info(f"Деактивированы {inactive_users.count()} неактивных пользователей")