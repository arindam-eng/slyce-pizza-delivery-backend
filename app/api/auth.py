from fastapi import APIRouter, Depends, HTTPException, Body, Request
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
import jwt

from app.config import settings
from app.schemas.user import UserCreate, UserProfile, UserOut, TokenData, OTPRequest
from app.services.auth_service import (
    send_otp, verify_otp, create_user, update_user_profile, 
    create_access_token, create_refresh_token
)
from app.api.middleware.auth_middleware import get_current_user, role_required

router = APIRouter(prefix="/auth", tags=["Authentication"])
security = HTTPBearer()

@router.post("/send-otp", status_code=200)
async def request_otp(request: OTPRequest):
    """Send OTP to the provided mobile number"""
    result = await send_otp(request.mobile)
    return result

@router.post("/verify-otp", response_model=TokenData)
async def verify_otp_route(mobile: str = Body(...), otp: str = Body(...)):
    """Verify OTP and return auth tokens"""
    is_valid = await verify_otp(mobile, otp)
    print(is_valid, mobile, otp)
    
    if not is_valid:
        raise HTTPException(status_code=400, detail="Invalid OTP")
    
    # Create or get user14546---------
    user = await create_user(mobile)
    
    # Generate tokens
    # Todo: checn the user role, replace 'admin' with the actual role => user.role
    access_token = await create_access_token({"sub": str(user.id), "role": 'admin'})
    refresh_token = await create_refresh_token({"sub": str(user.id), "role": 'admin'})
    
    return TokenData(access_token=access_token, refresh_token=refresh_token, user=user)

@router.post("/refresh-otp")
async def refresh_otp(request: OTPRequest):
    """Regenerate and send a new OTP"""
    result = await send_otp(request.mobile)
    return result

@router.post("/complete-profile", response_model=UserOut)
async def complete_profile(
    profile: UserProfile,
    user = Depends(get_current_user)
):
    """Complete user profile after OTP verification"""
    updated_user = await update_user_profile(user.id, profile)
    return updated_user

@router.get("/me", response_model=UserOut)
async def get_current_user_route(user = Depends(get_current_user)):
    """Get current authenticated user details"""
    return user

@router.post("/refresh-token", response_model=TokenData)
async def refresh_token(credentials: HTTPAuthorizationCredentials = Depends(security)):
    """Refresh access token using refresh token"""
    refresh_token = credentials.credentials
    
    try:
        payload = jwt.decode(refresh_token, settings.JWT_SECRET_KEY, algorithms=[settings.JWT_ALGORITHM])
        user_id = payload.get("sub")
        
        if user_id is None:
            raise HTTPException(status_code=401, detail="Invalid token")
        
        # Generate new tokens
        access_token = await create_access_token({"sub": user_id})
        new_refresh_token = await create_refresh_token({"sub": user_id})
        
        return TokenData(access_token=access_token, refresh_token=new_refresh_token)
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Refresh token has expired, please login again")
    except jwt.InvalidTokenError:
        raise HTTPException(status_code=401, detail="Invalid refresh token")
