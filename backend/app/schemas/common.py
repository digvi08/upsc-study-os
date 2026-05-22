"""Common/shared schemas."""
from pydantic import BaseModel
from typing import Optional, List, Any, Generic, TypeVar

T = TypeVar("T")


class PaginationParams(BaseModel):
    page: int = 1
    page_size: int = 20
    search: Optional[str] = None
    sort_by: Optional[str] = None
    sort_order: str = "desc"


class PaginatedResponse(BaseModel, Generic[T]):
    items: List[T]
    total: int
    page: int
    page_size: int
    total_pages: int
    has_next: bool
    has_prev: bool


class MessageResponse(BaseModel):
    message: str
    success: bool = True


class ErrorResponse(BaseModel):
    detail: str
    error_code: Optional[str] = None


class AIQueryRequest(BaseModel):
    query: str
    context: Optional[str] = None
    mode: str = "mains"  # beginner, prelims, mains, quick_revision
    subject: Optional[str] = None
    topic: Optional[str] = None


class AIQueryResponse(BaseModel):
    response: str
    sources: List[str] = []
    related_topics: List[str] = []
    current_affairs_links: List[dict] = []
