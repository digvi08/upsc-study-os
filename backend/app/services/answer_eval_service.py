"""Answer Evaluation service."""
from typing import Optional, Dict, Any, List
from sqlalchemy.orm import Session
from fastapi import HTTPException, status
import uuid

from app.models.answer_evaluation import AnswerEvaluation, EvaluationStatus
from app.models.user import User


class AnswerEvalService:
    def __init__(self, db: Session):
        self.db = db

    def save_evaluation(
        self,
        user: User,
        question: str,
        marks: int,
        evaluation_result: Dict[str, Any],
        answer_text: Optional[str] = None,
        answer_image_url: Optional[str] = None,
        ocr_text: Optional[str] = None,
        topic_id: Optional[uuid.UUID] = None,
        exam_type: Optional[str] = None,
        time_taken_minutes: Optional[int] = None,
    ) -> AnswerEvaluation:
        obtained = evaluation_result.get("obtained_marks", 0) or 0
        pct = round(obtained / marks * 100, 1) if marks > 0 else 0

        evaluation = AnswerEvaluation(
            user_id=user.id,
            topic_id=topic_id,
            question=question,
            answer_text=answer_text,
            answer_image_url=answer_image_url,
            ocr_extracted_text=ocr_text,
            status=EvaluationStatus.COMPLETED,
            total_marks=marks,
            obtained_marks=obtained,
            percentage=pct,
            structure_score=evaluation_result.get("structure_score"),
            content_score=evaluation_result.get("content_score"),
            keyword_score=evaluation_result.get("keyword_score"),
            analytical_score=evaluation_result.get("analytical_score"),
            grammar_score=evaluation_result.get("grammar_score"),
            examples_score=evaluation_result.get("examples_score"),
            overall_feedback=evaluation_result.get("overall_feedback"),
            strengths=evaluation_result.get("strengths", []),
            improvements=evaluation_result.get("improvements", []),
            suggested_answer=evaluation_result.get("suggested_answer"),
            word_count=evaluation_result.get("word_count"),
            detailed_feedback=evaluation_result,
            exam_type=exam_type,
            time_taken_minutes=time_taken_minutes,
        )
        self.db.add(evaluation)

        # Update analytics
        from app.models.analytics import UserAnalytics
        analytics = self.db.query(UserAnalytics).filter(
            UserAnalytics.user_id == user.id
        ).first()
        if analytics:
            analytics.total_answers_evaluated += 1

        self.db.commit()
        self.db.refresh(evaluation)
        return evaluation

    def get_history(
        self,
        user: User,
        page: int = 1,
        page_size: int = 20,
    ) -> Dict[str, Any]:
        import math
        query = self.db.query(AnswerEvaluation).filter(
            AnswerEvaluation.user_id == user.id,
            AnswerEvaluation.is_deleted == False,
        )
        total = query.count()
        evaluations = (
            query.order_by(AnswerEvaluation.created_at.desc())
            .offset((page - 1) * page_size)
            .limit(page_size)
            .all()
        )
        return {
            "items": [self._to_dict(e) for e in evaluations],
            "total": total,
            "page": page,
            "page_size": page_size,
            "total_pages": math.ceil(total / page_size),
        }

    def get_evaluation(self, user: User, eval_id: uuid.UUID) -> AnswerEvaluation:
        ev = self.db.query(AnswerEvaluation).filter(
            AnswerEvaluation.id == eval_id,
            AnswerEvaluation.user_id == user.id,
            AnswerEvaluation.is_deleted == False,
        ).first()
        if not ev:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Evaluation not found")
        return ev

    def get_performance_stats(self, user: User) -> Dict[str, Any]:
        evaluations = self.db.query(AnswerEvaluation).filter(
            AnswerEvaluation.user_id == user.id,
            AnswerEvaluation.status == EvaluationStatus.COMPLETED,
            AnswerEvaluation.is_deleted == False,
        ).all()

        if not evaluations:
            return {"total": 0, "avg_percentage": 0, "best_score": 0, "recent_trend": []}

        percentages = [e.percentage for e in evaluations if e.percentage is not None]
        return {
            "total": len(evaluations),
            "avg_percentage": round(sum(percentages) / len(percentages), 1) if percentages else 0,
            "best_score": max(percentages) if percentages else 0,
            "recent_trend": [
                {"date": str(e.created_at.date()), "percentage": e.percentage}
                for e in evaluations[-10:]
            ],
        }

    @staticmethod
    def _to_dict(e: AnswerEvaluation) -> Dict[str, Any]:
        return {
            "id": str(e.id),
            "question": e.question[:120] + "..." if len(e.question) > 120 else e.question,
            "total_marks": e.total_marks,
            "obtained_marks": e.obtained_marks,
            "percentage": e.percentage,
            "overall_feedback": e.overall_feedback,
            "strengths": e.strengths,
            "improvements": e.improvements,
            "exam_type": e.exam_type,
            "created_at": e.created_at.isoformat(),
        }
