from celery import Celery
from twilio.rest import Client
from src.config.base import settings
import logging

celery_app = Celery('tasks', broker=settings.CELERY_BROKER_URL, backend=settings.CELERY_RESULT_BACKEND)

client = Client(settings.TWILIO_ACCOUNT_SID, settings.TWILIO_AUTH_TOKEN)

logging.basicConfig(level=logging.INFO)

@celery_app.task(bind=True)
def send_reminder(self, to: str, message: str):
    logging.info(f"Task {self.request.id}: Sending reminder to {to}: {message}")
    try:
        client.messages.create(
            body=message,
            from_=settings.TWILIO_WHATSAPP_NUMBER,
            to=to
        )
        logging.info(f"Task {self.request.id}: Reminder sent to {to}")
    except Exception as e:
        logging.error(f"Task {self.request.id}: Failed to send reminder to {to}: {e}")
        self.retry(exc=e, countdown=60, max_retries=3)
