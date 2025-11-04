from __future__ import annotations
import os
from celery import Celery

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "expense_tracker.settings")

# creating celery app instance
app = Celery("expense_tracker")

app.config_from_object("django.conf:settings", namespace="CELERY")
# auto-detect tasks.py
app.autodiscover_tasks()
