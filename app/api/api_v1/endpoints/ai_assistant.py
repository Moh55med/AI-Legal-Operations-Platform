"""
AI Assistant API endpoints
Provides structured query endpoint for legal operations
"""

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from sqlalchemy.orm import Session
from typing import Optional, Dict, Any

from app.db.session import get_db
from app.services.ai_assistant import AIAssistantService

router = APIRouter()


class AssistantQueryRequest(BaseModel):
    """Request model for assistant queries"""
    question: str


class AssistantQueryResponse(BaseModel):
    """Response model for assistant queries"""
    success: bool
    query_type: str
    answer: str
    data: Dict[str, Any] = {}


@router.post("/ask", response_model=AssistantQueryResponse, status_code=status.HTTP_200_OK)
def ask_assistant(
    request: AssistantQueryRequest,
    db: Session = Depends(get_db)
) -> AssistantQueryResponse:
    """
    Ask the AI Assistant a structured query about cases, clients, or deadlines.
    
    Supported query types:
    1. Case Duration: "How long has this case been going?" or "Case duration for CASE-2024-0012"
    2. Client Cases: "How many cases do we have from Ahmed?" or "Cases from this client"
    3. Deadline Status: "Has this case reached the deadline?" or "When is the deadline for CASE-2024-0012?"
    
    If the query is ambiguous or doesn't match any category, the assistant will request clarification.
    """
    
    if not request.question or not request.question.strip():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Question cannot be empty"
        )
    
    try:
        # Initialize service and process query
        assistant = AIAssistantService(db=db)
        response = assistant.process_query(request.question)
        
        return AssistantQueryResponse(
            success=response.success,
            query_type=response.query_type,
            answer=response.answer,
            data=response.data
        )
    
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error processing query: {str(e)}"
        )


@router.get("/health", status_code=status.HTTP_200_OK)
def assistant_health(db: Session = Depends(get_db)) -> Dict[str, Any]:
    """
    Check AI Assistant service health and database connectivity.
    """
    try:
        # Verify database connection
        db.execute("SELECT 1")
        
        return {
            "status": "healthy",
            "service": "ai-assistant",
            "database": "connected",
            "supported_queries": [
                "case_duration",
                "client_count",
                "deadline_status"
            ]
        }
    
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=f"Service unavailable: {str(e)}"
        )
