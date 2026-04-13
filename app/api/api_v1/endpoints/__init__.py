"""
FastAPI endpoints for case management.
Provides CRUD operations for legal cases.
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from app.db.session import get_db
from app.crud import cases as cases_crud
from app.schemas import CaseCreate, CaseUpdate, CaseResponse

router = APIRouter()


@router.post("/", response_model=CaseResponse, status_code=status.HTTP_201_CREATED)
def create_case(case: CaseCreate, db: Session = Depends(get_db)):
    """
    Create a new case.
    
    **Parameters:**
    - **title**: Case title (required)
    - **description**: Case description (optional)
    
    **Returns:** Created case object with ID
    """
    db_case = cases_crud.create_case(db, title=case.title, description=case.description)
    return db_case


@router.get("/", response_model=List[CaseResponse])
def list_cases(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    """
    List all cases with pagination.
    
    **Parameters:**
    - **skip**: Number of records to skip (default: 0)
    - **limit**: Number of records to return (default: 100, max: 100)
    
    **Returns:** List of cases
    """
    if limit > 100:
        limit = 100
    cases = cases_crud.get_all_cases(db, skip=skip, limit=limit)
    return cases


@router.get("/{case_id}", response_model=CaseResponse)
def get_case(case_id: int, db: Session = Depends(get_db)):
    """
    Get a specific case by ID.
    
    **Parameters:**
    - **case_id**: Case ID (required)
    
    **Returns:** Case object
    """
    db_case = cases_crud.get_case(db, case_id)
    if not db_case:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Case with ID {case_id} not found"
        )
    return db_case


@router.put("/{case_id}", response_model=CaseResponse)
def update_case(case_id: int, case_update: CaseUpdate, db: Session = Depends(get_db)):
    """
    Update a case.
    
    **Parameters:**
    - **case_id**: Case ID (required)
    - **title**: Updated case title (optional)
    - **description**: Updated case description (optional)
    - **status**: Updated case status - 'open', 'closed', 'on_hold' (optional)
    
    **Returns:** Updated case object
    """
    db_case = cases_crud.update_case(
        db,
        case_id,
        title=case_update.title,
        description=case_update.description,
        status=case_update.status,
    )
    if not db_case:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Case with ID {case_id} not found"
        )
    return db_case


@router.put("/{case_id}/close", response_model=CaseResponse)
def close_case(case_id: int, db: Session = Depends(get_db)):
    """
    Close a case.
    
    **Parameters:**
    - **case_id**: Case ID (required)
    
    **Returns:** Updated case object with status 'closed'
    """
    db_case = cases_crud.close_case(db, case_id)
    if not db_case:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Case with ID {case_id} not found"
        )
    return db_case


@router.delete("/{case_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_case(case_id: int, db: Session = Depends(get_db)):
    """
    Delete a case.
    
    **Parameters:**
    - **case_id**: Case ID (required)
    
    **Returns:** No content
    """
    success = cases_crud.delete_case(db, case_id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Case with ID {case_id} not found"
        )
