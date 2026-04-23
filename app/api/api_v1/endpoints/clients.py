"""
FastAPI endpoints for client management.
Provides CRUD operations for law firm clients.
"""

from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import List
from app.db.session import get_db
from app.crud import clients as clients_crud
from app.schemas import ClientCreate, ClientUpdate, ClientResponse

router = APIRouter()


@router.post("/", response_model=ClientResponse, status_code=status.HTTP_201_CREATED)
def create_client(client: ClientCreate, db: Session = Depends(get_db)):
    """
    Create a new client.
    
    **Parameters:**
    - **first_name**: Client first name (required)
    - **last_name**: Client last name (required)
    - **email**: Client email - must be unique (required)
    - **phone**: Client phone number (optional)
    - **company_name**: Client company name (optional)
    - **address**: Client street address (optional)
    - **city**: Client city (optional)
    - **state**: Client state/province (optional)
    - **zip_code**: Client zip/postal code (optional)
    
    **Returns:** Created client object with ID
    """
    db_client = clients_crud.create_client(
        db,
        first_name=client.first_name,
        last_name=client.last_name,
        email=client.email,
        phone=client.phone,
        company_name=client.company_name,
        address=client.address,
        city=client.city,
        state=client.state,
        zip_code=client.zip_code,
    )
    return db_client


@router.get("/", response_model=List[ClientResponse])
def list_clients(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    """
    List all clients with pagination.
    
    **Parameters:**
    - **skip**: Number of records to skip (default: 0)
    - **limit**: Number of records to return (default: 100, max: 100)
    
    **Returns:** List of clients
    """
    if limit > 100:
        limit = 100
    clients = clients_crud.get_all_clients(db, skip=skip, limit=limit)
    return clients


@router.get("/search", response_model=List[ClientResponse])
def search_clients(
    search_term: str = Query(..., min_length=1),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=100),
    db: Session = Depends(get_db),
):
    """
    Search clients by name, email, or company.
    
    **Parameters:**
    - **search_term**: Search term (required, min length: 1)
    - **skip**: Number of records to skip (default: 0)
    - **limit**: Number of records to return (default: 100)
    
    **Returns:** List of matching clients
    """
    clients = clients_crud.search_clients(db, search_term, skip=skip, limit=limit)
    return clients


@router.get("/{client_id}", response_model=ClientResponse)
def get_client(client_id: int, db: Session = Depends(get_db)):
    """
    Get a specific client by ID.
    
    **Parameters:**
    - **client_id**: Client ID (required)
    
    **Returns:** Client object
    """
    db_client = clients_crud.get_client(db, client_id)
    if not db_client:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Client with ID {client_id} not found"
        )
    return db_client


@router.put("/{client_id}", response_model=ClientResponse)
def update_client(
    client_id: int,
    client_update: ClientUpdate,
    db: Session = Depends(get_db),
):
    """
    Update a client.
    
    **Parameters:**
    - **client_id**: Client ID (required)
    - **first_name**: Updated first name (optional)
    - **last_name**: Updated last name (optional)
    - **email**: Updated email (optional)
    - **phone**: Updated phone (optional)
    - **company_name**: Updated company name (optional)
    - **address**: Updated address (optional)
    - **city**: Updated city (optional)
    - **state**: Updated state (optional)
    - **zip_code**: Updated zip code (optional)
    
    **Returns:** Updated client object
    """
    db_client = clients_crud.update_client(
        db,
        client_id,
        first_name=client_update.first_name,
        last_name=client_update.last_name,
        email=client_update.email,
        phone=client_update.phone,
        company_name=client_update.company_name,
        address=client_update.address,
        city=client_update.city,
        state=client_update.state,
        zip_code=client_update.zip_code,
    )
    if not db_client:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Client with ID {client_id} not found"
        )
    return db_client


@router.delete("/{client_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_client(client_id: int, db: Session = Depends(get_db)):
    """
    Delete a client.
    
    **Parameters:**
    - **client_id**: Client ID (required)
    
    **Returns:** No content
    """
    success = clients_crud.delete_client(db, client_id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Client with ID {client_id} not found"
        )
