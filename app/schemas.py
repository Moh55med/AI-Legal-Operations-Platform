"""Request and response schemas using Pydantic"""

from pydantic import BaseModel, Field, EmailStr
from datetime import datetime
from typing import List, Optional
from enum import Enum


class RoleEnum(str, Enum):
    """Role enumeration"""
    SUPERVISOR = "supervisor"
    BASIC = "basic"


class CaseStatusEnum(str, Enum):
    """Case status enumeration"""
    OPEN = "open"
    CLOSED = "closed"
    ON_HOLD = "on_hold"


class AccessTypeEnum(str, Enum):
    """Access type enumeration"""
    ASSIGNED = "assigned"
    VIEWER = "viewer"


class DeadlineStatusEnum(str, Enum):
    """Deadline status enumeration"""
    PENDING = "pending"
    MISSED = "missed"
    COMPLETED = "completed"


# User Schemas
class UserBase(BaseModel):
    """Base user schema"""
    first_name: str = Field(..., min_length=1, max_length=100)
    last_name: str = Field(..., min_length=1, max_length=100)
    email: EmailStr
    phone: Optional[str] = Field(None, max_length=20)


class UserCreate(UserBase):
    """Schema for creating user"""
    username: str = Field(..., min_length=3, max_length=100)
    password: str = Field(..., min_length=8)


class UserResponse(UserBase):
    """Schema for user response"""
    id: int
    username: str
    role: RoleEnum
    is_active: bool
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


# Client Schemas
class ClientBase(BaseModel):
    """Base client schema"""
    first_name: str = Field(..., min_length=1, max_length=100)
    last_name: str = Field(..., min_length=1, max_length=100)
    email: EmailStr
    phone: Optional[str] = Field(None, max_length=20)
    company_name: Optional[str] = Field(None, max_length=255)
    address: Optional[str] = Field(None, max_length=500)
    city: Optional[str] = Field(None, max_length=100)
    state: Optional[str] = Field(None, max_length=100)
    zip_code: Optional[str] = Field(None, max_length=20)


class ClientCreate(ClientBase):
    """Schema for creating client"""
    pass


class ClientUpdate(BaseModel):
    """Schema for updating client"""
    first_name: Optional[str] = Field(None, max_length=100)
    last_name: Optional[str] = Field(None, max_length=100)
    email: Optional[EmailStr] = None
    phone: Optional[str] = Field(None, max_length=20)
    company_name: Optional[str] = Field(None, max_length=255)
    address: Optional[str] = Field(None, max_length=500)
    city: Optional[str] = Field(None, max_length=100)
    state: Optional[str] = Field(None, max_length=100)
    zip_code: Optional[str] = Field(None, max_length=20)


class ClientResponse(ClientBase):
    """Schema for client response"""
    id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


# Case Schemas
class CaseBase(BaseModel):
    """Base case schema"""
    title: str = Field(..., min_length=1, max_length=255)
    case_reference_number: str = Field(..., min_length=1, max_length=50)
    client_id: int
    description: Optional[str] = None


class CaseCreate(CaseBase):
    """Schema for creating case"""
    pass


class CaseUpdate(BaseModel):
    """Schema for updating case"""
    title: Optional[str] = Field(None, max_length=255)
    description: Optional[str] = None
    status: Optional[CaseStatusEnum] = None


class CaseResponse(CaseBase):
    """Schema for case response"""
    id: int
    status: CaseStatusEnum
    created_at: datetime
    updated_at: datetime
    closed_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class CaseDetailResponse(CaseResponse):
    """Detailed case response with related data"""
    pass


# Deadline Schemas
class DeadlineBase(BaseModel):
    """Base deadline schema"""
    due_date: datetime
    description: Optional[str] = None


class DeadlineCreate(DeadlineBase):
    """Schema for creating deadline"""
    case_id: int


class DeadlineUpdate(BaseModel):
    """Schema for updating deadline"""
    due_date: Optional[datetime] = None
    description: Optional[str] = None
    status: Optional[DeadlineStatusEnum] = None


class DeadlineResponse(DeadlineBase):
    """Schema for deadline response"""
    id: int
    case_id: int
    status: DeadlineStatusEnum
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


# Document Schemas
class DocumentBase(BaseModel):
    """Base document schema"""
    filename: str = Field(..., max_length=255)
    tags: List[str] = Field(default_factory=list)


class DocumentCreate(DocumentBase):
    """Schema for creating document"""
    case_id: int


class DocumentResponse(DocumentBase):
    """Schema for document response"""
    id: int
    case_id: int
    file_path: str
    uploaded_by: Optional[int] = None
    uploaded_at: datetime

    class Config:
        from_attributes = True


# Watcher Schemas
class WatcherCreate(BaseModel):
    """Schema for creating watcher"""
    user_id: int
    case_id: int
    access_type: AccessTypeEnum


class WatcherResponse(BaseModel):
    """Schema for watcher response"""
    id: int
    user_id: int
    case_id: int
    access_type: AccessTypeEnum
    assigned_at: datetime

    class Config:
        from_attributes = True


# Notification Schemas
class NotificationResponse(BaseModel):
    """Schema for notification response"""
    id: int
    user_id: int
    deadline_id: int
    status: str
    created_at: datetime
    read_at: Optional[datetime] = None

    class Config:
        from_attributes = True


# Audit Log Schemas
class AuditLogResponse(BaseModel):
    """Schema for audit log response"""
    id: int
    user_id: Optional[int] = None
    action: str
    change_in: Optional[dict] = None
    datetime: datetime
    ip_address: Optional[str] = None

    class Config:
        from_attributes = True
