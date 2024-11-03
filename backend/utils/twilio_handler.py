from twilio.rest import Client
from twilio.twiml.messaging_response import MessagingResponse
import os
from dotenv import load_dotenv

class TwilioHandler:
    def __init__(self):
        load_dotenv()
        self.account_sid = os.getenv('TWILIO_ACCOUNT_SID')
        self.auth_token = os.getenv('TWILIO_AUTH_TOKEN')
        self.whatsapp_number = os.getenv('TWILIO_WHATSAPP_NUMBER')
        
        if all([self.account_sid, self.auth_token, self.whatsapp_number]):
            self.client = Client(self.account_sid, self.auth_token)
        else:
            print("Warning: Twilio credentials not found in .env file")
            self.client = None

    def send_whatsapp_message(self, to_number: str, message: str) -> bool:
        """Send WhatsApp message using Twilio"""
        try:
            if not self.client:
                print("Error: Twilio client not initialized")
                return False

            message = self.client.messages.create(
                from_=f'whatsapp:{self.whatsapp_number}',
                body=message,
                to=f'whatsapp:{to_number}'
            )
            
            return True
        except Exception as e:
            print(f"Error sending WhatsApp message: {str(e)}")
            return False

    def create_response(self, message: str) -> str:
        """Create TwiML response for incoming messages"""
        try:
            resp = MessagingResponse()
            resp.message(message)
            return str(resp)
        except Exception as e:
            print(f"Error creating response: {str(e)}")
            return ""