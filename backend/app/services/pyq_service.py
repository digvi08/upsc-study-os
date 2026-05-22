"""PYQ service with analysis."""
from typing import List, Optional, Dict, Any
from sqlalchemy.orm import Session
from sqlalchemy import func, and_, or_
from fastapi import HTTPException, status
from collections import Counter
import uuid

from app.models.pyq import PYQ, ExamType
from app.schemas.pyq import PYQCreate, PYQAnalysisRequest, PYQAnalysisResponse


class PYQService:
    def __init__(self, db: Session):
        self.db = db

    def create_pyq(self, data: PYQCreate, uploaded_by: uuid.UUID) -> PYQ:
        pyq = PYQ(**data.model_dump(), uploaded_by=uploaded_by)
        self.db.add(pyq)
        self.db.commit()
        self.db.refresh(pyq)
        return pyq

    def get_pyqs(
        self,
        topic: Optional[str] = None,
        subject: Optional[str] = None,
        year: Optional[int] = None,
        exam: Optional[str] = None,
        search: Optional[str] = None,
        page: int = 1,
        page_size: int = 20,
    ) -> tuple[List[PYQ], int]:
        query = self.db.query(PYQ).filter(PYQ.is_deleted == False)

        if topic:
            query = query.filter(PYQ.topic.ilike(f"%{topic}%"))
        if subject:
            query = query.filter(PYQ.subject.ilike(f"%{subject}%"))
        if year:
            query = query.filter(PYQ.year == year)
        if exam:
            query = query.filter(PYQ.exam == exam)
        if search:
            query = query.filter(
                or_(
                    PYQ.question.ilike(f"%{search}%"),
                    PYQ.topic.ilike(f"%{search}%"),
                    PYQ.subject.ilike(f"%{search}%"),
                )
            )

        total = query.count()
        pyqs = query.order_by(PYQ.year.desc()) \
                    .offset((page - 1) * page_size) \
                    .limit(page_size) \
                    .all()
        return pyqs, total

    def analyze_topic(self, request: PYQAnalysisRequest) -> Dict[str, Any]:
        """Analyze PYQs for a given topic."""
        current_year = 2024
        start_year = current_year - request.years

        query = self.db.query(PYQ).filter(
            PYQ.topic.ilike(f"%{request.topic}%"),
            PYQ.year >= start_year,
            PYQ.is_deleted == False,
        )

        if request.subject:
            query = query.filter(PYQ.subject.ilike(f"%{request.subject}%"))
        if request.exam_type and request.exam_type != "both":
            query = query.filter(PYQ.exam == request.exam_type)

        pyqs = query.order_by(PYQ.year.desc()).all()

        if not pyqs:
            return {
                "topic": request.topic,
                "total_questions": 0,
                "year_wise_count": {},
                "exam_type_distribution": {},
                "recurring_keywords": [],
                "trend_analysis": "No PYQs found for this topic.",
                "probability_score": 0.0,
                "mains_angles": [],
                "prelims_insights": [],
                "questions": [],
                "ai_insights": "No data available for analysis.",
            }

        # Year-wise count
        year_wise = Counter(pyq.year for pyq in pyqs)

        # Exam type distribution
        exam_dist = Counter(pyq.exam.value for pyq in pyqs)

        # Keyword frequency
        all_keywords = []
        for pyq in pyqs:
            all_keywords.extend(pyq.keywords or [])
        keyword_freq = Counter(all_keywords).most_common(20)
        recurring_keywords = [{"keyword": k, "count": v} for k, v in keyword_freq]

        # Trend analysis
        recent_years = [y for y in year_wise.keys() if y >= current_year - 5]
        trend = "increasing" if len(recent_years) >= 3 else "stable" if len(recent_years) >= 1 else "decreasing"

        # Probability score (0-1) based on frequency and recency
        max_year = max(year_wise.keys()) if year_wise else 0
        recency_bonus = 0.2 if max_year >= current_year - 2 else 0.0
        frequency_score = min(len(pyqs) / 10, 0.8)
        probability_score = round(frequency_score + recency_bonus, 2)

        return {
            "topic": request.topic,
            "total_questions": len(pyqs),
            "year_wise_count": dict(sorted(year_wise.items())),
            "exam_type_distribution": dict(exam_dist),
            "recurring_keywords": recurring_keywords,
            "trend_analysis": f"Topic shows {trend} trend. Asked {len(pyqs)} times in last {request.years} years.",
            "probability_score": probability_score,
            "mains_angles": self._extract_mains_angles(pyqs),
            "prelims_insights": self._extract_prelims_insights(pyqs),
            "questions": pyqs,
            "ai_insights": f"This topic has been asked {len(pyqs)} times. Focus on {', '.join([k['keyword'] for k in recurring_keywords[:5]])}.",
        }

    def _extract_mains_angles(self, pyqs: List[PYQ]) -> List[str]:
        """Extract mains answer angles from questions."""
        mains_pyqs = [p for p in pyqs if p.exam == ExamType.MAINS]
        angles = []
        for pyq in mains_pyqs[:5]:
            if pyq.answer_structure:
                angles.extend(pyq.answer_structure.get("angles", []))
        return list(set(angles))[:10]

    def _extract_prelims_insights(self, pyqs: List[PYQ]) -> List[str]:
        """Extract prelims-specific insights."""
        prelims_pyqs = [p for p in pyqs if p.exam == ExamType.PRELIMS]
        insights = []
        if prelims_pyqs:
            insights.append(f"Asked {len(prelims_pyqs)} times in Prelims")
            years = sorted(set(p.year for p in prelims_pyqs), reverse=True)
            insights.append(f"Recent years: {', '.join(map(str, years[:5]))}")
        return insights
