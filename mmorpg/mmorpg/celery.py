import os

from celery import Celery
from celery.schedules import crontab

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'mmorpg.settings')

app = Celery('mmorpg')
app.config_from_object('django.conf:settings', namespace='CELERY')

app.autodiscover_tasks()

app.conf.beat_schedule = {
    'print_every_monday_8_oclock': {
        'task': 'appmmo.tasks.email_every_monday',
        'schedule': crontab(day_of_week="monday", hour=8, minute=0),
    },
}

