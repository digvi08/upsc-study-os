"""Notes routes."""
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from typing import Optional, List
import uuid

from app.database import get_db
from app.auth.dependencies import get_current_user
from app.models.user import User
from app.services.note_service import NoteService
from app.ai.mentor_service import MentorService
from app.schemas.note import NoteCreate, NoteUpdate, NoteResponse, AIGenerateNoteRequest
from app.schemas.common import MessageResponse, PaginatedResponse
import math

router = APIRouter(prefix="/notes", tags=["Notes"])


@router.post("", response_model=NoteResponse, status_code=201)
async def create_note(
    data: NoteCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Create a new note."""
    service = NoteService(db)
    return service.create_note(current_user, data)


@router.get("", response_model=PaginatedResponse[NoteResponse])
async def list_notes(
    topic_id: Optional[uuid.UUID] = None,
    subject_id: Optional[uuid.UUID] = None,
    note_type: Optional[str] = None,
    search: Optional[str] = None,
    pinned_only: bool = False,
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=20, ge=1, le=100),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """List notes with filtering and pagination."""
    service = NoteService(db)
    notes, total = service.get_notes(
        current_user, topic_id, subject_id, note_type, search, pinned_only, page, page_size
    )
    total_pages = math.ceil(total / page_size)
    return PaginatedResponse(
        items=[NoteResponse.model_validate(n) for n in notes],
        total=total,
        page=page,
        page_size=page_size,
        total_pages=total_pages,
        has_next=page < total_pages,
        has_prev=page > 1,
    )


@router.get("/{note_id}", response_model=NoteResponse)
async def get_note(
    note_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Get a specific note."""
    service = NoteService(db)
    return service.get_note(current_user, note_id)


@router.put("/{note_id}", response_model=NoteResponse)
async def update_note(
    note_id: uuid.UUID,
    data: NoteUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Update a note."""
    service = NoteService(db)
    return service.update_note(current_user, note_id, data)


@router.delete("/{note_id}", response_model=MessageResponse)
async def delete_note(
    note_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Delete a note."""
    service = NoteService(db)
    service.delete_note(current_user, note_id)
    return MessageResponse(message="Note deleted successfully")


@router.post("/{note_id}/pin", response_model=NoteResponse)
async def toggle_pin(
    note_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Toggle pin status of a note."""
    service = NoteService(db)
    return service.toggle_pin(current_user, note_id)


@router.post("/{note_id}/favorite", response_model=NoteResponse)
async def toggle_favorite(
    note_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Toggle favorite status of a note."""
    service = NoteService(db)
    return service.toggle_favorite(current_user, note_id)


@router.post("/{note_id}/ai-summary", response_model=dict)
async def generate_ai_summary(
    note_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Generate AI summary for a note."""
    note_service = NoteService(db)
    note = note_service.get_note(current_user, note_id)

    mentor = MentorService()
    summary = await mentor.generate_note_summary(note.content, note.title)

    # Save summary to note
    note.ai_summary = summary
    db.commit()

    return {"summary": summary}


@router.post("/{note_id}/flashcards", response_model=dict)
async def generate_flashcards(
    note_id: uuid.UUID,
    count: int = Query(default=10, ge=5, le=30),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Generate AI flashcards from a note."""
    note_service = NoteService(db)
    note = note_service.get_note(current_user, note_id)

    mentor = MentorService()
    flashcards = await mentor.generate_flashcards(note.content, note.title, count)

    # Save flashcards to note
    note.flashcards = flashcards
    db.commit()

    return {"flashcards": flashcards}


@router.post("/ai-generate", response_model=NoteResponse, status_code=201)
async def ai_generate_note(
    data: AIGenerateNoteRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Generate a complete AI note on a topic."""
    from app.schemas.common import AIQueryRequest
    from app.schemas.note import NoteCreate

    mentor = MentorService()
    request = AIQueryRequest(
        query=f"Create comprehensive {data.note_type} notes on: {data.topic}",
        mode="mains",
        subject=data.subject,
        topic=data.topic,
    )
    content = await mentor.get_response(request)

    note_data = NoteCreate(
        title=f"AI Notes: {data.topic}",
        content=content,
        note_type="ai_generated",
        tags=[data.topic, data.subject or "", data.note_type],
    )
    note_service = NoteService(db)
    return note_service.create_note(current_user, note_data)
