from datetime import datetime, timezone
import pytz
from src.utils.redis_client import redis_client


def save_reminder(user: str, reminder: str, reminder_time: datetime, user_tz: str):
    reminder_id = f"reminder:{user}:{reminder_time.timestamp()}"
    redis_client.hset(reminder_id,
                      mapping={"reminder": reminder, "time": reminder_time.isoformat(), "user_tz": user_tz})
    redis_client.zadd("reminders", {reminder_id: reminder_time.timestamp()})


def get_reminders(user: str):
    keys = redis_client.keys(f"reminder:{user}:*")
    reminders = [redis_client.hgetall(key) for key in keys]

    decoded_reminders = []
    for reminder in reminders:
        decoded_reminder = {k.decode('utf-8'): v.decode('utf-8') for k, v in reminder.items()}
        decoded_reminders.append(decoded_reminder)

    now = datetime.now(timezone.utc)

    current_reminders = [reminder for reminder in decoded_reminders if
                         'time' in reminder and datetime.fromisoformat(reminder['time']).astimezone(timezone.utc) > now]

    reminder_texts = [f"{reminder['reminder']} at {reminder['time']} ({reminder['user_tz']})" for reminder in
                      current_reminders if
                      'reminder' in reminder and 'time' in reminder]

    for reminder in decoded_reminders:
        if 'reminder' not in reminder or 'time' not in reminder:
            print(f"Missing keys in reminder: {reminder}")

    return reminder_texts


def schedule_reminder(user: str, reminder: str, reminder_time_str: str, user_tz: str):
    user_timezone = pytz.timezone(user_tz)
    reminder_time_local = datetime.strptime(reminder_time_str, '%Y-%m-%d %H:%M')
    reminder_time_utc = user_timezone.localize(reminder_time_local).astimezone(timezone.utc)
    save_reminder(user, reminder, reminder_time_utc, user_tz)
    delay = (reminder_time_utc - datetime.now(timezone.utc)).total_seconds()
    from src.utils.celery_client import send_reminder
    send_reminder.apply_async((user, f"Reminder: {reminder}"), countdown=delay)
