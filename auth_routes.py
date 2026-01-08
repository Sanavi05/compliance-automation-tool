from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import HTTPBearer
from sqlalchemy.orm import Session
from pydantic import BaseModel
from database import get_db
from auth import create_access_token
from models import User
from datetime import datetime

auth_router = APIRouter(prefix="/api/auth", tags=["Authentication"])
security = HTTPBearer()


class UserRegister(BaseModel):
    user_id: str
    full_name: str
    password: str


class UserLogin(BaseModel):
    user_id: str
    password: str


@auth_router.post("/register")
def register(user_data: UserRegister, db: Session = Depends(get_db)):
    """Register a new user"""
    try:
        # Check if user already exists
        existing_user = db.query(User).filter(User.user_id == user_data.user_id).first()
        if existing_user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="User ID already exists"
            )
        
        # Create new user
        new_user = User(
            user_id=user_data.user_id,
            full_name=user_data.full_name,
            aadhar_verified=False,
            pan_verified=False,
            bank_verified=False,
            onboarding_date=datetime.utcnow(),
            risk_profile="LOW"
        )
        
        db.add(new_user)
        db.commit()
        db.refresh(new_user)
        
        # Create access token
        access_token = create_access_token(data={"sub": user_data.user_id})
        
        return {
            "message": "User registered successfully",
            "access_token": access_token,
            "token_type": "bearer",
            "user_id": user_data.user_id
        }
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Registration failed: {str(e)}"
        )


@auth_router.post("/login")
def login(credentials: UserLogin, db: Session = Depends(get_db)):
    """Login and get JWT token"""
    try:
        # For simplicity, we'll auto-create users if they don't exist
        # In production, you'd have a separate users table with passwords
        user = db.query(User).filter(User.user_id == credentials.user_id).first()
        
        if not user:
            # Create user if doesn't exist (for development)
            user = User(
                user_id=credentials.user_id,
                full_name=credentials.user_id,
                aadhar_verified=False,
                pan_verified=False,
                bank_verified=False,
                onboarding_date=datetime.utcnow(),
                risk_profile="LOW"
            )
            db.add(user)
            db.commit()
            db.refresh(user)
        
        # Create access token
        access_token = create_access_token(data={"sub": credentials.user_id})
        
        return {
            "access_token": access_token,
            "token_type": "bearer",
            "user_id": credentials.user_id
        }
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Login failed: {str(e)}"
        )
