from src.config.base import settings
from src.utils import client


def send_twilio_message(
        message: str,
        to: str
):
    client.messages.create(
        body=message,
        from_=settings.TWILIO_WHATSAPP_NUMBER,
        to=to
    )