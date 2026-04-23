"""
FastAPI endpoints for case management.
Provides CRUD operations for legal cases.
"""

from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime
from app.db.session import get_db
from app.crud import cases as cases_crud
from app.schemas import CaseCreate, CaseUpdate, CaseResponse
from app.db.models import CaseStatusEnum

router = APIRouter()


@router.post("/", response_model=CaseResponse, status_code=status.HTTP_201_CREATED)
def create_case(case: CaseCreate, db: Session = Depends(get_db)):
    """
    Create a new case.
    
    **Parameters:**
    - **title**: Case title (required)
    - **case_reference_number**: Case reference number - must be unique (required)
    - **client_id**: Client ID (required)
    - **description**: Case description (optional)
    
    **Returns:** Created case object with ID
    """
    db_case = cases_crud.create_case(
        db,
        title=case.title,
        case_reference_number=case.case_reference_number,
        client_id=case.client_id,
        description=case.description,
    )
    return db_case


@router.get("/", response_model=List[CaseResponse])
def list_cases(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=100),
    status: Optional[CaseStatusEnum] = Query(None),
    title: Optional[str] = Query(None),
    case_reference_number: Optional[str] = Query(None),
    client_name: Optional[str] = Query(None),
    assigned_user_id: Optional[int] = Query(None),
    date_from: Optional[datetime] = Query(None),
    date_to: Optional[datetime] = Query(None),
    db: Session = Depends(get_db),
):
    """
    List all cases with advanced filtering and search.
    
    **Parameters:**
    - **skip**: Number of records to skip (default: 0)
    - **limit**: Number of records to return (default: 100, max: 100)
    - **status**: Filter by case status - 'open', 'closed', 'on_hold' (optional)
    - **title**: Search in case title (optional)
    - **case_reference_number**: Search by case reference number (optional)
    - **client_name**: Filter by client first or last name (optional)
    - **assigned_user_id**: Filter by assigned user ID (optional)
    - **date_from**: Filter cases created from this date (ISO format, optional)
    - **date_to**: Filter cases created until this date (ISO format, optional)
    
    **Returns:** List of cases matching the filters
    """
    if limit > 100:
        limit = 100
    
    # If any filter is provided, use advanced filtering
    if any([status, title, case_reference_number, client_name, assigned_user_id, date_from, date_to]):
        cases = cases_crud.filter_cases(
            db,
            status=status,
            client_name=client_name,
            assigned_user_id=assigned_user_id,
            date_from=date_from,
            date_to=date_to,
            title=title,
            case_reference_number=case_reference_number,
            skip=skip,
            limit=limit,
        )
    else:
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
