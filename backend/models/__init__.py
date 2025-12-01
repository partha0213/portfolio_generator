from sqlalchemy import Column, String, Integer, DateTime, JSON, Text, Boolean, Float, ForeignKey, Index
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from database import Base
import uuid
from datetime import datetime

class User(Base):
    __tablename__ = "users"
    
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    email = Column(String(255), unique=True, nullable=False, index=True)
    hashed_password = Column(String(255), nullable=False)
    full_name = Column(String(255))
    is_email_verified = Column(Boolean, default=False, nullable=False)
    verification_code = Column(String(6), nullable=True)
    verification_code_expires_at = Column(DateTime(timezone=True), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    projects = relationship("Project", back_populates="user", lazy="dynamic")
    assets = relationship("Asset", back_populates="user", lazy="dynamic")
    deployments = relationship("Deployment", back_populates="user", lazy="dynamic")
    generation_logs = relationship("GenerationLog", back_populates="user", lazy="dynamic")

class Session(Base):
    __tablename__ = "sessions"
    
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String(36), ForeignKey("users.id"), nullable=True, index=True)
    resume_filename = Column(String(255))
    resume_data = Column(JSON)
    user_prompt = Column(Text, nullable=True)
    portfolio_code = Column(JSON, nullable=True)
    generated_at = Column(DateTime(timezone=True), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    
    __table_args__ = (
        Index('idx_session_user_created', 'user_id', 'created_at'),
    )

class Project(Base):
    __tablename__ = "projects"
    
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String(36), ForeignKey("users.id"), nullable=True, index=True)
    session_id = Column(String(36), ForeignKey("sessions.id"), nullable=False)
    name = Column(String(255))
    stack = Column(String(50))  # react, nextjs, vue, svelte
    files = Column(JSON)  # File structure as JSON
    customization = Column(JSON)  # Theme, colors, design_notes
    status = Column(String(20), default="draft")  # draft, published, archived
    is_public = Column(Boolean, default=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    
    # Relationships
    user = relationship("User", back_populates="projects")
    
    __table_args__ = (
        Index('idx_project_user_created', 'user_id', 'created_at'),
    )

class ChatHistory(Base):
    __tablename__ = "chat_history"
    
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    session_id = Column(String(36), ForeignKey("sessions.id"), nullable=False, index=True)
    user_id = Column(String(36), ForeignKey("users.id"), nullable=False, index=True)
    role = Column(String(20))  # user, assistant
    message = Column(Text)
    thought = Column(Text, nullable=True)
    file_changes = Column(JSON, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

class ChatSession(Base):
    """Extended chat sessions for rich chat features"""
    __tablename__ = "chat_sessions"
    
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String(36), ForeignKey("users.id"), nullable=True, index=True)
    session_id = Column(String(36), ForeignKey("sessions.id"), nullable=False, index=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    last_active = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    # 'metadata' is a reserved attribute name on the declarative base.
    # Use a different Python attribute while keeping the DB column name as 'metadata'.
    session_metadata = Column('metadata', JSON, nullable=True)  # Store context like theme prefs
    
    __table_args__ = (
        Index('idx_chat_sessions_user', 'user_id', 'last_active'),
    )

class PortfolioSnapshot(Base):
    """Portfolio version snapshots for undo/redo"""
    __tablename__ = "portfolio_snapshots"
    
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    session_id = Column(String(36), ForeignKey("sessions.id"), nullable=False, index=True)
    files = Column(JSON, nullable=False)  # Complete portfolio file structure
    size_bytes = Column(Integer, nullable=False)  # For size limit enforcement
    description = Column(Text, nullable=True)  # Human-readable description
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    __table_args__ = (
        Index('idx_snapshots_session', 'session_id', 'created_at'),
    )

class GenerationLog(Base):
    """Track portfolio generation events for analytics"""
    __tablename__ = "generation_logs"
    
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String(36), ForeignKey("users.id"), nullable=True, index=True)
    session_id = Column(String(36), nullable=False)
    prompt = Column(Text)
    framework = Column(String(50))  # nextjs, react, vue, etc.
    success = Column(Boolean, default=True)
    error_message = Column(Text, nullable=True)
    generation_time_seconds = Column(Float)
    file_count = Column(Integer)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationship
    user = relationship("User", back_populates="generation_logs")
    
    __table_args__ = (
        Index('idx_genlog_user_created', 'user_id', 'created_at'),
        Index('idx_genlog_success', 'success'),
    )

class Deployment(Base):
    """Track portfolio deployments"""
    __tablename__ = "deployments"
    
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String(36), ForeignKey("users.id"), nullable=False, index=True)
    session_id = Column(String(36), ForeignKey("sessions.id"), nullable=False)
    project_id = Column(String(36), ForeignKey("projects.id"), nullable=True)
    platform = Column(String(50))  # vercel, netlify
    deployment_id = Column(String(255))
    deployment_url = Column(String(255), nullable=True)
    status = Column(String(50))  # pending, success, failed
    error_message = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    
    # Relationship
    user = relationship("User", back_populates="deployments")

class Asset(Base):
    """Store uploaded assets (images, logos, etc.)"""
    __tablename__ = "assets"
    
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String(36), ForeignKey("users.id"), nullable=False, index=True)
    session_id = Column(String(36), nullable=True)
    asset_type = Column(String(50))  # image, logo, icon, etc.
    filename = Column(String(255))
    url = Column(String(500))  # Cloudinary URL
    cloudinary_public_id = Column(String(255), nullable=True)  # For deletion
    size_bytes = Column(Integer)
    content_type = Column(String(50))
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationship
    user = relationship("User", back_populates="assets")
