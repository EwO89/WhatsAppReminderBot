from fastapi import APIRouter, Request
from src.utils.twilio_client import send_twilio_message
from src.utils.reminder_service import ReminderService, ReminderServiceDelete

router = APIRouter()

reminder_service = ReminderService()
reminder_service_delete = ReminderServiceDelete()


@router.post("/webhooks/twilio")
async def twilio_webhook(
        request: Request
):
    form = await request.form()
    from_number = form.get("From")
    body = form.get("Body").strip().lower()

    if body == "/start":
        welcome_msg = "Welcome to the Reminder Bot! You can use the following commands:\n" \
                      "/help - Show this help message\n" \
                      "/list - List all reminders\n" \
                      "/delete [ID or index] - Delete a specific reminder by ID or index\n" \
                      "/add remind me to [task] at [YYYY-MM-DD HH:MM] in [Timezone]"
        send_twilio_message(welcome_msg, from_number)

    elif body == "/help":
        help_msg = "You can use the following commands:\n" \
                   "/list - List all reminders\n" \
                   "/delete [ID or index] - Delete a specific reminder by ID or index\n" \
                   "/add remind me to [task] at [YYYY-MM-DD HH:MM] in [Timezone] - set a new reminder"
        send_twilio_message(help_msg, from_number)

    elif body == "/list":
        reminders = reminder_service.get_reminders(from_number)
        reminders_text = "\n".join(reminders)
        if not reminders:
            reminders_text = "You have no reminders."
        send_twilio_message(f"Here are your reminders:\n{reminders_text}", from_number)

    elif body.startswith("/delete"):
        try:
            _, identifier = body.split(" ", 1)
            identifier = identifier.strip()
            if identifier.isdigit():
                index = int(identifier)
                if reminder_service_delete.delete_reminder_by_index(from_number, index):
                    confirmation_msg = f"Deleted reminder with index {index}."
                else:
                    confirmation_msg = f"Failed to delete reminder with index {index}."
            else:
                if reminder_service_delete.delete_reminder(from_number, identifier):
                    confirmation_msg = f"Deleted reminder with ID {identifier}."
                else:
                    confirmation_msg = f"Failed to delete reminder with ID {identifier}."
            send_twilio_message(confirmation_msg, from_number)
        except Exception as e:
            error_msg = "Sorry, I didn't understand that command. You can ask me to 'delete [ID or index]'."
            send_twilio_message(error_msg, from_number)

    elif body.startswith("/add remind me to"):
        try:
            parts = body.split("at")
            reminder_text = parts[0].replace("/add remind me to", "").strip()
            time_part = parts[1].strip()
            if "in" in time_part:
                reminder_time_str, user_tz = time_part.split("in")
                user_tz = user_tz.strip().title()
            else:
                reminder_time_str = time_part.strip()
                user_tz = 'Europe/Moscow'
            reminder_time_str = reminder_time_str.strip()
            reminder_id = reminder_service.schedule_reminder(from_number, reminder_text, reminder_time_str, user_tz)
            confirmation_msg = f"Reminder set for '{reminder_text}' at {reminder_time_str} in {user_tz}."
            send_twilio_message(confirmation_msg, from_number)
        except Exception as e:
            error_msg = "Sorry, I didn't understand that command. You can ask me to '/add remind me to [task] at [YYYY-MM-DD HH:MM] in [Timezone]' or '/list' or '/delete [ID or index]'."
            send_twilio_message(error_msg, from_number)

    else:
        error_msg = "Sorry, I didn't understand that command. You can ask me to '/add remind me to [task] at [YYYY-MM-DD HH:MM] in [Timezone]', '/list' or '/delete [ID or index]'."
        send_twilio_message(error_msg, from_number)
