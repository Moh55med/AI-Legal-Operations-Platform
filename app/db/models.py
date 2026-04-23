"""
SQLAlchemy ORM models for database tables.
Defines all tables for cases, users, documents, deadlines, notifications, and audit logs.
"""

from sqlalchemy import (
    Column, Integer, String, DateTime, Boolean, Enum, ForeignKey,
    JSON, UniqueConstraint, Index, Text
)
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from datetime import datetime
import enum

Base = declarative_base()


class RoleEnum(str, enum.Enum):
    """Role enumeration for users"""
    SUPERVISOR = "supervisor"
    BASIC = "basic"


class AccessTypeEnum(str, enum.Enum):
    """Access type enumeration for watchers"""
    ASSIGNED = "assigned"
    VIEWER = "viewer"


class CaseStatusEnum(str, enum.Enum):
    """Case status enumeration"""
    OPEN = "open"
    CLOSED = "closed"
    ON_HOLD = "on_hold"


class DeadlineStatusEnum(str, enum.Enum):
    """Deadline status enumeration"""
    PENDING = "pending"
    MISSED = "missed"
    COMPLETED = "completed"


class User(Base):
    """User table for authentication and role management"""
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    first_name = Column(String(100), nullable=False)
    last_name = Column(String(100), nullable=False)
    username = Column(String(100), unique=True, nullable=False, index=True)
    email = Column(String(255), unique=True, nullable=False, index=True)
    phone = Column(String(20), nullable=True)
    password = Column(String(255), nullable=False)
    role = Column(Enum(RoleEnum), default=RoleEnum.BASIC, nullable=False)
    is_active = Column(Boolean, default=True, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    # Relationships
    cases = relationship("Watcher", back_populates="user", cascade="all, delete-orphan")
    documents = relationship("Document", back_populates="uploaded_by_user", foreign_keys="Document.uploaded_by")
    audit_logs = relationship("AuditLog", back_populates="user", cascade="all, delete-orphan")
    notifications = relationship("Notification", back_populates="user", cascade="all, delete-orphan")


class Client(Base):
    """Client table for law firm clients"""
    __tablename__ = "clients"

    id = Column(Integer, primary_key=True, index=True)
    first_name = Column(String(100), nullable=False)
    last_name = Column(String(100), nullable=False)
    email = Column(String(255), unique=True, nullable=False, index=True)
    phone = Column(String(20), nullable=True)
    company_name = Column(String(255), nullable=True)
    address = Column(String(500), nullable=True)
    city = Column(String(100), nullable=True)
    state = Column(String(100), nullable=True)
    zip_code = Column(String(20), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    # Relationships
    cases = relationship("Case", back_populates="client", cascade="all, delete-orphan")


class Case(Base):
    """Case table for tracking legal cases"""
    __tablename__ = "cases"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(255), nullable=False)
    case_reference_number = Column(String(50), unique=True, nullable=False, index=True)
    client_id = Column(Integer, ForeignKey("clients.id", ondelete="CASCADE"), nullable=False, index=True)
    status = Column(Enum(CaseStatusEnum), default=CaseStatusEnum.OPEN, nullable=False)
    description = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False, index=True)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    closed_at = Column(DateTime, nullable=True)

    # Relationships
    client = relationship("Client", back_populates="cases")
    watchers = relationship("Watcher", back_populates="case", cascade="all, delete-orphan")
    documents = relationship("Document", back_populates="case", cascade="all, delete-orphan")
    deadlines = relationship("Deadline", back_populates="case", cascade="all, delete-orphan")


class Watcher(Base):
    """Watcher join table linking users to cases with access type"""
    __tablename__ = "watchers"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    case_id = Column(Integer, ForeignKey("cases.id", ondelete="CASCADE"), nullable=False, index=True)
    access_type = Column(Enum(AccessTypeEnum), nullable=False)
    assigned_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    # Composite unique constraint: each user can have only one access type per case
    __table_args__ = (
        UniqueConstraint("user_id", "case_id", name="uq_user_case"),
    )

    # Relationships
    user = relationship("User", back_populates="cases")
    case = relationship("Case", back_populates="watchers")


class Document(Base):
    """Document table for storing legal documents"""
    __tablename__ = "documents"

    id = Column(Integer, primary_key=True, index=True)
    case_id = Column(Integer, ForeignKey("cases.id", ondelete="CASCADE"), nullable=False, index=True)
    filename = Column(String(255), nullable=False)
    file_path = Column(String(500), nullable=False)
    uploaded_by = Column(Integer, ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    tags = Column(JSON, default=list, nullable=False)  # Array of tags
    uploaded_at = Column(DateTime, default=datetime.utcnow, nullable=False, index=True)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    # Relationships
    case = relationship("Case", back_populates="documents")
    uploaded_by_user = relationship("User", back_populates="documents", foreign_keys=[uploaded_by])


class Deadline(Base):
    """Deadline table for tracking case deadlines"""
    __tablename__ = "deadlines"

    id = Column(Integer, primary_key=True, index=True)
    case_id = Column(Integer, ForeignKey("cases.id", ondelete="CASCADE"), nullable=False, index=True)
    due_date = Column(DateTime, nullable=False, index=True)
    description = Column(Text, nullable=True)
    status = Column(Enum(DeadlineStatusEnum), default=DeadlineStatusEnum.PENDING, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    # Relationships
    case = relationship("Case", back_populates="deadlines")
    notifications = relationship("Notification", back_populates="deadline", cascade="all, delete-orphan")

    __table_args__ = (
        Index("idx_deadline_due_date", "due_date"),
    )


class AuditLog(Base):
    """AuditLog table for tracking user actions"""
    __tablename__ = "audit_logs"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    action = Column(String(100), nullable=False)
    change_in = Column(JSON, nullable=True)  # Track what changed
    datetime = Column(DateTime, default=datetime.utcnow, nullable=False, index=True)
    ip_address = Column(String(45), nullable=True)  # IPv6 support

    # Relationships
    user = relationship("User", back_populates="audit_logs")


class Notification(Base):
    """Notification table for deadline alerts"""
    __tablename__ = "notifications"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    deadline_id = Column(Integer, ForeignKey("deadlines.id", ondelete="CASCADE"), nullable=False, index=True)
    status = Column(String(50), default="unread", nullable=False)  # unread, read, dismissed
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    read_at = Column(DateTime, nullable=True)

    __table_args__ = (
        Index("idx_notification_deadline", "deadline_id"),
        Index("idx_notification_user_status", "user_id", "status"),
    )

    # Relationships
    user = relationship("User", back_populates="notifications")
    deadline = relationship("Deadline", back_populates="notifications")
