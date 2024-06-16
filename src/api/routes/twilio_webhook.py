from fastapi import APIRouter, Form
import re
from datetime import datetime, timezone
import logging
from src.utils.twilio_client import send_twilio_message
from src.utils.redis_client import save_reminder
from src.utils.celery_client import send_reminder

router = APIRouter()

logging.basicConfig(level=logging.INFO)

reminder_pattern = re.compile(r'remind me to (.+) at (.+)', re.IGNORECASE)


@router.post("/webhooks/twilio")
async def receive_message(From: str = Form(...), Body: str = Form(...)):
    logging.info(f"Received message from {From}: {Body}")
    match = reminder_pattern.match(Body)

    if match:
        reminder_text = match.group(1)
        reminder_time_str = match.group(2)

        try:
            reminder_time = datetime.strptime(reminder_time_str, '%Y-%m-%d %H:%M')
            reminder_time_utc = reminder_time.replace(tzinfo=timezone.utc)
            logging.info(f"Parsed reminder: {reminder_text} at {reminder_time_utc}")

            save_reminder(From, reminder_text, reminder_time_utc)

            delay = (reminder_time_utc - datetime.utcnow().replace(tzinfo=timezone.utc)).total_seconds()
            send_reminder.apply_async((From, f"Reminder: {reminder_text}"), countdown=delay)

            send_twilio_message(f"Got it! I'll remind you to '{reminder_text}' at {reminder_time_str}.", From)
        except ValueError:
            logging.error("Failed to parse date and time")
            send_twilio_message("Sorry, I couldn't understand the time format. Please use 'YYYY-MM-DD HH:MM'.", From)
    else:
        logging.warning("Message did not match the expected format")
        send_twilio_message("Please use the format 'remind me to [reminder] at [YYYY-MM-DD HH:MM]'.", From)

    logging.info("Response sent to Twilio")
    return "OK"
