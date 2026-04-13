"""CRUD operations for documents"""

from sqlalchemy.orm import Session
from app.db.models import Document
from typing import List, Optional
from datetime import datetime
import os


def create_document(
    db: Session,
    case_id: int,
    filename: str,
    file_path: str,
    uploaded_by: Optional[int] = None,
    tags: Optional[List[str]] = None,
) -> Document:
    """Create a new document record"""
    db_document = Document(
        case_id=case_id,
        filename=filename,
        file_path=file_path,
        uploaded_by=uploaded_by,
        tags=tags or [],
    )
    db.add(db_document)
    db.commit()
    db.refresh(db_document)
    return db_document


def get_document(db: Session, document_id: int) -> Optional[Document]:
    """Get a document by ID"""
    return db.query(Document).filter(Document.id == document_id).first()


def get_documents_by_case(
    db: Session, case_id: int, skip: int = 0, limit: int = 100
) -> List[Document]:
    """Get all documents for a case"""
    return (
        db.query(Document)
        .filter(Document.case_id == case_id)
        .offset(skip)
        .limit(limit)
        .all()
    )


def search_documents(
    db: Session, case_id: int, search_term: str, skip: int = 0, limit: int = 100
) -> List[Document]:
    """Search documents by filename or tags"""
    query = db.query(Document).filter(Document.case_id == case_id)
    
    # Search in filename
    query = query.filter(
        Document.filename.ilike(f"%{search_term}%")
    )
    
    return query.offset(skip).limit(limit).all()


def update_document_tags(
    db: Session, document_id: int, tags: List[str]
) -> Optional[Document]:
    """Update document tags"""
    db_document = get_document(db, document_id)
    if db_document:
        db_document.tags = tags
        db_document.updated_at = datetime.utcnow()
        db.commit()
        db.refresh(db_document)
    return db_document


def delete_document(db: Session, document_id: int) -> bool:
    """Delete a document record and its file"""
    db_document = get_document(db, document_id)
    if db_document:
        # Delete file from disk if it exists
        if os.path.exists(db_document.file_path):
            try:
                os.remove(db_document.file_path)
            except OSError:
                pass
        
        db.delete(db_document)
        db.commit()
        return True
    return False


def get_all_documents(
    db: Session, skip: int = 0, limit: int = 100
) -> List[Document]:
    """Get all documents with pagination"""
    return db.query(Document).offset(skip).limit(limit).all()
