import pytest
from src.utils.twilio_client import send_twilio_message


@pytest.fixture
def mock_twilio_client(
        mocker
):
    return mocker.patch("src.utils.twilio_client.Client")


def test_send_twilio_message(
        mock_twilio_client
):
    mock_instance = mock_twilio_client.return_value
    mock_messages = mock_instance.messages
    mock_create = mock_messages.create

    mock_create.return_value.sid = "SMXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX"

    to = "whatsapp:+79026212196"
    message = "Hello from Twilio WhatsApp!"

    message_sid = send_twilio_message(message, to)

    mock_create.assert_called_once_with(
        body=message,
        from_='whatsapp:+YOUR_TWILIO_PHONE_NUMBER',
        to=to
    )
    assert message_sid == "SMXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX"
