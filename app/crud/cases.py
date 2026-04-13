"""CRUD operations for cases"""

from sqlalchemy.orm import Session
from app.db.models import Case, CaseStatusEnum
from datetime import datetime
from typing import List, Optional


def create_case(db: Session, title: str, description: Optional[str] = None) -> Case:
    """Create a new case"""
    db_case = Case(title=title, description=description, status=CaseStatusEnum.OPEN)
    db.add(db_case)
    db.commit()
    db.refresh(db_case)
    return db_case


def get_case(db: Session, case_id: int) -> Optional[Case]:
    """Get a case by ID"""
    return db.query(Case).filter(Case.id == case_id).first()


def get_all_cases(db: Session, skip: int = 0, limit: int = 100) -> List[Case]:
    """Get all cases with pagination"""
    return db.query(Case).offset(skip).limit(limit).all()


def update_case(
    db: Session,
    case_id: int,
    title: Optional[str] = None,
    description: Optional[str] = None,
    status: Optional[CaseStatusEnum] = None,
) -> Optional[Case]:
    """Update a case"""
    db_case = get_case(db, case_id)
    if db_case:
        if title is not None:
            db_case.title = title
        if description is not None:
            db_case.description = description
        if status is not None:
            db_case.status = status
            # Set closed_at if closing the case
            if status == CaseStatusEnum.CLOSED and db_case.closed_at is None:
                db_case.closed_at = datetime.utcnow()
        db_case.updated_at = datetime.utcnow()
        db.commit()
        db.refresh(db_case)
    return db_case


def close_case(db: Session, case_id: int) -> Optional[Case]:
    """Close a case"""
    db_case = get_case(db, case_id)
    if db_case:
        db_case.status = CaseStatusEnum.CLOSED
        db_case.closed_at = datetime.utcnow()
        db_case.updated_at = datetime.utcnow()
        db.commit()
        db.refresh(db_case)
    return db_case


def delete_case(db: Session, case_id: int) -> bool:
    """Delete a case"""
    db_case = get_case(db, case_id)
    if db_case:
        db.delete(db_case)
        db.commit()
        return True
    return False
