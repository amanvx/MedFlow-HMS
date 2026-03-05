from celery import Celery
from celery.schedules import crontab
from flask import Flask
import os


def make_celery(app):
    celery = Celery(
        app.import_name,
        backend=app.config.get("CELERY_RESULT_BACKEND", "redis://localhost:6379/0"),
        broker=app.config.get("CELERY_BROKER_URL", "redis://localhost:6379/0"),
    )
    celery.conf.update(app.config)

    class ContextTask(celery.Task):
        def __call__(self, *args, **kwargs):
            with app.app_context():
                return self.run(*args, **kwargs)

    celery.Task = ContextTask
    return celery


# Initialize Celery
celery = Celery("hms_tasks", broker="redis://localhost:6379/0")


@celery.on_after_configure.connect
def setup_periodic_tasks(sender, **kwargs):
    from app.tasks.email_tasks import send_daily_reminders, generate_monthly_reports

    # Daily email reminders at 8 AM
    sender.add_periodic_task(
        crontab(hour=8, minute=0),
        send_daily_reminders.s(),
        name="daily-appointment-reminders",
    )

    # Monthly reports on 1st of every month at 9 AM
    sender.add_periodic_task(
        crontab(hour=9, minute=0, day_of_month=1),
        generate_monthly_reports.s(),
        name="monthly-doctor-reports",
    )

