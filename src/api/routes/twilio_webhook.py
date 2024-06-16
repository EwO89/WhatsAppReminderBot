from fastapi import APIRouter, Request
from src.utils.twilio_client import send_twilio_message
from src.utils.reminder_service import schedule_reminder, get_reminders, delete_reminder, delete_reminder_by_index

router = APIRouter()


@router.post("/webhooks/twilio")
async def twilio_webhook(request: Request):
    form = await request.form()
    from_number = form.get("From")
    body = form.get("Body").strip().lower()

    if body.startswith("remind me to"):
        try:
            parts = body.split("at")
            reminder_text = parts[0].replace("remind me to", "").strip()
            time_part = parts[1].strip()
            if "in" in time_part:
                reminder_time_str, user_tz = time_part.split("in")
                user_tz = user_tz.strip()
            else:
                reminder_time_str = time_part.strip()
                user_tz = 'Europe/Moscow'
            reminder_time_str = reminder_time_str.strip()
            reminder_id = schedule_reminder(from_number, reminder_text, reminder_time_str, user_tz)
            confirmation_msg = f"Reminder set for '{reminder_text}' at {reminder_time_str} in {user_tz}."
            send_twilio_message(confirmation_msg, from_number)
        except Exception as e:
            error_msg = "Sorry, I didn't understand that command. You can ask me to 'remind me to [task] at [YYYY-MM-DD HH:MM] in [Timezone]' or 'list reminders' or 'delete reminder [ID]'."
            send_twilio_message(error_msg, from_number)
    elif body == "list reminders":
        reminders = get_reminders(from_number)
        reminders_text = "\n".join(reminders)
        if not reminders:
            reminders_text = "You have no reminders."
        send_twilio_message(f"Here are your reminders:\n{reminders_text}", from_number)
    elif body.startswith("delete reminder"):
        try:
            _, identifier = body.split("delete reminder")
            identifier = identifier.strip()
            if identifier.isdigit():
                index = int(identifier)
                if delete_reminder_by_index(from_number, index):
                    confirmation_msg = f"Deleted reminder with index {index}."
                else:
                    confirmation_msg = f"Failed to delete reminder with index {index}."
            else:
                if delete_reminder(from_number, identifier):
                    confirmation_msg = f"Deleted reminder with ID {identifier}."
                else:
                    confirmation_msg = f"Failed to delete reminder with ID {identifier}."
            send_twilio_message(confirmation_msg, from_number)
        except Exception as e:
            error_msg = "Sorry, I didn't understand that command. You can ask me to 'delete reminder [ID]' or 'delete reminder [index]'."
            send_twilio_message(error_msg, from_number)
    else:
        error_msg = "Sorry, I didn't understand that command. You can ask me to 'remind me to [task] at [YYYY-MM-DD HH:MM] in [Timezone]', 'list reminders' or 'delete reminder [ID]' or 'delete reminder [index]'."
        send_twilio_message(error_msg, from_number)
