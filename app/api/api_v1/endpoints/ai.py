"""
FastAPI endpoints for AI-powered legal insights.
Allows querying cases and documents using natural language.
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import Optional, List, Dict, Any
import logging
from pydantic import BaseModel, Field

from app.db.session import get_db
from app.services.ai_query import AIQueryService

logger = logging.getLogger(__name__)

router = APIRouter()


class AIQueryRequest(BaseModel):
    """Request model for AI query"""
    question: str = Field(..., min_length=1, max_length=1000)
    conversation_history: Optional[List[Dict[str, str]]] = Field(None)


class SourceInfo(BaseModel):
    """Information about data sources used"""
    cases_count: int
    documents_count: int
    deadlines_count: int


class Citation(BaseModel):
    """Citation for case/document/deadline"""
    type: str  # case, document, deadline
    id: int
    title: Optional[str] = None
    reference: Optional[str] = None
    filename: Optional[str] = None
    case_id: Optional[int] = None
    due_date: Optional[str] = None


class AIQueryResponse(BaseModel):
    """Response model for AI query"""
    success: bool
    answer: str
    citations: List[Citation] = []
    sources_used: SourceInfo = None
    conversation_history: Optional[List[Dict[str, str]]] = None
    error: Optional[str] = None

    class Config:
        from_attributes = True


@router.post("/query", response_model=AIQueryResponse, status_code=status.HTTP_200_OK)
def query_ai(request: AIQueryRequest, db: Session = Depends(get_db)):
    """
    Query AI insights about cases and documents using natural language.
    
    The system will:
    1. Search the database for relevant cases, documents, and deadlines based on keywords
    2. Send the relevant context to Claude AI
    3. Return Claude's answer with citations to the source data
    
    **Parameters:**
    - **question**: Your question about cases, documents, or deadlines (required)
    - **conversation_history**: Previous conversation messages for context (optional)
    
    **Returns:** AI-generated answer with citations and sources information
    
    **Example Request:**
    ```json
    {
        "question": "What documents do we have for John Smith's case?",
        "conversation_history": null
    }
    ```
    
    **Important Notes:**
    - This is NOT legal advice - AI responses are informational only
    - Always verify important information with your legal team
    - The API requires ANTHROPIC_API_KEY environment variable
    - Set API key in .env: ANTHROPIC_API_KEY=sk-ant-...
    """
    try:
        # Initialize AI service
        ai_service = AIQueryService()
        
        # Query Claude with relevant context
        result = ai_service.query_claude(
            db,
            question=request.question,
            conversation_history=request.conversation_history,
        )
        
        if not result["success"]:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=result.get("error", "Failed to process AI query"),
            )
        
        # Build response
        citations = []
        for citation_data in result.get("citations", []):
            citations.append(Citation(**citation_data))
        
        return AIQueryResponse(
            success=True,
            answer=result["answer"],
            citations=citations,
            sources_used=SourceInfo(**result.get("sources_used", {})),
            conversation_history=result.get("conversation_history"),
        )
    
    except ValueError as e:
        # API key not configured
        logger.error(f"API configuration error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="AI service not configured. Please set ANTHROPIC_API_KEY environment variable.",
        )
    
    except Exception as e:
        logger.error(f"Unexpected error in AI query: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error processing query: {str(e)}",
        )


@router.get("/health", response_model=Dict[str, Any])
def ai_service_health(db: Session = Depends(get_db)):
    """
    Check health of AI service and database connectivity.
    
    **Returns:** Status of AI service and database
    """
    try:
        # Try to initialize AI service
        ai_service = AIQueryService()
        ai_status = "available"
    except ValueError:
        ai_status = "not_configured"
    except Exception as e:
        ai_status = f"error: {str(e)}"
    
    # Check database
    try:
        # Simple query to verify database connection
        db.execute("SELECT 1")
        db_status = "connected"
    except Exception as e:
        db_status = f"error: {str(e)}"
    
    return {
        "service": "AI Insights",
        "ai_status": ai_status,
        "database_status": db_status,
        "healthy": ai_status == "available" and db_status == "connected",
    }
