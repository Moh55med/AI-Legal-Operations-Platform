"""CRUD operations for deadlines"""

from sqlalchemy.orm import Session
from app.db.models import Deadline, DeadlineStatusEnum
from typing import List, Optional
from datetime import datetime


def create_deadline(
    db: Session,
    case_id: int,
    due_date: datetime,
    description: Optional[str] = None,
) -> Deadline:
    """Create a new deadline"""
    db_deadline = Deadline(
        case_id=case_id,
        due_date=due_date,
        description=description,
        status=DeadlineStatusEnum.PENDING,
    )
    db.add(db_deadline)
    db.commit()
    db.refresh(db_deadline)
    return db_deadline


def get_deadline(db: Session, deadline_id: int) -> Optional[Deadline]:
    """Get a deadline by ID"""
    return db.query(Deadline).filter(Deadline.id == deadline_id).first()


def get_deadlines_by_case(
    db: Session, case_id: int, skip: int = 0, limit: int = 100
) -> List[Deadline]:
    """Get all deadlines for a case"""
    return (
        db.query(Deadline)
        .filter(Deadline.case_id == case_id)
        .offset(skip)
        .limit(limit)
        .all()
    )


def get_all_deadlines(
    db: Session, skip: int = 0, limit: int = 100
) -> List[Deadline]:
    """Get all deadlines with pagination"""
    return db.query(Deadline).offset(skip).limit(limit).all()


def get_pending_deadlines(
    db: Session, skip: int = 0, limit: int = 100
) -> List[Deadline]:
    """Get all pending deadlines"""
    return (
        db.query(Deadline)
        .filter(Deadline.status == DeadlineStatusEnum.PENDING)
        .offset(skip)
        .limit(limit)
        .all()
    )


def update_deadline(
    db: Session,
    deadline_id: int,
    due_date: Optional[datetime] = None,
    description: Optional[str] = None,
    status: Optional[DeadlineStatusEnum] = None,
) -> Optional[Deadline]:
    """Update a deadline"""
    db_deadline = get_deadline(db, deadline_id)
    if db_deadline:
        if due_date is not None:
            db_deadline.due_date = due_date
        if description is not None:
            db_deadline.description = description
        if status is not None:
            db_deadline.status = status
        db_deadline.updated_at = datetime.utcnow()
        db.commit()
        db.refresh(db_deadline)
    return db_deadline


def mark_deadline_completed(
    db: Session, deadline_id: int
) -> Optional[Deadline]:
    """Mark a deadline as completed"""
    db_deadline = get_deadline(db, deadline_id)
    if db_deadline:
        db_deadline.status = DeadlineStatusEnum.COMPLETED
        db_deadline.updated_at = datetime.utcnow()
        db.commit()
        db.refresh(db_deadline)
    return db_deadline


def mark_deadline_missed(db: Session, deadline_id: int) -> Optional[Deadline]:
    """Mark a deadline as missed"""
    db_deadline = get_deadline(db, deadline_id)
    if db_deadline:
        db_deadline.status = DeadlineStatusEnum.MISSED
        db_deadline.updated_at = datetime.utcnow()
        db.commit()
        db.refresh(db_deadline)
    return db_deadline


def delete_deadline(db: Session, deadline_id: int) -> bool:
    """Delete a deadline"""
    db_deadline = get_deadline(db, deadline_id)
    if db_deadline:
        db.delete(db_deadline)
        db.commit()
        return True
    return False


def get_overdue_deadlines(db: Session) -> List[Deadline]:
    """Get all overdue deadlines (past due_date with PENDING status)"""
    now = datetime.utcnow()
    return (
        db.query(Deadline)
        .filter(
            Deadline.due_date < now,
            Deadline.status == DeadlineStatusEnum.PENDING,
        )
        .all()
    )


def filter_deadlines(
    db: Session,
    case_id: Optional[int] = None,
    status: Optional[DeadlineStatusEnum] = None,
    due_date: Optional[datetime] = None,
    due_date_from: Optional[datetime] = None,
    due_date_to: Optional[datetime] = None,
    skip: int = 0,
    limit: int = 100,
) -> List[Deadline]:
    """
    Advanced search and filtering for deadlines.
    
    Parameters:
    - case_id: Filter by case ID
    - status: Filter by deadline status (pending, completed, missed)
    - due_date: Filter deadlines on exact date
    - due_date_from: Filter deadlines on or after this date
    - due_date_to: Filter deadlines on or before this date
    """
    query = db.query(Deadline)
    
    if case_id is not None:
        query = query.filter(Deadline.case_id == case_id)
    
    if status is not None:
        query = query.filter(Deadline.status == status)
    
    if due_date is not None:
        # Convert to date only for comparison
        query = query.filter(Deadline.due_date.cast(db.func.date) == due_date.date())
    
    if due_date_from is not None:
        query = query.filter(Deadline.due_date >= due_date_from)
    
    if due_date_to is not None:
        query = query.filter(Deadline.due_date <= due_date_to)
    
    return query.offset(skip).limit(limit).all()
