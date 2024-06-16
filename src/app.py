import uvicorn
from fastapi import FastAPI
from src.api.routes import twilio_webhook, home
from src.config.base import settings

app = FastAPI(
    title="WhatsAppReminderBot",
    version="1.0.0",
    description="Whatsapp ReminderBot Bot service",
)
app.include_router(twilio_webhook.router)
app.include_router(home.router)

if __name__ == '__main__':
    uvicorn.run(app, host=settings.HOST, port=settings.PORT)
