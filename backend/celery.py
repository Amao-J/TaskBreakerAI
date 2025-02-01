
from __future__ import absolute_import, unicode_literals
import os
from celery import Celery
from celery.utils.log import get_task_logger

# set the default Django settings module for the 'celery' program.
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings')

app = Celery('backend')


app.config_from_object('django.conf:settings', namespace='CELERY')


app.autodiscover_tasks()
app.conf.broker_connection_retry_on_startup = True

@app.task(bind=True)
def debug_task(self):
    logger.info(f'Request: {self.request!r}')
