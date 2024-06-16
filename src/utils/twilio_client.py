from twilio.rest import Client
from src.config.base import settings
import logging

client = Client(settings.TWILIO_ACCOUNT_SID, settings.TWILIO_AUTH_TOKEN)

logging.basicConfig(level=logging.INFO)


def send_twilio_message(
        body: str,
        to: str
):
    logging.info(f"Sending message to {to}: {body}")
    try:
        message = client.messages.create(
            body=body,
            from_=settings.TWILIO_WHATSAPP_NUMBER,
            to=to
        )
        logging.info(f"Message sent to {to} with SID: {message.sid}")
        return message.sid
    except Exception as e:
        logging.error(f"Failed to send message to {to}: {e}")
        raise e
