"""Revision service — spaced repetition scheduling."""
from datetime import datetime, timedelta
from typing import List, Optional, Dict, Any
from sqlalchemy.orm import Session
from sqlalchemy import and_
from fastapi import HTTPException, status
import uuid

from app.models.revision import RevisionHistory, RevisionStatus
from app.models.subject import Topic
from app.models.user import User

# SM-2 spaced repetition intervals (days)
REVISION_INTERVALS = [1, 3, 7, 15, 30]


def _next_interval(revision_number: int, ease_factor: float = 2.5) -> int:
    """Return interval in days for the given revision number."""
    if revision_number <= len(REVISION_INTERVALS):
        return REVISION_INTERVALS[revision_number - 1]
    return int(REVISION_INTERVALS[-1] * ease_factor)


class RevisionService:
    def __init__(self, db: Session):
        self.db = db

    # ── Scheduling ────────────────────────────────────────────────────────────

    def schedule_topic(self, user: User, topic_id: uuid.UUID) -> List[Dict[str, Any]]:
        """Schedule all 5 spaced-repetition revisions for a topic."""
        topic = self.db.query(Topic).filter(
            Topic.id == topic_id,
            Topic.is_deleted == False,
        ).first()
        if not topic:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Topic not found")

        existing_count = self.db.query(RevisionHistory).filter(
            RevisionHistory.user_id == user.id,
            RevisionHistory.topic_id == topic_id,
        ).count()

        scheduled = []
        base_date = datetime.utcnow()

        for i in range(1, 6):
            rev_num = existing_count + i
            interval = _next_interval(rev_num)
            sched_date = base_date + timedelta(days=interval)

            revision = RevisionHistory(
                user_id=user.id,
                topic_id=topic_id,
                revision_number=rev_num,
                scheduled_date=sched_date,
                interval_days=interval,
            )
            self.db.add(revision)
            scheduled.append({
                "revision_number": rev_num,
                "scheduled_date": sched_date.isoformat(),
                "interval_days": interval,
            })

        self.db.commit()
        return scheduled

    def get_pending(self, user: User) -> List[Dict[str, Any]]:
        """Get all pending/overdue revisions for the user."""
        now = datetime.utcnow()
        revisions = (
            self.db.query(RevisionHistory)
            .filter(
                RevisionHistory.user_id == user.id,
                RevisionHistory.status == RevisionStatus.PENDING,
                RevisionHistory.scheduled_date <= now,
                RevisionHistory.is_deleted == False,
            )
            .order_by(RevisionHistory.scheduled_date)
            .all()
        )

        result = []
        for rev in revisions:
            topic = self.db.query(Topic).filter(Topic.id == rev.topic_id).first()
            result.append({
                "id": str(rev.id),
                "topic_id": str(rev.topic_id),
                "topic_name": topic.name if topic else "Unknown",
                "subject_id": str(topic.subject_id) if topic else None,
                "revision_number": rev.revision_number,
                "scheduled_date": rev.scheduled_date.isoformat(),
                "is_overdue": rev.scheduled_date < now,
                "status": rev.status.value,
                "confidence_before": rev.confidence_before,
            })
        return result

    def get_upcoming(self, user: User, days: int = 30) -> List[Dict[str, Any]]:
        """Get upcoming revisions grouped by date."""
        now = datetime.utcnow()
        end = now + timedelta(days=days)

        revisions = (
            self.db.query(RevisionHistory)
            .filter(
                RevisionHistory.user_id == user.id,
                RevisionHistory.scheduled_date > now,
                RevisionHistory.scheduled_date <= end,
                RevisionHistory.status == RevisionStatus.PENDING,
                RevisionHistory.is_deleted == False,
            )
            .order_by(RevisionHistory.scheduled_date)
            .all()
        )

        calendar: Dict[str, list] = {}
        for rev in revisions:
            topic = self.db.query(Topic).filter(Topic.id == rev.topic_id).first()
            date_key = rev.scheduled_date.strftime("%Y-%m-%d")
            if date_key not in calendar:
                calendar[date_key] = []
            calendar[date_key].append({
                "id": str(rev.id),
                "topic_id": str(rev.topic_id),
                "topic_name": topic.name if topic else "Unknown",
                "revision_number": rev.revision_number,
            })

        return [{"date": k, "revisions": v} for k, v in sorted(calendar.items())]

    def complete_revision(
        self,
        user: User,
        revision_id: uuid.UUID,
        confidence_after: int,
        time_spent_minutes: int,
        notes: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Mark a revision complete and schedule the next one."""
        revision = self.db.query(RevisionHistory).filter(
            RevisionHistory.id == revision_id,
            RevisionHistory.user_id == user.id,
        ).first()
        if not revision:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Revision not found")

        revision.status = RevisionStatus.COMPLETED
        revision.completed_date = datetime.utcnow()
        revision.confidence_after = confidence_after
        revision.time_spent_minutes = time_spent_minutes
        if notes:
            revision.notes = notes

        # Adjust ease factor (SM-2)
        if confidence_after >= 80:
            revision.ease_factor = min(revision.ease_factor + 0.1, 3.0)
        elif confidence_after < 50:
            revision.ease_factor = max(revision.ease_factor - 0.2, 1.3)

        # Schedule next revision if not at max
        next_rev_data = None
        if revision.revision_number < 5:
            next_interval = _next_interval(revision.revision_number + 1, revision.ease_factor)
            next_date = datetime.utcnow() + timedelta(days=next_interval)
            next_rev = RevisionHistory(
                user_id=user.id,
                topic_id=revision.topic_id,
                revision_number=revision.revision_number + 1,
                scheduled_date=next_date,
                interval_days=next_interval,
                ease_factor=revision.ease_factor,
                confidence_before=confidence_after,
            )
            self.db.add(next_rev)
            next_rev_data = {
                "revision_number": next_rev.revision_number,
                "scheduled_date": next_date.isoformat(),
                "interval_days": next_interval,
            }

        # Update topic stats
        topic = self.db.query(Topic).filter(Topic.id == revision.topic_id).first()
        if topic:
            topic.revision_count += 1
            topic.confidence_level = confidence_after

        # Update analytics
        from app.models.analytics import UserAnalytics
        analytics = self.db.query(UserAnalytics).filter(
            UserAnalytics.user_id == user.id
        ).first()
        if analytics:
            analytics.total_revisions += 1

        self.db.commit()
        return {
            "message": "Revision completed",
            "next_revision": next_rev_data,
        }

    def skip_revision(self, user: User, revision_id: uuid.UUID) -> Dict[str, Any]:
        """Skip a revision and reschedule it for tomorrow."""
        revision = self.db.query(RevisionHistory).filter(
            RevisionHistory.id == revision_id,
            RevisionHistory.user_id == user.id,
        ).first()
        if not revision:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Revision not found")

        revision.status = RevisionStatus.SKIPPED
        revision.scheduled_date = datetime.utcnow() + timedelta(days=1)
        revision.status = RevisionStatus.PENDING  # reschedule
        self.db.commit()
        return {"message": "Revision rescheduled to tomorrow"}

    def get_stats(self, user: User) -> Dict[str, Any]:
        """Get revision statistics for the user."""
        total = self.db.query(RevisionHistory).filter(
            RevisionHistory.user_id == user.id,
            RevisionHistory.is_deleted == False,
        ).count()
        completed = self.db.query(RevisionHistory).filter(
            RevisionHistory.user_id == user.id,
            RevisionHistory.status == RevisionStatus.COMPLETED,
        ).count()
        pending = self.db.query(RevisionHistory).filter(
            RevisionHistory.user_id == user.id,
            RevisionHistory.status == RevisionStatus.PENDING,
            RevisionHistory.scheduled_date <= datetime.utcnow(),
        ).count()
        return {
            "total_scheduled": total,
            "completed": completed,
            "pending_today": pending,
            "completion_rate": round(completed / total * 100, 1) if total > 0 else 0,
        }
