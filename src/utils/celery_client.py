from celery import Celery
from src.utils import client
from src.config.base import settings

celery_app = Celery('tasks', broker=settings.CELERY_BROKER_URL, backend=settings.CELERY_RESULT_BACKEND)


@celery_app.task
def send_reminder(to: str, message: str):
    client.messages.create(
        body=message,
        from_=settings.TWILIO_WHATSAPP_NUMBER,
        to=to
    )
