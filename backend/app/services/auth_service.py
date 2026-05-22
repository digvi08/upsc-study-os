"""Authentication service."""
import secrets
import uuid
from datetime import datetime, timedelta
from typing import Optional, Tuple
from sqlalchemy.orm import Session
from fastapi import HTTPException, status
import httpx
import logging

from app.models.user import User, UserRole, ExamTarget
from app.models.analytics import UserAnalytics
from app.auth.password import hash_password, verify_password
from app.auth.jwt_handler import create_access_token, create_refresh_token, verify_refresh_token
from app.schemas.auth import RegisterRequest, LoginRequest, TokenResponse
from app.config import settings

logger = logging.getLogger(__name__)


class AuthService:
    def __init__(self, db: Session):
        self.db = db

    def register(self, data: RegisterRequest) -> Tuple[User, TokenResponse]:
        """Register a new user."""
        # Check email uniqueness
        if self.db.query(User).filter(User.email == data.email).first():
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Email already registered",
            )
        # Check username uniqueness
        if self.db.query(User).filter(User.username == data.username).first():
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Username already taken",
            )

        user = User(
            email=data.email,
            username=data.username,
            full_name=data.full_name,
            hashed_password=hash_password(data.password),
            exam_target=ExamTarget(data.exam_target),
            is_verified=False,
            role=UserRole.STUDENT,
        )
        self.db.add(user)
        self.db.flush()

        # Create analytics record
        analytics = UserAnalytics(user_id=user.id)
        self.db.add(analytics)
        self.db.commit()
        self.db.refresh(user)

        tokens = self._generate_tokens(user)
        return user, tokens

    def login(self, data: LoginRequest) -> Tuple[User, TokenResponse]:
        """Authenticate user and return tokens."""
        user = self.db.query(User).filter(
            User.email == data.email,
            User.is_deleted == False,
        ).first()

        if not user or not user.hashed_password:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid email or password",
            )
        if not verify_password(data.password, user.hashed_password):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid email or password",
            )
        if not user.is_active:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Account is deactivated",
            )

        tokens = self._generate_tokens(user)
        return user, tokens

    def refresh_tokens(self, refresh_token: str) -> TokenResponse:
        """Refresh access token using refresh token."""
        payload = verify_refresh_token(refresh_token)
        user_id = payload.get("sub")

        user = self.db.query(User).filter(
            User.id == uuid.UUID(user_id),
            User.is_active == True,
            User.is_deleted == False,
        ).first()

        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="User not found",
            )

        return self._generate_tokens(user)

    async def google_oauth(self, code: str, redirect_uri: Optional[str] = None) -> Tuple[User, TokenResponse]:
        """Handle Google OAuth login/registration."""
        # Exchange code for tokens
        token_url = "https://oauth2.googleapis.com/token"
        async with httpx.AsyncClient() as client:
            token_response = await client.post(token_url, data={
                "code": code,
                "client_id": settings.google_client_id,
                "client_secret": settings.google_client_secret,
                "redirect_uri": redirect_uri or settings.google_redirect_uri,
                "grant_type": "authorization_code",
            })

        if token_response.status_code != 200:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Failed to exchange Google auth code",
            )

        google_tokens = token_response.json()
        id_token = google_tokens.get("id_token")

        # Get user info from Google
        async with httpx.AsyncClient() as client:
            userinfo_response = await client.get(
                "https://www.googleapis.com/oauth2/v3/userinfo",
                headers={"Authorization": f"Bearer {google_tokens['access_token']}"},
            )

        if userinfo_response.status_code != 200:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Failed to get Google user info",
            )

        google_user = userinfo_response.json()
        google_id = google_user.get("sub")
        email = google_user.get("email")
        name = google_user.get("name", "")
        picture = google_user.get("picture")

        # Find or create user
        user = self.db.query(User).filter(User.google_id == google_id).first()
        if not user:
            user = self.db.query(User).filter(User.email == email).first()

        if user:
            # Update Google info
            user.google_id = google_id
            user.oauth_provider = "google"
            if picture:
                user.profile_picture = picture
        else:
            # Create new user
            username = email.split("@")[0].lower()
            base_username = username
            counter = 1
            while self.db.query(User).filter(User.username == username).first():
                username = f"{base_username}{counter}"
                counter += 1

            user = User(
                email=email,
                username=username,
                full_name=name,
                google_id=google_id,
                oauth_provider="google",
                profile_picture=picture,
                is_verified=True,
                role=UserRole.STUDENT,
            )
            self.db.add(user)
            self.db.flush()

            analytics = UserAnalytics(user_id=user.id)
            self.db.add(analytics)

        self.db.commit()
        self.db.refresh(user)
        tokens = self._generate_tokens(user)
        return user, tokens

    def _generate_tokens(self, user: User) -> TokenResponse:
        """Generate access and refresh tokens for a user."""
        token_data = {"sub": str(user.id), "email": user.email, "role": user.role.value}
        access_token = create_access_token(token_data)
        refresh_token = create_refresh_token(token_data)
        return TokenResponse(
            access_token=access_token,
            refresh_token=refresh_token,
            expires_in=settings.access_token_expire_minutes * 60,
        )
