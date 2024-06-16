import uvicorn
from fastapi import FastAPI
from src.api.routes import twilio_webhook, home

app = FastAPI()
app.include_router(twilio_webhook.router)
app.include_router(home.router)

if __name__ == '__main__':
    uvicorn.run(app, host='127.0.0.1', port=8000)
