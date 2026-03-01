"""
Database Configuration and Models
==================================

This module handles all database-related operations including:
- Database connection setup
- SQLAlchemy ORM configuration
- Database models (User, File, AISession)
- Database initialization

Author: Manus AI
Version: 1.0.0
"""

from sqlalchemy import create_engine, Column, Integer, String, Text, DateTime, Boolean, Enum
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
from datetime import datetime
import os
from typing import Optional
import enum

# Database URL - uses SQLite for development
# For production, use PostgreSQL: postgresql://user:password@localhost/dbname
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./rizwan_ai.db")

# Create database engine
# echo=True will print all SQL queries (useful for debugging)
engine = create_engine(
    DATABASE_URL,
    connect_args={"check_same_thread": False} if "sqlite" in DATABASE_URL else {},
    echo=False
)

# Create session factory
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Base class for all models
Base = declarative_base()


# ============================================================================
# DATABASE MODELS
# ============================================================================

class User(Base):
    """
    User model - represents a user in the system.
    
    Attributes:
        id: Unique user identifier
        username: Unique username for login
        email: User's email address
        hashed_password: Bcrypt hashed password (never store plain text!)
        full_name: User's full name
        is_active: Whether the user account is active
        created_at: Account creation timestamp
        updated_at: Last update timestamp
    """
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(50), unique=True, index=True, nullable=False)
    email = Column(String(100), unique=True, index=True, nullable=False)
    hashed_password = Column(String(255), nullable=False)
    full_name = Column(String(100))
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def __repr__(self) -> str:
        return f"<User(id={self.id}, username='{self.username}', email='{self.email}')>"


class FileUpload(Base):
    """
    FileUpload model - tracks uploaded files.
    
    Attributes:
        id: Unique file identifier
        user_id: ID of the user who uploaded the file
        filename: Original filename
        file_path: Path where file is stored on server
        file_size: Size of file in bytes
        file_type: MIME type of file (e.g., 'application/pdf')
        uploaded_at: When the file was uploaded
    """
    __tablename__ = "file_uploads"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, nullable=False)
    filename = Column(String(255), nullable=False)
    file_path = Column(String(500), nullable=False)
    file_size = Column(Integer)  # in bytes
    file_type = Column(String(100))  # MIME type
    uploaded_at = Column(DateTime, default=datetime.utcnow)
    
    def __repr__(self) -> str:
        return f"<FileUpload(id={self.id}, filename='{self.filename}', user_id={self.user_id})>"


class AISessionStatus(str, enum.Enum):
    """Enum for AI session status"""
    ACTIVE = "active"
    COMPLETED = "completed"
    FAILED = "failed"
    PENDING = "pending"


class AISession(Base):
    """
    AISession model - tracks AI interaction sessions.
    
    Attributes:
        id: Unique session identifier
        user_id: ID of the user who initiated the session
        session_name: Name/title of the session
        status: Current status of the session
        input_text: User's input/prompt
        output_text: AI's response
        model_used: Which AI model was used
        created_at: When the session was created
        updated_at: Last update timestamp
    """
    __tablename__ = "ai_sessions"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, nullable=False)
    session_name = Column(String(255))
    status = Column(Enum(AISessionStatus), default=AISessionStatus.PENDING)
    input_text = Column(Text)
    output_text = Column(Text)
    model_used = Column(String(100))
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def __repr__(self) -> str:
        return f"<AISession(id={self.id}, user_id={self.user_id}, status='{self.status}')>"


# ============================================================================
# DATABASE INITIALIZATION
# ============================================================================

def init_db():
    """
    Initialize the database by creating all tables.
    
    Call this function once when starting the application:
        from database import init_db
        init_db()
    """
    Base.metadata.create_all(bind=engine)
    print("✅ Database tables created successfully")


def get_db() -> Session:
    """
    Dependency function to get database session.
    
    Usage in FastAPI routes:
        @app.get("/users")
        def get_users(db: Session = Depends(get_db)):
            return db.query(User).all()
    
    Yields:
        Session: SQLAlchemy database session
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# ============================================================================
# DATABASE UTILITY FUNCTIONS
# ============================================================================

def create_user(db: Session, username: str, email: str, hashed_password: str, full_name: Optional[str] = None) -> User:
    """
    Create a new user in the database.
    
    Args:
        db: Database session
        username: Unique username
        email: User's email
        hashed_password: Already hashed password (use bcrypt)
        full_name: Optional full name
        
    Returns:
        User: The created user object
    """
    db_user = User(
        username=username,
        email=email,
        hashed_password=hashed_password,
        full_name=full_name
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user


def get_user_by_username(db: Session, username: str) -> Optional[User]:
    """
    Retrieve a user by username.
    
    Args:
        db: Database session
        username: Username to search for
        
    Returns:
        User or None: The user if found, None otherwise
    """
    return db.query(User).filter(User.username == username).first()


def get_user_by_id(db: Session, user_id: int) -> Optional[User]:
    """
    Retrieve a user by ID.
    
    Args:
        db: Database session
        user_id: User ID to search for
        
    Returns:
        User or None: The user if found, None otherwise
    """
    return db.query(User).filter(User.id == user_id).first()


def save_file_record(db: Session, user_id: int, filename: str, file_path: str, 
                     file_size: int, file_type: str) -> FileUpload:
    """
    Save a file upload record to the database.
    
    Args:
        db: Database session
        user_id: ID of user who uploaded the file
        filename: Original filename
        file_path: Path where file is stored
        file_size: Size of file in bytes
        file_type: MIME type of file
        
    Returns:
        FileUpload: The created file record
    """
    db_file = FileUpload(
        user_id=user_id,
        filename=filename,
        file_path=file_path,
        file_size=file_size,
        file_type=file_type
    )
    db.add(db_file)
    db.commit()
    db.refresh(db_file)
    return db_file


def create_ai_session(db: Session, user_id: int, session_name: str, 
                     input_text: str, model_used: str) -> AISession:
    """
    Create a new AI session record.
    
    Args:
        db: Database session
        user_id: ID of user initiating the session
        session_name: Name of the session
        input_text: User's input/prompt
        model_used: Name of the AI model used
        
    Returns:
        AISession: The created session record
    """
    db_session = AISession(
        user_id=user_id,
        session_name=session_name,
        input_text=input_text,
        status=AISessionStatus.PENDING,
        model_used=model_used
    )
    db.add(db_session)
    db.commit()
    db.refresh(db_session)
    return db_session


def update_ai_session(db: Session, session_id: int, output_text: str, 
                     status: AISessionStatus) -> Optional[AISession]:
    """
    Update an AI session with output and status.
    
    Args:
        db: Database session
        session_id: ID of session to update
        output_text: AI's response text
        status: New status of the session
        
    Returns:
        AISession or None: The updated session if found
    """
    db_session = db.query(AISession).filter(AISession.id == session_id).first()
    if db_session:
        db_session.output_text = output_text
        db_session.status = status
        db_session.updated_at = datetime.utcnow()
        db.commit()
        db.refresh(db_session)
    return db_session
