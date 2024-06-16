import logging
from datetime import datetime, timezone
import pytz
import uuid
from src.utils.redis_client import redis_client
from src.utils.celery_client import send_reminder, celery_app

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("app.log"),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)


class ReminderServiceBase:
    pass


class ReminderStorage:
    @staticmethod
    def save_reminder(user: str, reminder: str, reminder_time: datetime, user_tz: str, reminder_id: str):
        reminder_key = f"reminder:{user}:{reminder_id}"
        redis_client.hset(reminder_key,
                          mapping={"reminder": reminder, "time": reminder_time.isoformat(), "user_tz": user_tz,
                                   "id": reminder_id})
        redis_client.zadd("reminders", {reminder_key: reminder_time.timestamp()})
        logger.info(f"Saved reminder: {reminder} for user: {user} at time: {reminder_time} in timezone: {user_tz}")

    @staticmethod
    def get_reminders(user: str):
        keys = redis_client.keys(f"reminder:{user}:*")
        reminders = [redis_client.hgetall(key) for key in keys]
        return reminders

    @staticmethod
    def delete_reminder(user: str, reminder_id: str):
        reminder_keys = redis_client.keys(f"reminder:{user}:{reminder_id}")
        if not reminder_keys:
            logger.warning(f"No reminders found for user: {user} with ID: {reminder_id}")
            return False
        for reminder_key in reminder_keys:
            redis_client.delete(reminder_key)
            redis_client.zrem("reminders", reminder_key)
            celery_app.control.revoke(reminder_id, terminate=True)
            logger.info(f"Deleted reminder for user: {user} with ID: {reminder_id}")
        return True

    @staticmethod
    def delete_all_reminders(user: str):
        reminder_keys = redis_client.keys(f"reminder:{user}:*")
        if not reminder_keys:
            logger.warning(f"No reminders found for user: {user}")
            return False
        for reminder_key in reminder_keys:
            reminder_id = reminder_key.decode().split(":")[-1]
            redis_client.delete(reminder_key)
            redis_client.zrem("reminders", reminder_key)
            celery_app.control.revoke(reminder_id, terminate=True)
            logger.info(f"Deleted reminder for user: {user} with key: {reminder_key}")
        return True


class ReminderUtils:
    @staticmethod
    def format_reminder(reminder, idx):
        reminder_time_utc = datetime.fromisoformat(reminder['time'])
        user_timezone = pytz.timezone(reminder['user_tz'])
        reminder_time_local = reminder_time_utc.astimezone(user_timezone)
        utc_offset = reminder_time_local.utcoffset().total_seconds() / 3600
        offset_sign = '+' if utc_offset >= 0 else '-'
        offset_hours = int(abs(utc_offset))
        offset_minutes = int((abs(utc_offset) * 60) % 60)
        offset_str = f"UTC {offset_sign}{offset_hours:02}:{offset_minutes:02}"
        reminder_text = (
            f"{idx}. {reminder['reminder']} at {reminder_time_local.strftime('%Y-%m-%d %H:%M')} "
            f"({reminder['user_tz']}, {offset_str})"
        )
        if 'id' in reminder:
            reminder_text += f" [ID: {reminder['id']}]"
        return reminder_text


class ReminderService(ReminderServiceBase):
    @staticmethod
    def get_reminders(user: str):
        reminders = ReminderStorage.get_reminders(user)
        decoded_reminders = [
            {k.decode('utf-8'): v.decode('utf-8') for k, v in reminder.items()}
            for reminder in reminders
        ]

        now = datetime.now(timezone.utc)
        current_reminders = [
            reminder for reminder in decoded_reminders
            if 'time' in reminder and datetime.fromisoformat(reminder['time']).astimezone(timezone.utc) > now
        ]

        sorted_reminders = sorted(
            current_reminders,
            key=lambda r: datetime.fromisoformat(r['time']).astimezone(timezone.utc)
        )

        reminder_texts = [
            ReminderUtils.format_reminder(reminder, idx)
            for idx, reminder in enumerate(sorted_reminders, start=1)
        ]

        logger.info(f"Found {len(reminder_texts)} current reminders for user: {user}")
        return reminder_texts

    @staticmethod
    def schedule_reminder(user: str, reminder: str, reminder_time_str: str, user_tz: str = 'Europe/Moscow'):
        user_timezone = pytz.timezone(user_tz)
        reminder_time_local = datetime.strptime(reminder_time_str, '%Y-%m-%d %H:%M')
        reminder_time_utc = user_timezone.localize(reminder_time_local).astimezone(timezone.utc)
        reminder_id = str(uuid.uuid4())
        ReminderStorage.save_reminder(user, reminder, reminder_time_utc, user_tz, reminder_id)
        delay = (reminder_time_utc - datetime.now(timezone.utc)).total_seconds()
        send_reminder.apply_async((user, f"Reminder: {reminder}"), countdown=delay, task_id=reminder_id)
        logger.info(
            f"Scheduled reminder: {reminder} for user: {user} at time: {reminder_time_utc} with delay: {delay} seconds")
        return reminder_id


class ReminderServiceDelete(ReminderServiceBase):
    @staticmethod
    def delete_reminder(user: str, reminder_id: str):
        return ReminderStorage.delete_reminder(user, reminder_id)

    @staticmethod
    def delete_reminder_by_index(user: str, index: int):
        reminders = ReminderService.get_reminders(user)
        if index < 1 or index > len(reminders):
            logger.warning(f"Invalid index: {index} for user: {user}")
            return False
        reminder_text = reminders[index - 1]
        reminder_id_start = reminder_text.rfind("[ID: ") + len("[ID: ")
        reminder_id_end = reminder_text.rfind("]")
        reminder_id = reminder_text[reminder_id_start:reminder_id_end]
        return ReminderStorage.delete_reminder(user, reminder_id)

    @staticmethod
    def delete_all_reminders(user: str):
        return ReminderStorage.delete_all_reminders(user)
