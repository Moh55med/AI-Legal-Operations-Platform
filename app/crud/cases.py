"""CRUD operations for cases"""

from sqlalchemy.orm import Session
from sqlalchemy import and_, or_
from app.db.models import Case, CaseStatusEnum, Client, Watcher
from datetime import datetime
from typing import List, Optional


def create_case(
    db: Session,
    title: str,
    case_reference_number: str,
    client_id: int,
    description: Optional[str] = None,
) -> Case:
    """Create a new case"""
    db_case = Case(
        title=title,
        case_reference_number=case_reference_number,
        client_id=client_id,
        description=description,
        status=CaseStatusEnum.OPEN,
    )
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


def filter_cases(
    db: Session,
    status: Optional[CaseStatusEnum] = None,
    client_name: Optional[str] = None,
    assigned_user_id: Optional[int] = None,
    date_from: Optional[datetime] = None,
    date_to: Optional[datetime] = None,
    title: Optional[str] = None,
    case_reference_number: Optional[str] = None,
    skip: int = 0,
    limit: int = 100,
) -> List[Case]:
    """
    Advanced search and filtering for cases with multiple criteria.
    
    Parameters:
    - status: Filter by case status (open, closed, on_hold)
    - client_name: Search by client first or last name
    - assigned_user_id: Filter by assigned user
    - date_from: Filter cases created after this date
    - date_to: Filter cases created before this date
    - title: Search in case title
    - case_reference_number: Search by case reference number
    """
    query = db.query(Case)
    
    # Status filter
    if status is not None:
        query = query.filter(Case.status == status)
    
    # Title filter
    if title is not None:
        query = query.filter(Case.title.ilike(f"%{title}%"))
    
    # Case reference number filter
    if case_reference_number is not None:
        query = query.filter(Case.case_reference_number.ilike(f"%{case_reference_number}%"))
    
    # Client name filter (join with Client table)
    if client_name is not None:
        query = query.join(Client).filter(
            or_(
                Client.first_name.ilike(f"%{client_name}%"),
                Client.last_name.ilike(f"%{client_name}%"),
            )
        )
    
    # Assigned user filter (join with Watcher table)
    if assigned_user_id is not None:
        query = query.join(Watcher).filter(Watcher.user_id == assigned_user_id)
    
    # Date range filters
    if date_from is not None:
        query = query.filter(Case.created_at >= date_from)
    
    if date_to is not None:
        query = query.filter(Case.created_at <= date_to)
    
    return query.offset(skip).limit(limit).all()


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
