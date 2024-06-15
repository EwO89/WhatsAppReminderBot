from fastapi import APIRouter, Form
from twilio.twiml.messaging_response import MessagingResponse

router = APIRouter()


@router.post("/webhooks/twilio")
async def receive_message(From: str = Form(...), Body: str = Form(...)):
    print(f"Received message from {From}: {Body}")

    response = MessagingResponse()
    response.message(f"Hello, you said: {Body}")

    return str(response)
