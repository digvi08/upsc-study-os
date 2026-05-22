"""Authentication routes."""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.services.auth_service import AuthService
from app.schemas.auth import (
    RegisterRequest, LoginRequest, TokenResponse,
    RefreshTokenRequest, ForgotPasswordRequest,
    ResetPasswordRequest, ChangePasswordRequest, GoogleAuthRequest,
)
from app.schemas.user import UserResponse
from app.schemas.common import MessageResponse
from app.auth.dependencies import get_current_user
from app.models.user import User

router = APIRouter(prefix="/auth", tags=["Authentication"])


@router.post("/register", response_model=dict, status_code=status.HTTP_201_CREATED)
async def register(data: RegisterRequest, db: Session = Depends(get_db)):
    """Register a new user account."""
    service = AuthService(db)
    user, tokens = service.register(data)
    return {
        "user": UserResponse.model_validate(user),
        "tokens": tokens,
        "message": "Registration successful",
    }


@router.post("/login", response_model=dict)
async def login(data: LoginRequest, db: Session = Depends(get_db)):
    """Login with email and password."""
    service = AuthService(db)
    user, tokens = service.login(data)
    return {
        "user": UserResponse.model_validate(user),
        "tokens": tokens,
        "message": "Login successful",
    }


@router.post("/refresh", response_model=TokenResponse)
async def refresh_token(data: RefreshTokenRequest, db: Session = Depends(get_db)):
    """Refresh access token using refresh token."""
    service = AuthService(db)
    return service.refresh_tokens(data.refresh_token)


@router.post("/google", response_model=dict)
async def google_auth(data: GoogleAuthRequest, db: Session = Depends(get_db)):
    """Authenticate with Google OAuth."""
    service = AuthService(db)
    user, tokens = await service.google_oauth(data.code, data.redirect_uri)
    return {
        "user": UserResponse.model_validate(user),
        "tokens": tokens,
        "message": "Google authentication successful",
    }


@router.get("/me", response_model=UserResponse)
async def get_me(current_user: User = Depends(get_current_user)):
    """Get current authenticated user."""
    return current_user


@router.post("/logout", response_model=MessageResponse)
async def logout(current_user: User = Depends(get_current_user)):
    """Logout (client should discard tokens)."""
    return MessageResponse(message="Logged out successfully")


@router.post("/forgot-password", response_model=MessageResponse)
async def forgot_password(data: ForgotPasswordRequest, db: Session = Depends(get_db)):
    """Send password reset email."""
    # In production, send email with reset token
    return MessageResponse(message="If the email exists, a reset link has been sent")


@router.post("/reset-password", response_model=MessageResponse)
async def reset_password(data: ResetPasswordRequest, db: Session = Depends(get_db)):
    """Reset password using token."""
    return MessageResponse(message="Password reset successfully")
