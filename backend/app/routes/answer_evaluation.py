"""Answer Evaluation routes with OCR support."""
from fastapi import APIRouter, Depends, UploadFile, File, Form, Query
from sqlalchemy.orm import Session
from typing import Optional
import uuid

from app.database import get_db
from app.auth.dependencies import get_current_user
from app.models.user import User
from app.services.answer_eval_service import AnswerEvalService
from app.ai.mentor_service import MentorService
from app.ai.ocr_service import OCRService

router = APIRouter(prefix="/answer-evaluation", tags=["Answer Evaluation"])


@router.post("/evaluate-text", response_model=dict)
async def evaluate_text_answer(
    question: str,
    answer: str,
    marks: int = Query(default=10, ge=5, le=25),
    topic_id: Optional[uuid.UUID] = None,
    exam_type: Optional[str] = None,
    time_taken_minutes: Optional[int] = None,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Evaluate a typed UPSC answer with AI."""
    mentor = MentorService()
    result = await mentor.evaluate_answer(question, answer, marks)

    service = AnswerEvalService(db)
    evaluation = service.save_evaluation(
        user=current_user,
        question=question,
        marks=marks,
        evaluation_result=result,
        answer_text=answer,
        topic_id=topic_id,
        exam_type=exam_type,
        time_taken_minutes=time_taken_minutes,
    )
    return {"evaluation_id": str(evaluation.id), "result": result}


@router.post("/evaluate-image", response_model=dict)
async def evaluate_image_answer(
    question: str = Form(...),
    marks: int = Form(default=10),
    image: UploadFile = File(...),
    topic_id: Optional[str] = Form(default=None),
    exam_type: Optional[str] = Form(default=None),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Evaluate a handwritten answer image using OCR + AI."""
    image_bytes = await image.read()

    ocr_service = OCRService()
    extracted_text = ocr_service.extract_text_from_image(image_bytes)

    if not extracted_text.strip():
        return {
            "error": "Could not extract text from image. Please ensure the image is clear and well-lit.",
            "ocr_text": "",
        }

    mentor = MentorService()
    result = await mentor.evaluate_answer(question, extracted_text, marks)

    service = AnswerEvalService(db)
    evaluation = service.save_evaluation(
        user=current_user,
        question=question,
        marks=marks,
        evaluation_result=result,
        answer_text=extracted_text,
        ocr_text=extracted_text,
        topic_id=uuid.UUID(topic_id) if topic_id else None,
        exam_type=exam_type,
    )
    return {
        "evaluation_id": str(evaluation.id),
        "ocr_text": extracted_text,
        "result": result,
    }


@router.get("/history", response_model=dict)
async def get_evaluation_history(
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=20, ge=1, le=50),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Get answer evaluation history."""
    service = AnswerEvalService(db)
    return service.get_history(current_user, page, page_size)


@router.get("/stats", response_model=dict)
async def get_performance_stats(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Get answer writing performance statistics."""
    service = AnswerEvalService(db)
    return service.get_performance_stats(current_user)


@router.get("/{eval_id}", response_model=dict)
async def get_evaluation(
    eval_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Get a specific evaluation with full details."""
    service = AnswerEvalService(db)
    ev = service.get_evaluation(current_user, eval_id)
    return {
        "id": str(ev.id),
        "question": ev.question,
        "answer_text": ev.answer_text,
        "ocr_extracted_text": ev.ocr_extracted_text,
        "total_marks": ev.total_marks,
        "obtained_marks": ev.obtained_marks,
        "percentage": ev.percentage,
        "structure_score": ev.structure_score,
        "content_score": ev.content_score,
        "keyword_score": ev.keyword_score,
        "analytical_score": ev.analytical_score,
        "grammar_score": ev.grammar_score,
        "examples_score": ev.examples_score,
        "overall_feedback": ev.overall_feedback,
        "strengths": ev.strengths,
        "improvements": ev.improvements,
        "suggested_answer": ev.suggested_answer,
        "word_count": ev.word_count,
        "exam_type": ev.exam_type,
        "created_at": ev.created_at.isoformat(),
    }
