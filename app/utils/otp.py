import random
import string
from datetime import datetime, timedelta
from twilio.rest import Client
from app.config import settings

# Simple in-memory OTP store (use Redis in production)
otp_store = {}

def generate_otp(length=6):
    """Generate a random numeric OTP of specified length"""
    return ''.join(random.choices(string.digits, k=length))

def save_otp(phone_number: str, otp: str):
    """Save OTP with expiry time"""
    expiry = datetime.now() + timedelta(minutes=settings.OTP_EXPIRY_MINUTES)
    otp_store[phone_number] = {"otp": otp, "expiry": expiry}

def verify_otp(phone_number: str, otp: str) -> bool:
    """Verify if OTP is valid and not expired"""
    if phone_number not in otp_store:
        return False
    
    stored_data = otp_store[phone_number]
    
    # Check if OTP is expired
    if datetime.now() > stored_data["expiry"]:
        del otp_store[phone_number]
        return False
    
    # Check if OTP matches
    if stored_data["otp"] != otp:
        return False
    
    # OTP is valid, remove it from store
    del otp_store[phone_number]
    return True

def send_otp_via_sms(phone_number: str, otp: str):
    """Send OTP via Twilio SMS"""
    print(settings);
    # Skip if in development mode or Twilio credentials not set
    if not all([settings.TWILIO_ACCOUNT_SID, settings.TWILIO_AUTH_TOKEN, settings.TWILIO_PHONE_NUMBER]):
        print(f"Would send OTP {otp} to {phone_number}")
        return True
    
    try:
        client = Client(settings.TWILIO_ACCOUNT_SID, settings.TWILIO_AUTH_TOKEN)
        message = client.messages.create(
            body=f"Your Pizza Delivery verification code is: {otp}",
            from_=settings.TWILIO_PHONE_NUMBER,
            to=phone_number
        )
        return True
    except Exception as e:
        print(f"Error sending SMS: {e}")
        return False