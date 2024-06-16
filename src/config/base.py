from pydantic_settings import BaseSettings
from pathlib import Path

BASE_DIR = Path(__file__).absolute().parent.parent.parent


class Settings(
    BaseSettings
):
    REDIS_HOST: str
    REDIS_PORT: int
    CELERY_BROKER_URL: str
    CELERY_RESULT_BACKEND: str
    TWILIO_ACCOUNT_SID: str
    TWILIO_AUTH_TOKEN: str
    TWILIO_PHONE_NUMBER: str
    TWILIO_WHATSAPP_NUMBER: str
    PORT: int
    HOST: str

    class Config:
        env_file = BASE_DIR / '.env'
        extra = 'ignore'


settings = Settings()
