from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from database import get_db
from models import User
from services.auth import auth_service
from services.email_service import email_service
from pydantic import BaseModel, EmailStr
from typing import Optional
from datetime import datetime, timedelta, timezone

router = APIRouter()

class UserCreate(BaseModel):
    email: EmailStr
    password: str
    full_name: Optional[str] = None

class UserLogin(BaseModel):
    email: EmailStr
    password: str

class EmailVerificationRequest(BaseModel):
    email: EmailStr
    verification_code: str

class Token(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str
    user: dict

class RefreshTokenRequest(BaseModel):
    refresh_token: str

class SignupResponse(BaseModel):
    message: str
    email: str

class VerificationResponse(BaseModel):
    message: str
    email: str

@router.post("/signup", response_model=SignupResponse)
async def signup(user_data: UserCreate, db: AsyncSession = Depends(get_db)):
    """Register a new user and send verification email"""
    # Check if user exists
    result = await db.execute(select(User).where(User.email == user_data.email))
    if result.scalar_one_or_none():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )
    
    # Generate verification code
    verification_code = email_service.generate_verification_code()
    verification_expires = datetime.now(timezone.utc) + timedelta(minutes=10)
    
    # Create new user with unverified status
    hashed_password = auth_service.get_password_hash(user_data.password)
    new_user = User(
        email=user_data.email,
        hashed_password=hashed_password,
        full_name=user_data.full_name,
        is_email_verified=False,
        verification_code=verification_code,
        verification_code_expires_at=verification_expires
    )
    
    db.add(new_user)
    await db.commit()
    await db.refresh(new_user)
    
    # Send verification email
    try:
        email_service.send_verification_email(
            recipient_email=user_data.email,
            verification_code=verification_code,
            full_name=user_data.full_name
        )
    except Exception as e:
        print(f"Warning: Email sending failed: {str(e)}")
        # Continue with signup even if email fails (for testing)
    
    return {
        "message": "Account created successfully. Please verify your email with the 6-digit code sent to your inbox.",
        "email": new_user.email
    }

@router.post("/verify-email", response_model=VerificationResponse)
async def verify_email(request: EmailVerificationRequest, db: AsyncSession = Depends(get_db)):
    """Verify email with the verification code"""
    # Find user
    result = await db.execute(select(User).where(User.email == request.email))
    user = result.scalar_one_or_none()
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    if user.is_email_verified:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already verified"
        )
    
    # Check verification code
    if user.verification_code != request.verification_code:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid verification code"
        )
    
    # Check if code expired
    if datetime.now(timezone.utc) > user.verification_code_expires_at:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Verification code expired. Please signup again."
        )
    
    # Mark email as verified
    user.is_email_verified = True
    user.verification_code = None
    user.verification_code_expires_at = None
    
    await db.commit()
    
    return {
        "message": "Email verified successfully. You can now login.",
        "email": user.email
    }

@router.post("/login", response_model=Token)
async def login(user_data: UserLogin, db: AsyncSession = Depends(get_db)):
    """Login user if email is verified"""
    # Find user
    result = await db.execute(select(User).where(User.email == user_data.email))
    user = result.scalar_one_or_none()
    
    if not user or not auth_service.verify_password(user_data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # Check if email is verified
    if not user.is_email_verified:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Please verify your email before logging in"
        )
    
    # Generate tokens
    access_token = auth_service.create_access_token(data={"sub": user.id})
    refresh_token = auth_service.create_refresh_token(data={"sub": user.id})
    
    return {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "token_type": "bearer",
        "user": {
            "id": user.id,
            "email": user.email,
            "full_name": user.full_name
        }
    }

@router.post("/resend-verification", response_model=VerificationResponse)
async def resend_verification(email: EmailStr, db: AsyncSession = Depends(get_db)):
    """Resend verification code to email"""
    # Find user
    result = await db.execute(select(User).where(User.email == email))
    user = result.scalar_one_or_none()
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    if user.is_email_verified:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already verified"
        )
    
    # Generate new verification code
    verification_code = email_service.generate_verification_code()
    verification_expires = datetime.now(timezone.utc) + timedelta(minutes=10)
    
    user.verification_code = verification_code
    user.verification_code_expires_at = verification_expires
    
    await db.commit()
    
    # Send verification email
    try:
        email_service.send_verification_email(
            recipient_email=email,
            verification_code=verification_code,
            full_name=user.full_name
        )
    except Exception as e:
        print(f"Warning: Email sending failed: {str(e)}")
    
    return {
        "message": "New verification code sent to your email",
        "email": email
    }

@router.post("/refresh", response_model=Token)
async def refresh_token(request: RefreshTokenRequest, db: AsyncSession = Depends(get_db)):
    # Verify refresh token
    payload = auth_service.verify_token(request.refresh_token)
    if not payload or payload.get("type") != "refresh":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid refresh token",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    user_id = payload.get("sub")
    result = await db.execute(select(User).where(User.id == user_id))
    user = result.scalar_one_or_none()
    
    if not user:
        raise HTTPException(status_code=401, detail="User not found")
    
    # Generate new tokens
    access_token = auth_service.create_access_token(data={"sub": user.id})
    new_refresh_token = auth_service.create_refresh_token(data={"sub": user.id})
    
    return {
        "access_token": access_token,
        "refresh_token": new_refresh_token,
        "token_type": "bearer",
        "user": {
            "id": user.id,
            "email": user.email,
            "full_name": user.full_name
        }
    }

