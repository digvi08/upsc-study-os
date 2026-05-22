"""PYQ routes."""
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from typing import Optional, List
import uuid
import math

from app.database import get_db
from app.auth.dependencies import get_current_user, require_admin
from app.models.user import User
from app.services.pyq_service import PYQService
from app.ai.mentor_service import MentorService
from app.schemas.pyq import PYQCreate, PYQResponse, PYQAnalysisRequest, PYQAnalysisResponse
from app.schemas.common import PaginatedResponse, MessageResponse

router = APIRouter(prefix="/pyq", tags=["PYQ Analyzer"])


@router.get("", response_model=PaginatedResponse[PYQResponse])
async def list_pyqs(
    topic: Optional[str] = None,
    subject: Optional[str] = None,
    year: Optional[int] = None,
    exam: Optional[str] = None,
    search: Optional[str] = None,
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=20, ge=1, le=100),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """List PYQs with filtering."""
    service = PYQService(db)
    pyqs, total = service.get_pyqs(topic, subject, year, exam, search, page, page_size)
    total_pages = math.ceil(total / page_size)
    return PaginatedResponse(
        items=[PYQResponse.model_validate(p) for p in pyqs],
        total=total,
        page=page,
        page_size=page_size,
        total_pages=total_pages,
        has_next=page < total_pages,
        has_prev=page > 1,
    )


@router.post("/analyze", response_model=dict)
async def analyze_topic(
    request: PYQAnalysisRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Analyze PYQs for a topic — core feature."""
    service = PYQService(db)
    analysis = service.analyze_topic(request)

    # Enhance with AI insights
    if analysis["total_questions"] > 0:
        mentor = MentorService()
        questions_text = [q.question for q in analysis["questions"][:10]]
        ai_insights = await mentor.analyze_pyq_with_ai(request.topic, questions_text)
        analysis["ai_insights"] = ai_insights
        # Remove ORM objects from response
        analysis["questions"] = [PYQResponse.model_validate(q) for q in analysis["questions"]]

    return analysis


@router.post("", response_model=PYQResponse, status_code=201)
async def create_pyq(
    data: PYQCreate,
    current_user: User = Depends(require_admin),
    db: Session = Depends(get_db),
):
    """Create a new PYQ (admin only)."""
    service = PYQService(db)
    return service.create_pyq(data, current_user.id)


@router.get("/years", response_model=List[int])
async def get_available_years(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Get list of years with PYQ data."""
    from app.models.pyq import PYQ
    from sqlalchemy import distinct
    years = db.query(distinct(PYQ.year)).filter(PYQ.is_deleted == False).order_by(PYQ.year.desc()).all()
    return [y[0] for y in years]


@router.get("/subjects", response_model=List[str])
async def get_pyq_subjects(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Get list of subjects with PYQ data."""
    from app.models.pyq import PYQ
    from sqlalchemy import distinct
    subjects = db.query(distinct(PYQ.subject)).filter(PYQ.is_deleted == False).all()
    return [s[0] for s in subjects]
