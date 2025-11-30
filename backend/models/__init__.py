from sqlalchemy import Column, String, Integer, DateTime, JSON, Text
from sqlalchemy.sql import func
from database import Base
import uuid

class User(Base):
    __tablename__ = "users"
    
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    email = Column(String(255), unique=True, nullable=False)
    hashed_password = Column(String(255), nullable=False)
    full_name = Column(String(255))
    created_at = Column(DateTime(timezone=True), server_default=func.now())

class Session(Base):
    __tablename__ = "sessions"
    
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String(36), nullable=True)  # Nullable for guest sessions if needed
    resume_filename = Column(String(255))
    resume_data = Column(JSON)
    user_prompt = Column(Text, nullable=True)  # User's portfolio description prompt
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

class Project(Base):
    __tablename__ = "projects"
    
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String(36), nullable=True)
    session_id = Column(String(36), nullable=False)
    name = Column(String(255))
    stack = Column(String(50))  # react, nextjs, vue, svelte
    files = Column(JSON)  # File structure as JSON
    customization = Column(JSON)  # Theme, colors, etc.
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

class ChatHistory(Base):
    __tablename__ = "chat_history"
    
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    session_id = Column(String(36), nullable=False)
    user_id = Column(String(36), nullable=True)
    role = Column(String(20))  # user, assistant
    message = Column(Text)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
