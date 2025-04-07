import random
import string
import jwt
from datetime import datetime, timedelta
from typing import Optional
from fastapi import HTTPException
from sqlalchemy.future import select
from sqlalchemy.exc import IntegrityError

from app.models.user import User, UserRole
from app.schemas.user import UserCreate, UserProfile
from app.config import settings
from app.database import get_db
from app.redis import get_redis

# Twilio client setup
from twilio.rest import Client
from twilio.base.exceptions import TwilioRestException

twilio_client = Client(settings.TWILIO_ACCOUNT_SID, settings.TWILIO_AUTH_TOKEN)

async def generate_otp():
    """Generate a random OTP of specified length"""
    digits = string.digits
    return ''.join(random.choice(digits) for _ in range(settings.OTP_LENGTH))

async def send_otp(mobile: str):
    """Send OTP via Twilio and store in Redis"""
    # Generate OTP
    otp = await generate_otp()
    print(otp)
    
    # Store OTP in Redis with expiry
    redis_client = await get_redis()
    key = f"otp:{mobile}"
    await redis_client.set(key, otp, ex=settings.OTP_EXPIRY_SECONDS)
    
    # Send OTP via Twilio
    try:
        message = twilio_client.messages.create(
            body=f"Your verification code is: {otp}",
            from_=settings.TWILIO_PHONE_NUMBER,
            to=mobile
        )
        return {"message": "OTP sent successfully", "message_sid": message.sid, otp: otp}
    except TwilioRestException as e:
        # In development/testing environment, return the OTP
        if settings.ENVIRONMENT == "development":
            return {"message": "Development mode: OTP generated", "otp": otp}
        raise HTTPException(status_code=500, detail=f"Failed to send OTP: {str(e)}")

async def verify_otp(mobile: str, otp: str):
    """Verify the OTP for the given mobile number"""
    redis_client = await get_redis()
    key = f"otp:{mobile}"
    stored_otp = await redis_client.get(key)
    
    if not stored_otp or stored_otp != otp:
        return False
    
    # Delete the OTP after successful verification
    await redis_client.delete(key)
    return True

async def create_user(mobile: str):
    """Create a new user if not exists"""
    async with get_db() as db:
        # Check if user already exists
        result = await db.execute(select(User).where(User.mobile == mobile))
        if (user := result.scalar()):
            return user
        
        # Create new user
        new_user = User(
            mobile=mobile,
            role=UserRole.CUSTOMER,
            is_verified=True,
            is_profile_complete=False,
        )
        
        db.add(new_user)
        try:
            await db.commit()
            await db.refresh(new_user)
            return new_user
        except IntegrityError:
            await db.rollback()
            raise HTTPException(status_code=400, detail="User with this mobile already exists")

async def update_user_profile(user_id: int, profile_data: UserProfile):
    """Update user profile information"""

    async with get_db() as db:  # Ensures proper DB session management
        result = await db.execute(select(User).where(User.id == user_id))
        user = result.scalars().first()

        if not user:
            raise HTTPException(status_code=404, detail="User not found")

        # Update only provided fields
        updated_fields = profile_data.dict(exclude_unset=True)
        for field, value in updated_fields.items():
            setattr(user, field, value)

        # Check if all required fields are filled
        required_fields = UserProfile.__fields__.keys()
        user.is_profile_complete = all(getattr(user, field) for field in required_fields)

        user.updated_at = datetime.utcnow()
        db.add(user)

        try:
            await db.commit()
            await db.refresh(user)
            return user
        except IntegrityError:
            await db.rollback()
            raise HTTPException(status_code=400, detail="Update failed. Possible duplicate email.")

async def get_user_by_id(user_id: int):
    """Get user by ID"""
    async with get_db() as db:
        result = await db.execute(select(User).where(User.id == user_id))
        return result.scalars().first()

async def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    """Create JWT access token"""
    to_encode = data.copy()
    
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=settings.JWT_ACCESS_TOKEN_EXPIRE_MINUTES)
    
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, settings.JWT_SECRET_KEY, algorithm=settings.JWT_ALGORITHM)
    return encoded_jwt

async def create_refresh_token(data: dict):
    """Create JWT refresh token with longer expiry"""
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(days=settings.JWT_REFRESH_TOKEN_EXPIRE_DAYS)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, settings.JWT_SECRET_KEY, algorithm=settings.JWT_ALGORITHM)
    return encoded_jwt