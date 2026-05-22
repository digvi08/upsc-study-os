"""User profile routes."""
from fastapi import APIRouter, Depends, UploadFile, File
from sqlalchemy.orm import Session

from app.database import get_db
from app.auth.dependencies import get_current_user
from app.models.user import User
from app.schemas.user import UserResponse, UserUpdate
from app.schemas.common import MessageResponse

router = APIRouter(prefix="/users", tags=["Users"])


@router.get("/profile", response_model=UserResponse)
async def get_profile(current_user: User = Depends(get_current_user)):
    """Get current user profile."""
    return current_user


@router.put("/profile", response_model=UserResponse)
async def update_profile(
    data: UserUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Update user profile."""
    for field, value in data.model_dump(exclude_unset=True).items():
        setattr(current_user, field, value)
    db.commit()
    db.refresh(current_user)
    return current_user


@router.get("/dashboard-stats")
async def get_dashboard_stats(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Get dashboard statistics for the current user."""
    from app.models.subject import Subject, Topic, TopicStatus
    from app.models.note import Note
    from app.models.revision import RevisionHistory, RevisionStatus
    from app.models.study_plan import StudyTask, TaskStatus
    from app.models.analytics import UserAnalytics, DailyStudyLog
    from datetime import date, timedelta

    # Subject stats
    total_subjects = db.query(Subject).filter(
        Subject.user_id == current_user.id,
        Subject.is_deleted == False,
        Subject.is_active == True,
    ).count()

    total_topics = db.query(Topic).join(Subject).filter(
        Subject.user_id == current_user.id,
        Topic.is_deleted == False,
    ).count()

    completed_topics = db.query(Topic).join(Subject).filter(
        Subject.user_id == current_user.id,
        Topic.status == TopicStatus.COMPLETED,
        Topic.is_deleted == False,
    ).count()

    # Notes
    total_notes = db.query(Note).filter(
        Note.user_id == current_user.id,
        Note.is_deleted == False,
    ).count()

    # Pending revisions
    pending_revisions = db.query(RevisionHistory).filter(
        RevisionHistory.user_id == current_user.id,
        RevisionHistory.status == RevisionStatus.PENDING,
    ).count()

    # Today's tasks (scoped to current user's plans)
    from app.models.study_plan import StudyPlan
    today = date.today()
    today_tasks = db.query(StudyTask).join(StudyPlan).filter(
        StudyPlan.user_id == current_user.id,
        StudyTask.scheduled_date == today,
        StudyTask.is_deleted == False,
    ).count()

    today_completed = db.query(StudyTask).join(StudyPlan).filter(
        StudyPlan.user_id == current_user.id,
        StudyTask.scheduled_date == today,
        StudyTask.status == TaskStatus.COMPLETED,
        StudyTask.is_deleted == False,
    ).count()

    # Analytics
    analytics = db.query(UserAnalytics).filter(
        UserAnalytics.user_id == current_user.id
    ).first()

    # Recent study logs (last 7 days)
    week_ago = today - timedelta(days=7)
    recent_logs = db.query(DailyStudyLog).filter(
        DailyStudyLog.user_id == current_user.id,
        DailyStudyLog.date >= week_ago,
    ).order_by(DailyStudyLog.date.desc()).all()

    return {
        "subjects": {
            "total": total_subjects,
            "topics_total": total_topics,
            "topics_completed": completed_topics,
            "completion_percentage": round(completed_topics / total_topics * 100, 1) if total_topics > 0 else 0,
        },
        "notes": {"total": total_notes},
        "revisions": {"pending": pending_revisions},
        "today": {
            "tasks_total": today_tasks,
            "tasks_completed": today_completed,
            "completion_percentage": round(today_completed / today_tasks * 100, 1) if today_tasks > 0 else 0,
        },
        "streak": {
            "current": current_user.current_streak,
            "longest": current_user.longest_streak,
        },
        "analytics": {
            "total_study_hours": analytics.total_study_hours if analytics else 0,
            "total_revisions": analytics.total_revisions if analytics else 0,
            "weak_subjects": analytics.weak_subjects if analytics else [],
        },
        "recent_activity": [
            {
                "date": str(log.date),
                "study_hours": log.study_hours,
                "topics_studied": log.topics_studied,
                "productivity_score": log.productivity_score,
            }
            for log in recent_logs
        ],
    }
