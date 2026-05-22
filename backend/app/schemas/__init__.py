from .auth import (
    RegisterRequest, LoginRequest, TokenResponse,
    RefreshTokenRequest, ForgotPasswordRequest,
    ResetPasswordRequest, ChangePasswordRequest, GoogleAuthRequest
)
from .user import UserCreate, UserUpdate, UserResponse, UserProfileResponse
from .subject import (
    SubjectCreate, SubjectUpdate, SubjectResponse,
    TopicCreate, TopicUpdate, TopicResponse, TopicWithSubtopics
)
from .note import NoteCreate, NoteUpdate, NoteResponse, AIGenerateNoteRequest
from .pyq import PYQCreate, PYQResponse, PYQAnalysisRequest, PYQAnalysisResponse
from .common import (
    PaginationParams, PaginatedResponse,
    MessageResponse, ErrorResponse,
    AIQueryRequest, AIQueryResponse
)

__all__ = [
    "RegisterRequest", "LoginRequest", "TokenResponse",
    "RefreshTokenRequest", "ForgotPasswordRequest",
    "ResetPasswordRequest", "ChangePasswordRequest", "GoogleAuthRequest",
    "UserCreate", "UserUpdate", "UserResponse", "UserProfileResponse",
    "SubjectCreate", "SubjectUpdate", "SubjectResponse",
    "TopicCreate", "TopicUpdate", "TopicResponse", "TopicWithSubtopics",
    "NoteCreate", "NoteUpdate", "NoteResponse", "AIGenerateNoteRequest",
    "PYQCreate", "PYQResponse", "PYQAnalysisRequest", "PYQAnalysisResponse",
    "PaginationParams", "PaginatedResponse",
    "MessageResponse", "ErrorResponse",
    "AIQueryRequest", "AIQueryResponse",
]
