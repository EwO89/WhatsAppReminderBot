import os
from dotenv import load_dotenv

load_dotenv()


class BaseSettings:
    def __init__(
            self
    ):
        self.REDIS_HOST: str = os.getenv("REDIS_HOST")
        self.REDIS_PORT: int = int(os.getenv("REDIS_PORT"))
        self.CELERY_BROKER_URL: str = os.getenv("CELERY_BROKER_URL")
        self.CELERY_RESULT_BACKEND: str = os.getenv("CELERY_RESULT_BACKEND")
        self.TWILIO_ACCOUNT_SID: str = os.getenv("TWILIO_ACCOUNT_SID")
        self.TWILIO_AUTH_TOKEN: str = os.getenv("TWILIO_AUTH_TOKEN")
        self.TWILIO_PHONE_NUMBER: str = os.getenv("TWILIO_PHONE_NUMBER")
        self.TWILIO_WHATSAPP_NUMBER: str = os.getenv("TWILIO_WHATSAPP_NUMBER")


class Settings(BaseSettings):
    def __init__(
            self
    ):
        super().__init__()


settings = Settings()
