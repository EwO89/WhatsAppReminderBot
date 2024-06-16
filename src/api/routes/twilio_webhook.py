from datetime import datetime

import pytz
from fastapi import APIRouter, Form
from src.utils.reminder_service import get_reminders, schedule_reminder
from src.utils.twilio_client import send_twilio_message
import re

router = APIRouter()


@router.post("/webhooks/twilio")
async def twilio_webhook(From: str = Form(...), Body: str = Form(...)):
    print(f"Received message from {From}: {Body}")

    set_reminder_match = re.match(r'remind me to (.+) at (.+) in (.+)', Body, re.IGNORECASE)
    if set_reminder_match:
        reminder_text = set_reminder_match.group(1)
        reminder_time_str = set_reminder_match.group(2)
        user_tz = set_reminder_match.group(3)

        try:

            datetime.strptime(reminder_time_str, '%Y-%m-%d %H:%M')
            pytz.timezone(user_tz)
            schedule_reminder(From, reminder_text, reminder_time_str, user_tz)
            response_message = f"Got it! I'll remind you to '{reminder_text}' at {reminder_time_str} in {user_tz}."
        except (ValueError, pytz.UnknownTimeZoneError):
            response_message = "Sorry, I didn't understand the time format or timezone. Please use 'YYYY-MM-DD HH:MM' for time and a valid timezone."

        send_twilio_message(response_message, From)
        return {"status": "ok"}

    if Body.strip().lower() == "list reminders":
        reminders = get_reminders(From)
        if reminders:
            response_message = "Here are your reminders:\n" + "\n".join(reminders)
        else:
            response_message = "You have no reminders."

        send_twilio_message(response_message, From)
        return {"status": "ok"}

    response_message = "Sorry, I didn't understand that command. You can ask me to 'remind me to [task] at [YYYY-MM-DD HH:MM] in [Timezone]' or 'list reminders'."
    send_twilio_message(response_message, From)
    return {"status": "ok"}
