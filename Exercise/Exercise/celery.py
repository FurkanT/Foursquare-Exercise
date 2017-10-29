from __future__ import absolute_import, unicode_literals
import os
from celery import Celery
from celery.schedules import crontab


os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'Exercise.settings')
app = Celery('Exercise')
app.config_from_object('django.conf:settings', namespace='CELERY')
app.autodiscover_tasks()

app.conf.beat_schedule = {
    'mail-to-non-visitor-users': {
        'task': 'foursquare.tasks.mail_to_non_visitor_users',
        'schedule': crontab(),  # change to `crontab(minute=0, hour=0)` if you want it to run daily at midnight
    },
    'mail_to_user_before_birthday': {
        'task': 'foursquare.tasks.mail_to_user_before_birthday',
        'schedule': crontab(),
    }
}


@app.task(bind=True)
def debug_task(self):
    print('Request: {0!r}'.format(self.request))