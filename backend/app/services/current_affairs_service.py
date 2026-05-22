"""Current Affairs service."""
from datetime import date, timedelta
from typing import List, Optional, Dict, Any
from sqlalchemy.orm import Session
from sqlalchemy import or_
from fastapi import HTTPException, status
import math
import uuid

from app.models.current_affairs import CurrentAffair
from app.models.user import User


class CurrentAffairsService:
    def __init__(self, db: Session):
        self.db = db

    def list(
        self,
        search: Optional[str] = None,
        category: Optional[str] = None,
        subject: Optional[str] = None,
        days: int = 30,
        prelims_only: bool = False,
        mains_only: bool = False,
        page: int = 1,
        page_size: int = 20,
    ) -> Dict[str, Any]:
        start_date = date.today() - timedelta(days=days)
        query = self.db.query(CurrentAffair).filter(
            CurrentAffair.published_date >= start_date,
            CurrentAffair.is_deleted == False,
        )

        if search:
            query = query.filter(
                or_(
                    CurrentAffair.title.ilike(f"%{search}%"),
                    CurrentAffair.summary.ilike(f"%{search}%"),
                    CurrentAffair.content.ilike(f"%{search}%"),
                )
            )
        if category:
            query = query.filter(CurrentAffair.category == category)
        if subject:
            query = query.filter(CurrentAffair.related_subjects.contains([subject]))
        if prelims_only:
            query = query.filter(CurrentAffair.prelims_relevant == True)
        if mains_only:
            query = query.filter(CurrentAffair.mains_relevant == True)

        total = query.count()
        affairs = (
            query.order_by(CurrentAffair.published_date.desc())
            .offset((page - 1) * page_size)
            .limit(page_size)
            .all()
        )

        return {
            "items": [self._to_dict(a) for a in affairs],
            "total": total,
            "page": page,
            "page_size": page_size,
            "total_pages": math.ceil(total / page_size),
            "has_next": page < math.ceil(total / page_size),
            "has_prev": page > 1,
        }

    def get(self, affair_id: uuid.UUID) -> CurrentAffair:
        affair = self.db.query(CurrentAffair).filter(
            CurrentAffair.id == affair_id,
            CurrentAffair.is_deleted == False,
        ).first()
        if not affair:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Current affair not found")
        return affair

    def create(
        self,
        title: str,
        summary: str,
        published_date: date,
        content: Optional[str] = None,
        source: Optional[str] = None,
        source_url: Optional[str] = None,
        category: Optional[str] = None,
        tags: Optional[List[str]] = None,
        uploaded_by: Optional[uuid.UUID] = None,
        ai_data: Optional[Dict[str, Any]] = None,
    ) -> CurrentAffair:
        affair = CurrentAffair(
            title=title,
            summary=summary,
            content=content,
            source=source,
            source_url=source_url,
            published_date=published_date,
            category=category,
            tags=tags or [],
            uploaded_by=uploaded_by,
            is_verified=True,
        )
        if ai_data:
            affair.related_subjects = ai_data.get("related_subjects", [])
            affair.related_topics = ai_data.get("related_topics", [])
            affair.ai_relevance_explanation = ai_data.get("ai_relevance_explanation")
            affair.upsc_relevance_score = ai_data.get("upsc_relevance_score")
            affair.prelims_relevant = ai_data.get("prelims_relevant", False)
            affair.mains_relevant = ai_data.get("mains_relevant", False)
            affair.mains_angles = ai_data.get("mains_angles", [])
            affair.keywords = ai_data.get("keywords", [])

        self.db.add(affair)
        self.db.commit()
        self.db.refresh(affair)
        return affair

    def update_ai_linkage(self, affair_id: uuid.UUID, ai_data: Dict[str, Any]) -> CurrentAffair:
        affair = self.db.query(CurrentAffair).filter(CurrentAffair.id == affair_id).first()
        if not affair:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Not found")
        affair.related_subjects = ai_data.get("related_subjects", affair.related_subjects)
        affair.related_topics = ai_data.get("related_topics", affair.related_topics)
        affair.ai_relevance_explanation = ai_data.get("ai_relevance_explanation")
        affair.mains_angles = ai_data.get("mains_angles", [])
        affair.keywords = ai_data.get("keywords", [])
        affair.prelims_relevant = ai_data.get("prelims_relevant", False)
        affair.mains_relevant = ai_data.get("mains_relevant", False)
        affair.upsc_relevance_score = ai_data.get("upsc_relevance_score")
        self.db.commit()
        self.db.refresh(affair)
        return affair

    def get_categories(self) -> List[str]:
        from sqlalchemy import distinct
        cats = self.db.query(distinct(CurrentAffair.category)).filter(
            CurrentAffair.category != None,
            CurrentAffair.is_deleted == False,
        ).all()
        return [c[0] for c in cats if c[0]]

    def _to_dict(self, a: CurrentAffair) -> Dict[str, Any]:
        return {
            "id": str(a.id),
            "title": a.title,
            "summary": a.summary,
            "category": a.category,
            "published_date": str(a.published_date),
            "source": a.source,
            "source_url": a.source_url,
            "related_subjects": a.related_subjects,
            "related_topics": a.related_topics,
            "ai_relevance_explanation": a.ai_relevance_explanation,
            "upsc_relevance_score": a.upsc_relevance_score,
            "prelims_relevant": a.prelims_relevant,
            "mains_relevant": a.mains_relevant,
            "mains_angles": a.mains_angles,
            "tags": a.tags,
            "keywords": a.keywords,
        }
