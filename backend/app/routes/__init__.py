from fastapi import APIRouter
from .auth import router as auth_router
from .users import router as users_router
from .subjects import router as subjects_router
from .notes import router as notes_router
from .pyq import router as pyq_router
from .ai_mentor import router as ai_mentor_router
from .revision import router as revision_router
from .planner import router as planner_router
from .answer_evaluation import router as answer_eval_router
from .analytics import router as analytics_router
from .current_affairs import router as current_affairs_router
from .admin import router as admin_router

api_router = APIRouter(prefix="/api/v1")

api_router.include_router(auth_router)
api_router.include_router(users_router)
api_router.include_router(subjects_router)
api_router.include_router(notes_router)
api_router.include_router(pyq_router)
api_router.include_router(ai_mentor_router)
api_router.include_router(revision_router)
api_router.include_router(planner_router)
api_router.include_router(answer_eval_router)
api_router.include_router(analytics_router)
api_router.include_router(current_affairs_router)
api_router.include_router(admin_router)

__all__ = ["api_router"]
