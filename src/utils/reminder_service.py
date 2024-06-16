from datetime import datetime
from src.utils.celery_client import send_reminder
import logging

logging.basicConfig(level=logging.INFO)


def schedule_reminder(to: str, message: str, reminder_time: datetime):
    reminder_time_naive = reminder_time.replace(tzinfo=None)
    delay = (reminder_time_naive - datetime.utcnow()).total_seconds()
    logging.info(f"Scheduling reminder to {to} in {delay} seconds")
    send_reminder.apply_async((to, message), countdown=delay)
