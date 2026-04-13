"""
FastAPI endpoints for deadline management.
Handles deadline CRUD operations for cases.
"""

from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import List
from datetime import datetime
from app.db.session import get_db
from app.crud import deadlines as deadlines_crud
from app.schemas import DeadlineCreate, DeadlineUpdate, DeadlineResponse

router = APIRouter()


@router.post("/", response_model=DeadlineResponse, status_code=status.HTTP_201_CREATED)
def create_deadline(deadline: DeadlineCreate, db: Session = Depends(get_db)):
    """
    Create a new deadline for a case.
    
    **Parameters:**
    - **case_id**: Case ID (required)
    - **due_date**: Deadline due date (required, ISO format)
    - **description**: Deadline description (optional)
    
    **Returns:** Created deadline object
    """
    db_deadline = deadlines_crud.create_deadline(
        db,
        case_id=deadline.case_id,
        due_date=deadline.due_date,
        description=deadline.description,
    )
    return db_deadline


@router.get("/", response_model=List[DeadlineResponse])
def list_deadlines(
    case_id: int = Query(None),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=100),
    db: Session = Depends(get_db),
):
    """
    List all deadlines, optionally filtered by case.
    
    **Parameters:**
    - **case_id**: Filter by case ID (optional)
    - **skip**: Number of records to skip (default: 0)
    - **limit**: Number of records to return (default: 100)
    
    **Returns:** List of deadlines
    """
    if case_id:
        deadlines = deadlines_crud.get_deadlines_by_case(db, case_id, skip=skip, limit=limit)
    else:
        deadlines = deadlines_crud.get_all_deadlines(db, skip=skip, limit=limit)
    
    return deadlines


@router.get("/pending", response_model=List[DeadlineResponse])
def list_pending_deadlines(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=100),
    db: Session = Depends(get_db),
):
    """
    List all pending deadlines.
    
    **Parameters:**
    - **skip**: Number of records to skip (default: 0)
    - **limit**: Number of records to return (default: 100)
    
    **Returns:** List of pending deadlines
    """
    deadlines = deadlines_crud.get_pending_deadlines(db, skip=skip, limit=limit)
    return deadlines


@router.get("/overdue", response_model=List[DeadlineResponse])
def list_overdue_deadlines(db: Session = Depends(get_db)):
    """
    List all overdue deadlines (past due date with pending status).
    
    **Returns:** List of overdue deadlines
    """
    deadlines = deadlines_crud.get_overdue_deadlines(db)
    return deadlines


@router.get("/{deadline_id}", response_model=DeadlineResponse)
def get_deadline(deadline_id: int, db: Session = Depends(get_db)):
    """
    Get a specific deadline by ID.
    
    **Parameters:**
    - **deadline_id**: Deadline ID (required)
    
    **Returns:** Deadline object
    """
    db_deadline = deadlines_crud.get_deadline(db, deadline_id)
    if not db_deadline:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Deadline with ID {deadline_id} not found"
        )
    return db_deadline


@router.put("/{deadline_id}", response_model=DeadlineResponse)
def update_deadline(
    deadline_id: int,
    deadline_update: DeadlineUpdate,
    db: Session = Depends(get_db),
):
    """
    Update a deadline.
    
    **Parameters:**
    - **deadline_id**: Deadline ID (required)
    - **due_date**: Updated due date (optional)
    - **description**: Updated description (optional)
    - **status**: Updated status - 'pending', 'completed', 'missed' (optional)
    
    **Returns:** Updated deadline object
    """
    db_deadline = deadlines_crud.update_deadline(
        db,
        deadline_id,
        due_date=deadline_update.due_date,
        description=deadline_update.description,
        status=deadline_update.status,
    )
    if not db_deadline:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Deadline with ID {deadline_id} not found"
        )
    return db_deadline


@router.put("/{deadline_id}/complete", response_model=DeadlineResponse)
def mark_deadline_complete(deadline_id: int, db: Session = Depends(get_db)):
    """
    Mark a deadline as completed.
    
    **Parameters:**
    - **deadline_id**: Deadline ID (required)
    
    **Returns:** Updated deadline object with status 'completed'
    """
    db_deadline = deadlines_crud.mark_deadline_completed(db, deadline_id)
    if not db_deadline:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Deadline with ID {deadline_id} not found"
        )
    return db_deadline


@router.put("/{deadline_id}/miss", response_model=DeadlineResponse)
def mark_deadline_missed(deadline_id: int, db: Session = Depends(get_db)):
    """
    Mark a deadline as missed.
    
    **Parameters:**
    - **deadline_id**: Deadline ID (required)
    
    **Returns:** Updated deadline object with status 'missed'
    """
    db_deadline = deadlines_crud.mark_deadline_missed(db, deadline_id)
    if not db_deadline:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Deadline with ID {deadline_id} not found"
        )
    return db_deadline


@router.delete("/{deadline_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_deadline(deadline_id: int, db: Session = Depends(get_db)):
    """
    Delete a deadline.
    
    **Parameters:**
    - **deadline_id**: Deadline ID (required)
    
    **Returns:** No content
    """
    success = deadlines_crud.delete_deadline(db, deadline_id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Deadline with ID {deadline_id} not found"
        )
