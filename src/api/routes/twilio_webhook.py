import re
from fastapi import APIRouter, Request
from twilio.twiml.messaging_response import MessagingResponse
from src.utils.reminder_service import schedule_reminder, get_reminders, delete_reminder
from src.utils.twilio_client import send_twilio_message

router = APIRouter()


@router.post("/webhooks/twilio")
async def twilio_webhook(request: Request):
    form = await request.form()
    from_number = form['From']
    body = form['Body'].strip().lower()

    reminder_pattern = re.compile(r"remind me to (.+) at (\d{4}-\d{2}-\d{2} \d{2}:\d{2})(?: in (.+))?")
    delete_pattern = re.compile(r"delete reminder (.+)")
    list_pattern = re.compile(r"list reminders")

    if reminder_match := reminder_pattern.match(body):
        reminder_text = reminder_match.group(1)
        reminder_time_str = reminder_match.group(2)
        user_tz = reminder_match.group(3) if reminder_match.group(3) else 'Europe/Moscow'
        reminder_id = schedule_reminder(from_number, reminder_text, reminder_time_str, user_tz)
        response_message = f"Reminder set for '{reminder_text}' at {reminder_time_str} in {user_tz}. [ID: {reminder_id}]"
    elif delete_match := delete_pattern.match(body):
        reminder_id = delete_match.group(1)
        if delete_reminder(from_number, reminder_id):
            response_message = f"Deleted reminder with ID {reminder_id}."
        else:
            response_message = f"No reminder found with ID {reminder_id}."
    elif list_pattern.match(body):
        reminders = get_reminders(from_number)
        response_message = "Here are your reminders:\n" + "\n".join(
            reminders) if reminders else "You have no current reminders."
    else:
        response_message = (
            "Sorry, I didn't understand that command. You can ask me to 'remind me to [task] at [YYYY-MM-DD HH:MM] in [Timezone]' or 'list reminders' or 'delete reminder [ID]'.")

    send_twilio_message(response_message, from_number)
    return str(MessagingResponse())
