"""CRUD operations for clients"""

from sqlalchemy.orm import Session
from app.db.models import Client
from typing import List, Optional
from datetime import datetime


def create_client(
    db: Session,
    first_name: str,
    last_name: str,
    email: str,
    phone: Optional[str] = None,
    company_name: Optional[str] = None,
    address: Optional[str] = None,
    city: Optional[str] = None,
    state: Optional[str] = None,
    zip_code: Optional[str] = None,
) -> Client:
    """Create a new client"""
    db_client = Client(
        first_name=first_name,
        last_name=last_name,
        email=email,
        phone=phone,
        company_name=company_name,
        address=address,
        city=city,
        state=state,
        zip_code=zip_code,
    )
    db.add(db_client)
    db.commit()
    db.refresh(db_client)
    return db_client


def get_client(db: Session, client_id: int) -> Optional[Client]:
    """Get a client by ID"""
    return db.query(Client).filter(Client.id == client_id).first()


def get_all_clients(db: Session, skip: int = 0, limit: int = 100) -> List[Client]:
    """Get all clients with pagination"""
    return db.query(Client).offset(skip).limit(limit).all()


def search_clients(
    db: Session, search_term: str, skip: int = 0, limit: int = 100
) -> List[Client]:
    """Search clients by name or email"""
    query = db.query(Client).filter(
        (Client.first_name.ilike(f"%{search_term}%"))
        | (Client.last_name.ilike(f"%{search_term}%"))
        | (Client.email.ilike(f"%{search_term}%"))
        | (Client.company_name.ilike(f"%{search_term}%"))
    )
    return query.offset(skip).limit(limit).all()


def update_client(
    db: Session,
    client_id: int,
    first_name: Optional[str] = None,
    last_name: Optional[str] = None,
    email: Optional[str] = None,
    phone: Optional[str] = None,
    company_name: Optional[str] = None,
    address: Optional[str] = None,
    city: Optional[str] = None,
    state: Optional[str] = None,
    zip_code: Optional[str] = None,
) -> Optional[Client]:
    """Update a client"""
    db_client = get_client(db, client_id)
    if db_client:
        if first_name is not None:
            db_client.first_name = first_name
        if last_name is not None:
            db_client.last_name = last_name
        if email is not None:
            db_client.email = email
        if phone is not None:
            db_client.phone = phone
        if company_name is not None:
            db_client.company_name = company_name
        if address is not None:
            db_client.address = address
        if city is not None:
            db_client.city = city
        if state is not None:
            db_client.state = state
        if zip_code is not None:
            db_client.zip_code = zip_code
        db_client.updated_at = datetime.utcnow()
        db.commit()
        db.refresh(db_client)
    return db_client


def delete_client(db: Session, client_id: int) -> bool:
    """Delete a client"""
    db_client = get_client(db, client_id)
    if db_client:
        db.delete(db_client)
        db.commit()
        return True
    return False
