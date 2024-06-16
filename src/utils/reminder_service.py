from datetime import datetime, timezone
from src.utils.redis_client import redis_client


def save_reminder(user: str, reminder: str, reminder_time: datetime):
    reminder_id = f"reminder:{user}:{reminder_time.timestamp()}"
    redis_client.hmset(reminder_id, {"reminder": reminder, "time": reminder_time.isoformat()})
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

    reminder_texts = [f"{reminder['reminder']} at {reminder['time']}" for reminder in current_reminders if
                      'reminder' in reminder and 'time' in reminder]

    for reminder in decoded_reminders:
        if 'reminder' not in reminder or 'time' not in reminder:
            print(f"Missing keys in reminder: {reminder}")

    return reminder_texts


def schedule_reminder(user: str, reminder: str, reminder_time_str: str):
    reminder_time = datetime.strptime(reminder_time_str, '%Y-%m-%d %H:%M').replace(tzinfo=timezone.utc)
    save_reminder(user, reminder, reminder_time)
    delay = (reminder_time - datetime.now(timezone.utc)).total_seconds()
    from src.utils.celery_client import send_reminder
    send_reminder.apply_async((user, f"Reminder: {reminder}"), countdown=delay)
