from __future__ import absolute_import, unicode_literals
from celery import Celery
from celery.schedules import crontab
from django.conf import settings
import os

# set the default Django settings module for the 'celery' program.
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'plaid_django.settings')
app = Celery('plaid_django')

# Using a string here means the worker doesn't have to serialize
# the configuration object to child processes.
# - namespace='CELERY' means all celery-related configuration keys
#   should have a `CELERY_` prefix.
app.config_from_object('django.conf:settings',  namespace='CELERY')
app.autodiscover_tasks()
# app.conf.timezone = 'Asia/Kolkata'


@app.task(bind=True)
def debug_task(self):
    print('Request: {0!r}'.format(self.request))
