from twilio.rest import Client
from src.config.base import settings
from .celery_client import send_reminder
from .celery_client import celery_app


client = Client(settings.TWILIO_ACCOUNT_SID, settings.TWILIO_AUTH_TOKEN)
