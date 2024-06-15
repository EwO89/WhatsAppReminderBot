from src.utils.twilio_client import send_twilio_message

if __name__ == "__main__":
    to = "whatsapp:+79026212196"
    message = "Hello from Twilio WhatsApp!"

    message_sid = send_twilio_message(message, to)
    print(f"Message sent with SID: {message_sid}")
