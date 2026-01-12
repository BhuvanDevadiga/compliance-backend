from celery import Celery

celery_app = Celery(
    "compliance_worker",
    broker="redis://localhost:6379/0",
    backend="redis://localhost:6379/0"
)

celery_app.autodiscover_tasks(["app.tasks"])

from celery.schedules import crontab

celery_app.conf.beat_schedule = {
    "daily-compliance-reminder": {
        "task": "app.tasks.reminders.daily_compliance_reminder",
        "schedule": crontab(hour=9, minute=0),
    }
}
