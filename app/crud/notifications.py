"""CRUD operations for notifications"""

from sqlalchemy.orm import Session
from app.db.models import Notification
from typing import List, Optional
from datetime import datetime


def create_notification(
    db: Session,
    user_id: int,
    deadline_id: int,
    status: str = "unread",
) -> Notification:
    """Create a new notification"""
    db_notification = Notification(
        user_id=user_id,
        deadline_id=deadline_id,
        status=status,
    )
    db.add(db_notification)
    db.commit()
    db.refresh(db_notification)
    return db_notification


def get_notification(db: Session, notification_id: int) -> Optional[Notification]:
    """Get a notification by ID"""
    return db.query(Notification).filter(Notification.id == notification_id).first()


def get_user_notifications(
    db: Session,
    user_id: int,
    status: Optional[str] = None,
    skip: int = 0,
    limit: int = 100,
) -> List[Notification]:
    """Get notifications for a user, optionally filtered by status"""
    query = db.query(Notification).filter(Notification.user_id == user_id)
    
    if status:
        query = query.filter(Notification.status == status)
    
    return query.offset(skip).limit(limit).all()


def mark_notification_read(db: Session, notification_id: int) -> Optional[Notification]:
    """Mark a notification as read"""
    db_notification = get_notification(db, notification_id)
    if db_notification:
        db_notification.status = "read"
        db_notification.read_at = datetime.utcnow()
        db.commit()
        db.refresh(db_notification)
    return db_notification


def mark_notification_dismissed(
    db: Session, notification_id: int
) -> Optional[Notification]:
    """Mark a notification as dismissed"""
    db_notification = get_notification(db, notification_id)
    if db_notification:
        db_notification.status = "dismissed"
        db.commit()
        db.refresh(db_notification)
    return db_notification


def delete_notification(db: Session, notification_id: int) -> bool:
    """Delete a notification"""
    db_notification = get_notification(db, notification_id)
    if db_notification:
        db.delete(db_notification)
        db.commit()
        return True
    return False


def delete_notifications_by_deadline(
    db: Session, deadline_id: int
) -> int:
    """Delete all notifications for a deadline"""
    count = db.query(Notification).filter(
        Notification.deadline_id == deadline_id
    ).delete()
    db.commit()
    return count
