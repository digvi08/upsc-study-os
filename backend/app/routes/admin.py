"""Admin panel routes."""
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from typing import Optional
from datetime import date, timedelta

from app.database import get_db
from app.auth.dependencies import require_admin
from app.models.user import User
from app.models.analytics import UserAnalytics, DailyStudyLog
from app.schemas.common import MessageResponse

router = APIRouter(prefix="/admin", tags=["Admin Panel"])


@router.get("/stats")
async def get_admin_stats(
    admin: User = Depends(require_admin),
    db: Session = Depends(get_db),
):
    """Get platform-wide statistics."""
    from app.models.user import User as UserModel
    from app.models.pyq import PYQ
    from app.models.note import Note
    from app.models.current_affairs import CurrentAffair

    total_users = db.query(UserModel).filter(UserModel.is_deleted == False).count()
    active_users = db.query(UserModel).filter(
        UserModel.is_active == True,
        UserModel.is_deleted == False,
    ).count()
    total_pyqs = db.query(PYQ).filter(PYQ.is_deleted == False).count()
    total_notes = db.query(Note).filter(Note.is_deleted == False).count()
    total_affairs = db.query(CurrentAffair).filter(CurrentAffair.is_deleted == False).count()

    # Recent signups (last 7 days)
    week_ago = date.today() - timedelta(days=7)
    recent_signups = db.query(UserModel).filter(
        UserModel.created_at >= week_ago,
        UserModel.is_deleted == False,
    ).count()

    return {
        "users": {
            "total": total_users,
            "active": active_users,
            "recent_signups": recent_signups,
        },
        "content": {
            "total_pyqs": total_pyqs,
            "total_notes": total_notes,
            "total_current_affairs": total_affairs,
        },
    }


@router.get("/users")
async def list_users(
    search: Optional[str] = None,
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=20, ge=1, le=100),
    admin: User = Depends(require_admin),
    db: Session = Depends(get_db),
):
    """List all users (admin only)."""
    from app.models.user import User as UserModel
    query = db.query(UserModel).filter(UserModel.is_deleted == False)
    if search:
        query = query.filter(
            UserModel.email.ilike(f"%{search}%") |
            UserModel.username.ilike(f"%{search}%") |
            UserModel.full_name.ilike(f"%{search}%")
        )

    total = query.count()
    users = query.order_by(UserModel.created_at.desc()) \
                 .offset((page - 1) * page_size) \
                 .limit(page_size) \
                 .all()

    return {
        "users": [
            {
                "id": str(u.id),
                "email": u.email,
                "username": u.username,
                "full_name": u.full_name,
                "role": u.role.value,
                "is_active": u.is_active,
                "exam_target": u.exam_target.value,
                "created_at": u.created_at.isoformat(),
            }
            for u in users
        ],
        "total": total,
        "page": page,
        "page_size": page_size,
    }


@router.put("/users/{user_id}/toggle-active", response_model=MessageResponse)
async def toggle_user_active(
    user_id: str,
    admin: User = Depends(require_admin),
    db: Session = Depends(get_db),
):
    """Activate or deactivate a user."""
    import uuid
    from app.models.user import User as UserModel
    user = db.query(UserModel).filter(UserModel.id == uuid.UUID(user_id)).first()
    if not user:
        from fastapi import HTTPException
        raise HTTPException(status_code=404, detail="User not found")

    user.is_active = not user.is_active
    db.commit()
    status = "activated" if user.is_active else "deactivated"
    return MessageResponse(message=f"User {status} successfully")
