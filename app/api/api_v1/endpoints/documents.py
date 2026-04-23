"""
FastAPI endpoints for document management.
Handles document upload, retrieval, search, and download.
"""

from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File, Query
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime
import os
import shutil
from pathlib import Path
from app.db.session import get_db
from app.crud import documents as documents_crud
from app.schemas import DocumentCreate, DocumentResponse

router = APIRouter()

# Upload directory configuration
UPLOAD_DIR = Path("uploads")
UPLOAD_DIR.mkdir(exist_ok=True)


def create_case_upload_dir(case_id: int) -> Path:
    """Create a case-specific upload directory"""
    case_dir = UPLOAD_DIR / f"case_{case_id}"
    case_dir.mkdir(parents=True, exist_ok=True)
    return case_dir


@router.post("/upload", response_model=DocumentResponse, status_code=status.HTTP_201_CREATED)
async def upload_document(
    case_id: int = Query(...),
    file: UploadFile = File(...),
    tags: Optional[List[str]] = Query(None),
    uploaded_by: Optional[int] = Query(None),
    db: Session = Depends(get_db),
):
    """
    Upload a document to a case.
    
    **Parameters:**
    - **case_id**: Case ID to upload document to (required)
    - **file**: File to upload (required)
    - **tags**: List of tags for the document (optional)
    - **uploaded_by**: User ID of uploader (optional)
    
    **Returns:** Created document object
    """
    try:
        # Create case-specific directory
        case_dir = create_case_upload_dir(case_id)
        
        # Generate unique filename with case prefix
        file_extension = os.path.splitext(file.filename)[1]
        unique_filename = f"doc_{case_id}_{os.urandom(8).hex()}{file_extension}"
        file_path = case_dir / unique_filename
        
        # Save file to disk
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
        
        # Create document record in database
        db_document = documents_crud.create_document(
            db,
            case_id=case_id,
            filename=file.filename,
            file_path=str(file_path),
            uploaded_by=uploaded_by,
            tags=tags or [],
        )
        
        return db_document
    
    except Exception as e:
        # Clean up uploaded file if database save fails
        if os.path.exists(file_path):
            os.remove(file_path)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"File upload failed: {str(e)}"
        )


@router.get("/", response_model=List[DocumentResponse])
def list_documents(
    case_id: Optional[int] = Query(None),
    filename: Optional[str] = Query(None),
    uploaded_by: Optional[int] = Query(None),
    uploaded_at: Optional[datetime] = Query(None),
    uploaded_at_from: Optional[datetime] = Query(None),
    uploaded_at_to: Optional[datetime] = Query(None),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=100),
    db: Session = Depends(get_db),
):
    """
    List documents with advanced filtering.
    
    **Parameters:**
    - **case_id**: Filter documents by case ID (optional)
    - **filename**: Search in filename (optional)
    - **uploaded_by**: Filter by uploader user ID (optional)
    - **uploaded_at**: Filter documents uploaded on exact date (ISO format, optional)
    - **uploaded_at_from**: Filter documents uploaded on or after this date (ISO format, optional)
    - **uploaded_at_to**: Filter documents uploaded on or before this date (ISO format, optional)
    - **skip**: Number of records to skip (default: 0)
    - **limit**: Number of records to return (default: 100)
    
    **Returns:** List of documents
    """
    if limit > 100:
        limit = 100
    
    # If any filter is provided, use advanced filtering
    if any([case_id, filename, uploaded_by, uploaded_at, uploaded_at_from, uploaded_at_to]):
        documents = documents_crud.filter_documents(
            db,
            case_id=case_id,
            filename=filename,
            uploaded_by=uploaded_by,
            uploaded_at=uploaded_at,
            uploaded_at_from=uploaded_at_from,
            uploaded_at_to=uploaded_at_to,
            skip=skip,
            limit=limit,
        )
    else:
        documents = documents_crud.get_all_documents(db, skip=skip, limit=limit)
    
    return documents


@router.get("/search", response_model=List[DocumentResponse])
def search_documents(
    case_id: int = Query(...),
    search_term: str = Query(..., min_length=1),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=100),
    db: Session = Depends(get_db),
):
    """
    Search documents by filename within a case.
    
    **Parameters:**
    - **case_id**: Case ID to search in (required)
    - **search_term**: Search term (required, min length: 1)
    - **skip**: Number of records to skip (default: 0)
    - **limit**: Number of records to return (default: 100)
    
    **Returns:** List of matching documents
    """
    documents = documents_crud.search_documents(
        db, case_id, search_term, skip=skip, limit=limit
    )
    return documents


@router.get("/{document_id}", response_model=DocumentResponse)
def get_document(document_id: int, db: Session = Depends(get_db)):
    """
    Get a specific document by ID.
    
    **Parameters:**
    - **document_id**: Document ID (required)
    
    **Returns:** Document object
    """
    db_document = documents_crud.get_document(db, document_id)
    if not db_document:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Document with ID {document_id} not found"
        )
    return db_document


@router.get("/{document_id}/download")
def download_document(document_id: int, db: Session = Depends(get_db)):
    """
    Download a document file.
    
    **Parameters:**
    - **document_id**: Document ID (required)
    
    **Returns:** File content
    """
    db_document = documents_crud.get_document(db, document_id)
    if not db_document:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Document with ID {document_id} not found"
        )
    
    if not os.path.exists(db_document.file_path):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Document file not found on disk"
        )
    
    return FileResponse(
        path=db_document.file_path,
        filename=db_document.filename,
        media_type="application/octet-stream",
    )


@router.delete("/{document_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_document(document_id: int, db: Session = Depends(get_db)):
    """
    Delete a document and its associated file.
    
    **Parameters:**
    - **document_id**: Document ID (required)
    
    **Returns:** No content
    """
    success = documents_crud.delete_document(db, document_id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Document with ID {document_id} not found"
        )
