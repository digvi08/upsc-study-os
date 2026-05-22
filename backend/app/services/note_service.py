"""Notes service."""
from typing import List, Optional
from sqlalchemy.orm import Session
from sqlalchemy import or_
from fastapi import HTTPException, status
import uuid

from app.models.note import Note, NoteType
from app.models.user import User
from app.schemas.note import NoteCreate, NoteUpdate


class NoteService:
    def __init__(self, db: Session):
        self.db = db

    def create_note(self, user: User, data: NoteCreate) -> Note:
        note = Note(user_id=user.id, **data.model_dump())
        self.db.add(note)
        self.db.commit()
        self.db.refresh(note)
        return note

    def get_notes(
        self,
        user: User,
        topic_id: Optional[uuid.UUID] = None,
        subject_id: Optional[uuid.UUID] = None,
        note_type: Optional[str] = None,
        search: Optional[str] = None,
        pinned_only: bool = False,
        page: int = 1,
        page_size: int = 20,
    ) -> tuple[List[Note], int]:
        query = self.db.query(Note).filter(
            Note.user_id == user.id,
            Note.is_deleted == False,
        )
        if topic_id:
            query = query.filter(Note.topic_id == topic_id)
        if subject_id:
            query = query.filter(Note.subject_id == subject_id)
        if note_type:
            query = query.filter(Note.note_type == note_type)
        if pinned_only:
            query = query.filter(Note.is_pinned == True)
        if search:
            query = query.filter(
                or_(
                    Note.title.ilike(f"%{search}%"),
                    Note.content.ilike(f"%{search}%"),
                )
            )

        total = query.count()
        notes = query.order_by(Note.is_pinned.desc(), Note.updated_at.desc()) \
                     .offset((page - 1) * page_size) \
                     .limit(page_size) \
                     .all()
        return notes, total

    def get_note(self, user: User, note_id: uuid.UUID) -> Note:
        note = self.db.query(Note).filter(
            Note.id == note_id,
            Note.user_id == user.id,
            Note.is_deleted == False,
        ).first()
        if not note:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Note not found")
        return note

    def update_note(self, user: User, note_id: uuid.UUID, data: NoteUpdate) -> Note:
        note = self.get_note(user, note_id)
        for field, value in data.model_dump(exclude_unset=True).items():
            setattr(note, field, value)
        self.db.commit()
        self.db.refresh(note)
        return note

    def delete_note(self, user: User, note_id: uuid.UUID) -> None:
        note = self.get_note(user, note_id)
        note.is_deleted = True
        self.db.commit()

    def toggle_pin(self, user: User, note_id: uuid.UUID) -> Note:
        note = self.get_note(user, note_id)
        note.is_pinned = not note.is_pinned
        self.db.commit()
        self.db.refresh(note)
        return note

    def toggle_favorite(self, user: User, note_id: uuid.UUID) -> Note:
        note = self.get_note(user, note_id)
        note.is_favorite = not note.is_favorite
        self.db.commit()
        self.db.refresh(note)
        return note
