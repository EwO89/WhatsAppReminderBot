import logging
from src.utils.reminder_service import ReminderServiceDelete
from src.config.base import settings

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

user_phone_number = settings.TWILIO_WHATSAPP_NUMBER
if ReminderServiceDelete.delete_all_reminders(user_phone_number):
    logger.info(f"All reminders for {user_phone_number} have been deleted.")
else:
    logger.info(f"No reminders found for {user_phone_number}.")
