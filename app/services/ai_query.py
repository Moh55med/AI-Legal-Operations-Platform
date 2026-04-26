"""
AI query service for legal insights.
Integrates with Claude API to answer questions about cases and documents.
"""

import os
from anthropic import Anthropic
from sqlalchemy.orm import Session
from app.db.models import Case, Document, Client, Deadline
from typing import Optional, Dict, List, Any
import logging

logger = logging.getLogger(__name__)


class AIQueryService:
    """Service for querying Claude AI with legal case context"""

    def __init__(self, api_key: Optional[str] = None):
        """Initialize AI service with Anthropic client"""
        self.api_key = api_key or os.getenv("ANTHROPIC_API_KEY")
        if not self.api_key:
            raise ValueError("ANTHROPIC_API_KEY not set in environment")
        
        self.client = Anthropic(api_key=self.api_key)
        self.model = "claude-3-5-sonnet-20241022"

    @staticmethod
    def fetch_relevant_data(
        db: Session,
        query: str,
        limit: int = 5,
    ) -> Dict[str, Any]:
        """
        Fetch relevant cases and documents based on the query.
        Search by case title, client name, case reference, deadlines, and document content.
        
        Returns dictionary with relevant data for context
        """
        query_lower = query.lower()
        
        # Search for cases by title, client name, or case reference
        cases = []
        case_results = (
            db.query(Case)
            .join(Client)
            .filter(
                (Case.title.ilike(f"%{query}%"))
                | (Client.first_name.ilike(f"%{query}%"))
                | (Client.last_name.ilike(f"%{query}%"))
                | (Case.case_reference_number.ilike(f"%{query}%"))
            )
            .limit(limit)
            .all()
        )
        
        for case in case_results:
            cases.append({
                "id": case.id,
                "title": case.title,
                "reference": case.case_reference_number,
                "status": case.status,
                "client": f"{case.client.first_name} {case.client.last_name}",
                "description": case.description,
                "created_at": case.created_at.isoformat() if case.created_at else None,
            })
        
        # Search for relevant documents
        documents = []
        doc_results = (
            db.query(Document)
            .filter(Document.filename.ilike(f"%{query}%"))
            .limit(limit)
            .all()
        )
        
        for doc in doc_results:
            documents.append({
                "id": doc.id,
                "filename": doc.filename,
                "case_id": doc.case_id,
                "tags": doc.tags,
                "uploaded_at": doc.uploaded_at.isoformat() if doc.uploaded_at else None,
            })
        
        # Search for relevant deadlines
        deadlines = []
        deadline_results = (
            db.query(Deadline)
            .filter(Deadline.description.ilike(f"%{query}%"))
            .limit(limit)
            .all()
        )
        
        for deadline in deadline_results:
            deadlines.append({
                "id": deadline.id,
                "case_id": deadline.case_id,
                "due_date": deadline.due_date.isoformat() if deadline.due_date else None,
                "description": deadline.description,
                "status": deadline.status,
            })
        
        return {
            "cases": cases,
            "documents": documents,
            "deadlines": deadlines,
        }

    def query_claude(
        self,
        db: Session,
        question: str,
        conversation_history: Optional[List[Dict[str, str]]] = None,
    ) -> Dict[str, Any]:
        """
        Query Claude AI with relevant case/document context.
        
        Parameters:
        - db: Database session
        - question: Natural language question
        - conversation_history: Previous message history for context
        
        Returns: Dictionary with answer and citations
        """
        # Fetch relevant data from database
        relevant_data = self.fetch_relevant_data(db, question)
        
        # Build context string
        context = self._build_context(question, relevant_data)
        
        # Build messages
        messages = conversation_history or []
        messages.append({
            "role": "user",
            "content": context,
        })
        
        try:
            # Call Claude API
            response = self.client.messages.create(
                model=self.model,
                max_tokens=1024,
                system=self._get_system_prompt(),
                messages=messages,
            )
            
            answer = response.content[0].text
            
            return {
                "success": True,
                "answer": answer,
                "citations": self._extract_citations(relevant_data),
                "sources_used": {
                    "cases_count": len(relevant_data["cases"]),
                    "documents_count": len(relevant_data["documents"]),
                    "deadlines_count": len(relevant_data["deadlines"]),
                },
                "conversation_history": messages,
            }
        
        except Exception as e:
            logger.error(f"Error querying Claude: {str(e)}")
            return {
                "success": False,
                "error": str(e),
                "answer": "Failed to process your query. Please try again.",
            }

    @staticmethod
    def _get_system_prompt() -> str:
        """Get the system prompt for Claude"""
        return """You are an AI legal assistant for a law firm platform. 
        You help answer questions about cases, documents, and deadlines.
        
        When answering questions:
        1. Be precise and professional
        2. Reference specific cases, clients, or documents when relevant
        3. Always cite your sources from the provided context
        4. If information is not available in the context, say so explicitly
        5. Do not provide legal advice - only factual information about cases and documents
        6. Include relevant deadlines or dates when applicable
        
        Format your response clearly with proper sections."""

    @staticmethod
    def _build_context(question: str, relevant_data: Dict[str, Any]) -> str:
        """Build the context message to send to Claude"""
        context = f"Question: {question}\n\n"
        context += "Relevant Context from Database:\n"
        context += "=" * 50 + "\n\n"
        
        # Add cases
        if relevant_data["cases"]:
            context += "RELEVANT CASES:\n"
            for case in relevant_data["cases"]:
                context += f"- Case: {case['title']} (Ref: {case['reference']})\n"
                context += f"  Client: {case['client']}\n"
                context += f"  Status: {case['status']}\n"
                if case['description']:
                    context += f"  Description: {case['description']}\n"
                context += "\n"
        
        # Add documents
        if relevant_data["documents"]:
            context += "RELEVANT DOCUMENTS:\n"
            for doc in relevant_data["documents"]:
                context += f"- Document: {doc['filename']}\n"
                context += f"  Case ID: {doc['case_id']}\n"
                if doc['tags']:
                    context += f"  Tags: {', '.join(doc['tags'])}\n"
                context += "\n"
        
        # Add deadlines
        if relevant_data["deadlines"]:
            context += "RELEVANT DEADLINES:\n"
            for deadline in relevant_data["deadlines"]:
                context += f"- Deadline: {deadline['description']} for Case {deadline['case_id']}\n"
                context += f"  Due: {deadline['due_date']}\n"
                context += f"  Status: {deadline['status']}\n"
                context += "\n"
        
        context += "=" * 50 + "\n"
        context += "Answer the question based on the context above.\n"
        
        return context

    @staticmethod
    def _extract_citations(relevant_data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Extract citations from the relevant data"""
        citations = []
        
        for case in relevant_data["cases"]:
            citations.append({
                "type": "case",
                "id": case["id"],
                "title": case["title"],
                "reference": case["reference"],
            })
        
        for doc in relevant_data["documents"]:
            citations.append({
                "type": "document",
                "id": doc["id"],
                "filename": doc["filename"],
                "case_id": doc["case_id"],
            })
        
        for deadline in relevant_data["deadlines"]:
            citations.append({
                "type": "deadline",
                "id": deadline["id"],
                "case_id": deadline["case_id"],
                "due_date": deadline["due_date"],
            })
        
        return citations
