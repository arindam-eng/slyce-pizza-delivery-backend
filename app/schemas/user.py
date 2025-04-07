from pydantic import BaseModel, Field, EmailStr, validator
from typing import Optional
from datetime import datetime
from app.models.user import UserRole

class UserBase(BaseModel):
    mobile: str
    
    @validator('mobile')
    def validate_mobile(cls, v):
        # Simple validation for mobile number format
        if not v.isdigit() or len(v) < 10:
            raise ValueError('Invalid mobile number format')
        return v

class UserCreate(UserBase):
    pass

class UserProfile(BaseModel):
    name: str
    email: Optional[EmailStr] = None
    address: Optional[str] = None
    profile_picture: Optional[str] = None

class UserInDB(UserBase):
    id: int
    name: Optional[str] = None
    email: Optional[str] = None
    role: UserRole
    is_active: bool
    is_verified: bool
    is_profile_complete: bool
    created_at: datetime
    updated_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True

class UserOut(BaseModel):
    id: int
    name: Optional[str] = None
    email: Optional[str] = None
    mobile: str
    role: UserRole
    is_verified: bool
    is_profile_complete: bool
    
    class Config:
        from_attributes = True

class TokenData(BaseModel):
    access_token: str
    refresh_token: str
    user: UserOut
    token_type: str = "bearer"

class OTPRequest(BaseModel):
    mobile: str
