from celery import Celery
from twilio.rest import Client
from src.config.base import settings
import logging

celery_app = Celery('tasks', broker=settings.CELERY_BROKER_URL, backend=settings.CELERY_RESULT_BACKEND)

client = Client(settings.TWILIO_ACCOUNT_SID, settings.TWILIO_AUTH_TOKEN)

logging.basicConfig(level=logging.INFO)


@celery_app.task(name='src.utils.celery_client.send_reminder')
def send_reminder(to: str, message: str):
    logging.info(f"Sending reminder to {to}: {message}")
    try:
        client.messages.create(
            body=message,
            from_=settings.TWILIO_WHATSAPP_NUMBER,
            to=to
        )
        logging.info(f"Reminder sent to {to}")
    except Exception as e:
        logging.error(f"Failed to send reminder to {to}: {e}")
        raise e



celery_app.autodiscover_tasks(['src.utils'], force=True)
