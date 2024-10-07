from celery import Celery
import os
from django.conf import settings
from celery.schedules import crontab

# Создание экземпляра Celery
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'myproject.settings')
app = Celery('myproject')
app.config_from_object('django.conf:settings', namespace='CELERY')
app.autodiscover_tasks(lambda: settings.INSTALLED_APPS)

# Настройки расписания celery-beat
app.conf.beat_schedule = {
    'deactivate_inactive_users': {
        'task': 'courses.tasks.deactivate_inactive_users',
        'schedule': crontab(hour=0, minute=0),  # Выполняется ежедневно в полночь
    },
}

if __name__ == '__main__':
    app.start()