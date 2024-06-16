import logging
from datetime import datetime, timezone
import pytz
from src.utils.redis_client import redis_client

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("app.log"),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)


def save_reminder(user: str, reminder: str, reminder_time: datetime, user_tz: str):
    reminder_id = f"reminder:{user}:{reminder_time.timestamp()}"
    redis_client.hset(reminder_id,
                      mapping={"reminder": reminder, "time": reminder_time.isoformat(), "user_tz": user_tz})
    redis_client.zadd("reminders", {reminder_id: reminder_time.timestamp()})
    logger.info(f"Saved reminder: {reminder} for user: {user} at time: {reminder_time} in timezone: {user_tz}")


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

    reminder_texts = []
    for reminder in current_reminders:
        if 'reminder' in reminder and 'time' in reminder and 'user_tz' in reminder:
            reminder_time_utc = datetime.fromisoformat(reminder['time'])
            user_timezone = pytz.timezone(reminder['user_tz'])
            reminder_time_local = reminder_time_utc.astimezone(user_timezone)
            utc_offset = reminder_time_local.utcoffset().total_seconds() / 3600
            if utc_offset != 0:
                offset_sign = '+' if utc_offset >= 0 else '-'
                offset_hours = int(abs(utc_offset))
                offset_minutes = int((abs(utc_offset) * 60) % 60)
                offset_str = f"UTC {offset_sign}{offset_hours:02}:{offset_minutes:02}"
                reminder_texts.append(
                    f"{reminder['reminder']} at {reminder_time_local.strftime('%Y-%m-%d %H:%M')} ({reminder['user_tz']}, {offset_str})")
            else:
                reminder_texts.append(
                    f"{reminder['reminder']} at {reminder_time_local.strftime('%Y-%m-%d %H:%M')} ({reminder['user_tz']})")
        else:
            logger.warning(f"Missing keys in reminder: {reminder}")

    logger.info(f"Found {len(reminder_texts)} current reminders for user: {user}")
    return reminder_texts


def schedule_reminder(user: str, reminder: str, reminder_time_str: str, user_tz: str = 'Europe/Moscow'):
    user_timezone = pytz.timezone(user_tz)
    reminder_time_local = datetime.strptime(reminder_time_str, '%Y-%m-%d %H:%M')
    reminder_time_utc = user_timezone.localize(reminder_time_local).astimezone(timezone.utc)
    save_reminder(user, reminder, reminder_time_utc, user_tz)
    delay = (reminder_time_utc - datetime.now(timezone.utc)).total_seconds()
    from src.utils.celery_client import send_reminder
    send_reminder.apply_async((user, f"Reminder: {reminder}"), countdown=delay)
    logger.info(
        f"Scheduled reminder: {reminder} for user: {user} at time: {reminder_time_utc} with delay: {delay} seconds")


def delete_reminder(user: str, reminder_time_str: str):
    try:
        reminder_time_local = datetime.strptime(reminder_time_str, '%Y-%m-%d %H:%M')
        reminder_time_utc = reminder_time_local.astimezone(timezone.utc)
        reminder_id = f"reminder:{user}:{reminder_time_utc.timestamp()}"

        logger.info(f"Trying to delete reminder: {reminder_id}")

        redis_client.delete(reminder_id)
        redis_client.zrem("reminders", reminder_id)
        logger.info(f"Deleted reminder for user: {user} at time: {reminder_time_utc}")
    except Exception as e:
        logger.error(f"Error deleting reminder: {e}")
