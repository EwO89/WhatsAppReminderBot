from src.utils.reminder_service import delete_all_reminders

user_phone_number = "whatsapp:+79026212196"
if delete_all_reminders(user_phone_number):
    print(f"All reminders for {user_phone_number} have been deleted.")
else:
    print(f"No reminders found for {user_phone_number}.")
