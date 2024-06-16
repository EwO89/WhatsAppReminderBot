import redis
from datetime import datetime
from src.config.base import settings

redis_client = redis.StrictRedis(host=settings.REDIS_HOST, port=settings.REDIS_PORT, db=0)


def save_reminder(user: str,
                  reminder: str,
                  reminder_time: datetime
                  ):
    reminder_id = f"reminder:{user}:{reminder_time.timestamp()}"
    redis_client.hmset(reminder_id, {"reminder": reminder, "time": reminder_time.isoformat()})
    redis_client.zadd("reminders", {reminder_id: reminder_time.timestamp()})