"""AI Mentor routes with streaming support."""
from fastapi import APIRouter, Depends
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session
from typing import List, Optional
import json

from app.database import get_db
from app.auth.dependencies import get_current_user
from app.models.user import User
from app.ai.mentor_service import MentorService
from app.schemas.common import AIQueryRequest, AIQueryResponse, MessageResponse

router = APIRouter(prefix="/ai-mentor", tags=["AI Mentor"])


@router.post("/chat", response_model=AIQueryResponse)
async def chat(
    request: AIQueryRequest,
    history: Optional[List[dict]] = None,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Chat with the AI mentor."""
    mentor = MentorService()
    response = await mentor.get_response(request, history)

    # Update AI usage analytics
    from app.models.analytics import UserAnalytics
    analytics = db.query(UserAnalytics).filter(
        UserAnalytics.user_id == current_user.id
    ).first()
    if analytics:
        analytics.total_ai_queries += 1
        db.commit()

    return AIQueryResponse(response=response)


@router.post("/chat/stream")
async def chat_stream(
    request: AIQueryRequest,
    history: Optional[List[dict]] = None,
    current_user: User = Depends(get_current_user),
):
    """Stream AI mentor response (Server-Sent Events)."""
    mentor = MentorService()

    async def generate():
        async for chunk in mentor.stream_response(request, history):
            yield f"data: {json.dumps({'content': chunk})}\n\n"
        yield "data: [DONE]\n\n"

    return StreamingResponse(
        generate(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "X-Accel-Buffering": "no",
        },
    )


@router.post("/explain")
async def explain_topic(
    topic: str,
    subject: Optional[str] = None,
    mode: str = "mains",
    current_user: User = Depends(get_current_user),
):
    """Get a structured explanation of a topic."""
    mentor = MentorService()
    request = AIQueryRequest(
        query=f"Explain {topic} in detail for UPSC preparation",
        mode=mode,
        subject=subject,
        topic=topic,
    )
    response = await mentor.get_response(request)
    return {"topic": topic, "explanation": response, "mode": mode}


@router.post("/compare")
async def compare_concepts(
    concept1: str,
    concept2: str,
    current_user: User = Depends(get_current_user),
):
    """Compare two UPSC concepts."""
    mentor = MentorService()
    request = AIQueryRequest(
        query=f"Compare and contrast {concept1} vs {concept2} for UPSC. Include similarities, differences, and UPSC relevance.",
        mode="mains",
    )
    response = await mentor.get_response(request)
    return {"concept1": concept1, "concept2": concept2, "comparison": response}


@router.post("/answer-structure")
async def get_answer_structure(
    question: str,
    marks: int = 10,
    current_user: User = Depends(get_current_user),
):
    """Get suggested answer structure for a UPSC question."""
    mentor = MentorService()
    request = AIQueryRequest(
        query=f"Provide a detailed answer structure and key points for this {marks}-mark UPSC question: {question}",
        mode="mains",
    )
    response = await mentor.get_response(request)
    return {"question": question, "marks": marks, "structure": response}


@router.post("/current-affairs-link")
async def link_with_current_affairs(
    topic: str,
    current_user: User = Depends(get_current_user),
):
    """Link a static topic with relevant current affairs."""
    mentor = MentorService()
    request = AIQueryRequest(
        query=f"Link the static UPSC topic '{topic}' with recent current affairs (2023-2024). Provide specific examples and how they relate.",
        mode="mains",
        topic=topic,
    )
    response = await mentor.get_response(request)
    return {"topic": topic, "current_affairs_linkage": response}
