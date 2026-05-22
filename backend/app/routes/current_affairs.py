"""Current Affairs routes."""
from fastapi import APIRouter, Depends, Query, Body
from sqlalchemy.orm import Session
from typing import Optional, List
from datetime import date
import uuid

from app.database import get_db
from app.auth.dependencies import get_current_user, require_admin
from app.models.user import User
from app.services.current_affairs_service import CurrentAffairsService
from app.ai.mentor_service import MentorService
from app.schemas.common import MessageResponse

router = APIRouter(prefix="/current-affairs", tags=["Current Affairs"])


@router.get("")
async def list_current_affairs(
    search: Optional[str] = None,
    category: Optional[str] = None,
    subject: Optional[str] = None,
    days: int = Query(default=30, ge=1, le=365),
    prelims_only: bool = False,
    mains_only: bool = False,
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=20, ge=1, le=100),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """List current affairs with filtering and pagination."""
    service = CurrentAffairsService(db)
    return service.list(search, category, subject, days, prelims_only, mains_only, page, page_size)


@router.get("/categories", response_model=List[str])
async def get_categories(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Get all available categories."""
    service = CurrentAffairsService(db)
    return service.get_categories()


@router.get("/{affair_id}")
async def get_current_affair(
    affair_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Get a specific current affair with full details."""
    service = CurrentAffairsService(db)
    affair = service.get(affair_id)
    return service._to_dict(affair)


@router.post("", status_code=201)
async def create_current_affair(
    title: str = Body(...),
    summary: str = Body(...),
    content: Optional[str] = Body(default=None),
    source: Optional[str] = Body(default=None),
    source_url: Optional[str] = Body(default=None),
    published_date: Optional[date] = Body(default=None),
    category: Optional[str] = Body(default=None),
    tags: Optional[List[str]] = Body(default=[]),
    current_user: User = Depends(require_admin),
    db: Session = Depends(get_db),
):
    """Create a current affair entry with AI linkage (admin only)."""
    mentor = MentorService()
    ai_data = await mentor.link_current_affairs(title, summary)

    service = CurrentAffairsService(db)
    affair = service.create(
        title=title,
        summary=summary,
        content=content,
        source=source,
        source_url=source_url,
        published_date=published_date or date.today(),
        category=category,
        tags=tags or [],
        uploaded_by=current_user.id,
        ai_data=ai_data,
    )
    return {"id": str(affair.id), "message": "Current affair created with AI linkage"}


@router.post("/{affair_id}/link-topics")
async def relink_topics(
    affair_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Re-run AI topic linkage for a current affair."""
    service = CurrentAffairsService(db)
    affair = service.get(affair_id)

    mentor = MentorService()
    ai_data = await mentor.link_current_affairs(affair.title, affair.summary)
    updated = service.update_ai_linkage(affair_id, ai_data)
    return {"message": "Topics linked successfully", "data": service._to_dict(updated)}
