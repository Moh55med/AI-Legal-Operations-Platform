"""
AI Assistant Service for structured legal queries
Handles keyword-based routing and context-specific responses
"""

from datetime import datetime
from typing import Optional, List, Dict, Any
from sqlalchemy.orm import Session
from sqlalchemy import func
import re

from app.db.models import Case, Client, Deadline, Document, User
from app.core.config import settings


class StructuredQueryResponse:
    """Response model for structured queries"""
    
    def __init__(self, success: bool, query_type: str, answer: str, data: Optional[Dict[str, Any]] = None):
        self.success = success
        self.query_type = query_type
        self.answer = answer
        self.data = data or {}


class AIAssistantService:
    """
    Structured AI Assistant for legal operations
    Routes queries to specific handlers based on keywords
    """
    
    # Keyword patterns for routing
    CASE_DURATION_KEYWORDS = [
        r'how\s+long\s+.*case',
        r'case\s+duration',
        r'how\s+much\s+time',
        r'been\s+going',
        r'how\s+long\s+has\s+this',
    ]
    
    CLIENT_CASE_COUNT_KEYWORDS = [
        r'how\s+many\s+cases',
        r'cases\s+from.*client',
        r'client.*how\s+many',
        r'cases\s+associated',
        r'client\s+cases',
    ]
    
    DEADLINE_STATUS_KEYWORDS = [
        r'reached\s+.*deadline',
        r'deadline\s+.*court',
        r'court\s+hearing\s+deadline',
        r'deadline\s+status',
        r'deadline\s+approaching',
        r'time\s+until\s+deadline',
        r'when\s+.*deadline',
    ]
    
    def __init__(self, db: Session):
        self.db = db
    
    def identify_query_type(self, question: str) -> str:
        """
        Identify the type of query based on keywords
        Returns: 'case_duration', 'client_count', 'deadline_status', or 'unknown'
        """
        question_lower = question.lower().strip()
        
        # Check case duration keywords
        for pattern in self.CASE_DURATION_KEYWORDS:
            if re.search(pattern, question_lower):
                return 'case_duration'
        
        # Check client case count keywords
        for pattern in self.CLIENT_CASE_COUNT_KEYWORDS:
            if re.search(pattern, question_lower):
                return 'client_count'
        
        # Check deadline status keywords
        for pattern in self.DEADLINE_STATUS_KEYWORDS:
            if re.search(pattern, question_lower):
                return 'deadline_status'
        
        return 'unknown'
    
    def extract_case_identifier(self, question: str) -> Optional[str]:
        """
        Extract case identifier from question
        Looks for case names, reference numbers, or IDs
        Returns: case name, reference number, or None
        """
        # Pattern for case reference numbers like CASE-2024-0012
        ref_match = re.search(r'CASE-\d{4}-\d{4}', question, re.IGNORECASE)
        if ref_match:
            return ref_match.group(0)
        
        # Pattern for quoted case names
        quote_match = re.search(r'"([^"]+)"', question)
        if quote_match:
            return quote_match.group(1)
        
        # If "this case" is mentioned, we'll handle it contextually
        if 'this case' in question.lower():
            return 'this'
        
        return None
    
    def extract_client_identifier(self, question: str) -> Optional[str]:
        """
        Extract client identifier from question
        Looks for client names, or generic "the client" references
        """
        # Pattern for quoted names
        quote_match = re.search(r'"([^"]+)"', question)
        if quote_match:
            return quote_match.group(1)
        
        # If "the client" is mentioned
        if 'this client' in question.lower() or 'the client' in question.lower():
            return 'current'
        
        return None
    
    def query_case_duration(self, question: str) -> StructuredQueryResponse:
        """
        Handle case duration queries
        Fetches case creation date and calculates duration
        """
        try:
            case_identifier = self.extract_case_identifier(question)
            
            if not case_identifier:
                return StructuredQueryResponse(
                    success=False,
                    query_type='case_duration',
                    answer='Please specify which case you\'re asking about (e.g., "CASE-2024-0012" or "Ahmed Property Dispute")',
                    data={}
                )
            
            # Search for case by reference number or title
            case = None
            if case_identifier.startswith('CASE-'):
                case = self.db.query(Case).filter(
                    Case.case_reference_number == case_identifier
                ).first()
            else:
                # Search by title (case-insensitive)
                case = self.db.query(Case).filter(
                    Case.title.ilike(f'%{case_identifier}%')
                ).first()
            
            if not case:
                return StructuredQueryResponse(
                    success=False,
                    query_type='case_duration',
                    answer=f'Case "{case_identifier}" not found in database. Please check the case reference number or name.',
                    data={}
                )
            
            # Calculate duration
            created_date = case.created_at
            current_date = datetime.utcnow()
            duration = self._calculate_duration_string(created_date, current_date)
            
            # Format response
            answer = f"""
Case: {case.title}
Reference: {case.case_reference_number}
Created: {created_date.strftime('%d/%m/%Y')}
Duration: {duration}
Status: {case.status}
""".strip()
            
            response_data = {
                'case_id': case.id,
                'title': case.title,
                'reference': case.case_reference_number,
                'created_at': created_date.isoformat(),
                'duration': duration,
                'status': case.status,
            }
            
            return StructuredQueryResponse(
                success=True,
                query_type='case_duration',
                answer=answer,
                data=response_data
            )
        
        except Exception as e:
            return StructuredQueryResponse(
                success=False,
                query_type='case_duration',
                answer=f'Error retrieving case duration: {str(e)}',
                data={}
            )
    
    def query_client_case_count(self, question: str) -> StructuredQueryResponse:
        """
        Handle client case count queries
        Fetches all cases for a client with details
        """
        try:
            client_identifier = self.extract_client_identifier(question)
            
            if not client_identifier:
                return StructuredQueryResponse(
                    success=False,
                    query_type='client_count',
                    answer='Please specify which client you\'re asking about (e.g., "Ahmed" or "John Smith")',
                    data={}
                )
            
            # Search for client
            client = None
            if client_identifier != 'current':
                # Search by first name, last name, or company
                client = self.db.query(Client).filter(
                    (Client.first_name.ilike(f'%{client_identifier}%')) |
                    (Client.last_name.ilike(f'%{client_identifier}%')) |
                    (Client.company_name.ilike(f'%{client_identifier}%'))
                ).first()
            
            if not client:
                return StructuredQueryResponse(
                    success=False,
                    query_type='client_count',
                    answer=f'Client "{client_identifier}" not found in database.',
                    data={}
                )
            
            # Get all cases for this client
            cases = self.db.query(Case).filter(Case.client_id == client.id).all()
            
            # Format response
            client_name = f'{client.first_name} {client.last_name}'.strip()
            case_count = len(cases)
            
            cases_text = f'({client_name}) has {case_count} case{"s" if case_count != 1 else ""}\n'
            
            for idx, case in enumerate(cases, 1):
                cases_text += f'  Case {idx}: {case.title}\n'
                cases_text += f'    Reference: {case.case_reference_number}\n'
                cases_text += f'    Created: {case.created_at.strftime("%d/%m/%Y")}\n'
                cases_text += f'    Status: {case.status}\n'
            
            response_data = {
                'client_id': client.id,
                'client_name': client_name,
                'case_count': case_count,
                'cases': [
                    {
                        'id': c.id,
                        'title': c.title,
                        'reference': c.case_reference_number,
                        'created_at': c.created_at.isoformat(),
                        'status': c.status,
                    }
                    for c in cases
                ]
            }
            
            return StructuredQueryResponse(
                success=True,
                query_type='client_count',
                answer=cases_text.strip(),
                data=response_data
            )
        
        except Exception as e:
            return StructuredQueryResponse(
                success=False,
                query_type='client_count',
                answer=f'Error retrieving client cases: {str(e)}',
                data={}
            )
    
    def query_deadline_status(self, question: str) -> StructuredQueryResponse:
        """
        Handle deadline status queries
        Fetches deadline and calculates days remaining
        """
        try:
            case_identifier = self.extract_case_identifier(question)
            
            if not case_identifier:
                return StructuredQueryResponse(
                    success=False,
                    query_type='deadline_status',
                    answer='Please specify which case\'s deadline you\'re asking about (e.g., "CASE-2024-0012" or "Ahmed Property Dispute")',
                    data={}
                )
            
            # Search for case
            case = None
            if case_identifier.startswith('CASE-'):
                case = self.db.query(Case).filter(
                    Case.case_reference_number == case_identifier
                ).first()
            else:
                case = self.db.query(Case).filter(
                    Case.title.ilike(f'%{case_identifier}%')
                ).first()
            
            if not case:
                return StructuredQueryResponse(
                    success=False,
                    query_type='deadline_status',
                    answer=f'Case "{case_identifier}" not found in database.',
                    data={}
                )
            
            # Get deadlines for this case
            deadlines = self.db.query(Deadline).filter(
                Deadline.case_id == case.id
            ).order_by(Deadline.due_date).all()
            
            if not deadlines:
                return StructuredQueryResponse(
                    success=False,
                    query_type='deadline_status',
                    answer=f'No deadlines found for case "{case.title}"',
                    data={'case_id': case.id, 'case_title': case.title}
                )
            
            # Use the nearest upcoming deadline or first pending one
            current_date = datetime.utcnow().date()
            upcoming_deadline = None
            
            for deadline in deadlines:
                if deadline.due_date >= current_date and deadline.status == 'pending':
                    upcoming_deadline = deadline
                    break
            
            if not upcoming_deadline:
                upcoming_deadline = deadlines[0]
            
            # Calculate days remaining
            days_remaining = (upcoming_deadline.due_date - current_date).days
            
            # Format response
            answer = f"""
Case: {case.title}
Reference: {case.case_reference_number}
Deadline: {upcoming_deadline.due_date.strftime('%d/%m/%Y')}
Days Remaining: {days_remaining}
Status: {upcoming_deadline.status}
Description: {upcoming_deadline.description}
""".strip()
            
            response_data = {
                'case_id': case.id,
                'case_title': case.title,
                'case_reference': case.case_reference_number,
                'deadline_id': upcoming_deadline.id,
                'due_date': upcoming_deadline.due_date.isoformat(),
                'days_remaining': days_remaining,
                'status': upcoming_deadline.status,
                'description': upcoming_deadline.description,
            }
            
            return StructuredQueryResponse(
                success=True,
                query_type='deadline_status',
                answer=answer,
                data=response_data
            )
        
        except Exception as e:
            return StructuredQueryResponse(
                success=False,
                query_type='deadline_status',
                answer=f'Error retrieving deadline status: {str(e)}',
                data={}
            )
    
    def process_query(self, question: str) -> StructuredQueryResponse:
        """
        Main entry point for processing queries
        Routes to appropriate handler based on query type
        """
        query_type = self.identify_query_type(question)
        
        if query_type == 'case_duration':
            return self.query_case_duration(question)
        
        elif query_type == 'client_count':
            return self.query_client_case_count(question)
        
        elif query_type == 'deadline_status':
            return self.query_deadline_status(question)
        
        else:
            return StructuredQueryResponse(
                success=False,
                query_type='unknown',
                answer='I didn\'t understand your query. Please ask about:\n'
                       '1. Case duration (e.g., "How long has this case been going?")\n'
                       '2. Client cases (e.g., "How many cases do we have from Ahmed?")\n'
                       '3. Deadline status (e.g., "Has this case reached the deadline?")',
                data={}
            )
    
    @staticmethod
    def _calculate_duration_string(start_date: datetime, end_date: datetime) -> str:
        """
        Calculate human-readable duration string
        """
        # Get difference
        diff = end_date.replace(hour=0, minute=0, second=0, microsecond=0) - start_date.replace(hour=0, minute=0, second=0, microsecond=0)
        days = diff.days
        
        # Calculate years, months, days
        years = days // 365
        remaining_days = days % 365
        months = remaining_days // 30
        final_days = remaining_days % 30
        
        parts = []
        if years > 0:
            parts.append(f'{years} year{"s" if years != 1 else ""}')
        if months > 0:
            parts.append(f'{months} month{"s" if months != 1 else ""}')
        if final_days > 0 or not parts:
            parts.append(f'{final_days} day{"s" if final_days != 1 else ""}')
        
        return ', '.join(parts)
