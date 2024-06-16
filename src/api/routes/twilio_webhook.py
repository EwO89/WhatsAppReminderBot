import re
import logging
from fastapi import APIRouter, Request
from twilio.twiml.messaging_response import MessagingResponse
from src.utils.reminder_service import schedule_reminder, get_reminders
from src.utils.twilio_client import send_twilio_message

router = APIRouter()

logger = logging.getLogger(__name__)


@router.post("/webhooks/twilio")
async def twilio_webhook(request: Request):
    form_data = await request.form()
    from_number = form_data.get("From")
    body = form_data.get("Body")

    reminder_regex = re.compile(r"remind me to (.+) at (\d{4}-\d{2}-\d{2} \d{2}:\d{2})(?: in (.+))?")
    list_regex = re.compile(r"list reminders", re.IGNORECASE)

    reminder_match = reminder_regex.match(body)
    list_match = list_regex.match(body)

    if reminder_match:
        reminder_text = reminder_match.group(1)
        reminder_time_str = reminder_match.group(2)
        user_tz = reminder_match.group(3) or 'Europe/Moscow'

        schedule_reminder(from_number, reminder_text, reminder_time_str, user_tz)
        response_message = f"Reminder set for '{reminder_text}' at {reminder_time_str} in {user_tz}."
        send_twilio_message(response_message, from_number)
    elif list_match:
        reminders = get_reminders(from_number)
        if reminders:
            response_message = "Here are your reminders:\n" + "\n".join(reminders)
        else:
            response_message = "You have no reminders."
        send_twilio_message(response_message, from_number)
    else:
        response_message = (
            "Sorry, I didn't understand that command. You can ask me to 'remind me to [task] at [YYYY-MM-DD HH:MM] in [Timezone]' "
            "or 'list reminders'."
        )
        send_twilio_message(response_message, from_number)

    return MessagingResponse()
