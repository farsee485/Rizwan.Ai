"""
File Upload and Management Routes
==================================

API endpoints for file operations:
- File upload
- File listing
- File download
- File deletion

Endpoints:
- POST /api/files/upload - Upload a file
- GET /api/files - List user's files
- GET /api/files/{file_id} - Get file info
- DELETE /api/files/{file_id} - Delete a file

Author: Manus AI
Version: 1.0.0
"""

from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import List, Optional
import os
import logging
from datetime import datetime

# Import from parent modules
import sys
sys.path.append('..')
from database import get_db, User, FileUpload, save_file_record
from routes.auth import get_current_user

logger = logging.getLogger(__name__)
router = APIRouter()

# ============================================================================
# CONFIGURATION
# ============================================================================

# Upload directory
UPLOAD_DIR = os.getenv("UPLOAD_DIR", "./uploads")

# Maximum file size (10 MB)
MAX_FILE_SIZE = 10 * 1024 * 1024

# Allowed file types
ALLOWED_EXTENSIONS = {
    'pdf', 'txt', 'doc', 'docx', 'xls', 'xlsx',
    'jpg', 'jpeg', 'png', 'gif', 'bmp',
    'mp3', 'wav', 'mp4', 'avi'
}

# Create upload directory if it doesn't exist
os.makedirs(UPLOAD_DIR, exist_ok=True)


# ============================================================================
# REQUEST/RESPONSE MODELS
# ============================================================================

class FileUploadResponse(BaseModel):
    """File upload response model"""
    id: int
    filename: str
    file_size: int
    file_type: str
    uploaded_at: datetime
    
    class Config:
        from_attributes = True
        json_schema_extra = {
            "example": {
                "id": 1,
                "filename": "document.pdf",
                "file_size": 102400,
                "file_type": "application/pdf",
                "uploaded_at": "2024-01-15T10:30:00"
            }
        }


class FileListResponse(BaseModel):
    """File list response model"""
    total: int
    files: List[FileUploadResponse]
    
    class Config:
        json_schema_extra = {
            "example": {
                "total": 2,
                "files": [
                    {
                        "id": 1,
                        "filename": "document.pdf",
                        "file_size": 102400,
                        "file_type": "application/pdf",
                        "uploaded_at": "2024-01-15T10:30:00"
                    }
                ]
            }
        }


class MessageResponse(BaseModel):
    """Generic message response"""
    message: str
    success: bool = True


# ============================================================================
# UTILITY FUNCTIONS
# ============================================================================

def get_file_extension(filename: str) -> str:
    """Get file extension from filename"""
    return filename.rsplit('.', 1)[1].lower() if '.' in filename else ''


def is_file_allowed(filename: str) -> bool:
    """Check if file type is allowed"""
    ext = get_file_extension(filename)
    return ext in ALLOWED_EXTENSIONS


def generate_safe_filename(user_id: int, original_filename: str) -> str:
    """
    Generate a safe filename to prevent directory traversal attacks.
    
    Args:
        user_id: User ID
        original_filename: Original filename
        
    Returns:
        str: Safe filename with user ID prefix
    """
    # Remove path components
    filename = os.path.basename(original_filename)
    
    # Add timestamp and user ID for uniqueness
    timestamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
    name, ext = os.path.splitext(filename)
    
    # Limit filename length
    name = name[:50]
    
    return f"{user_id}_{timestamp}_{name}{ext}"


# ============================================================================
# ROUTES
# ============================================================================

@router.post("/upload", response_model=FileUploadResponse, status_code=status.HTTP_201_CREATED)
async def upload_file(
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Upload a file.
    
    Args:
        file: File to upload
        current_user: Current authenticated user
        db: Database session
        
    Returns:
        FileUploadResponse: Information about uploaded file
        
    Raises:
        HTTPException: If file type not allowed or size exceeds limit
        
    Example:
        POST /api/files/upload
        Headers: Authorization: Bearer <token>
        Body: multipart/form-data with file
    """
    # Check file size
    contents = await file.read()
    if len(contents) > MAX_FILE_SIZE:
        logger.warning(f"File upload rejected: File too large ({len(contents)} bytes)")
        raise HTTPException(
            status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
            detail=f"File size exceeds maximum allowed ({MAX_FILE_SIZE / 1024 / 1024:.1f} MB)"
        )
    
    # Check file type
    if not is_file_allowed(file.filename):
        logger.warning(f"File upload rejected: Invalid file type ({file.filename})")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"File type not allowed. Allowed types: {', '.join(ALLOWED_EXTENSIONS)}"
        )
    
    # Generate safe filename
    safe_filename = generate_safe_filename(current_user.id, file.filename)
    file_path = os.path.join(UPLOAD_DIR, safe_filename)
    
    # Save file to disk
    try:
        with open(file_path, "wb") as f:
            f.write(contents)
        logger.info(f"✅ File uploaded: {safe_filename} by user {current_user.username}")
    except Exception as e:
        logger.error(f"Error saving file: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to save file"
        )
    
    # Save file record to database
    try:
        db_file = save_file_record(
            db=db,
            user_id=current_user.id,
            filename=file.filename,
            file_path=file_path,
            file_size=len(contents),
            file_type=file.content_type or "application/octet-stream"
        )
        return db_file
    except Exception as e:
        logger.error(f"Error saving file record: {str(e)}")
        # Clean up uploaded file
        if os.path.exists(file_path):
            os.remove(file_path)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to save file record"
        )


@router.get("", response_model=FileListResponse)
async def list_files(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
    skip: int = 0,
    limit: int = 10
):
    """
    List all files uploaded by current user.
    
    Args:
        current_user: Current authenticated user
        db: Database session
        skip: Number of files to skip (pagination)
        limit: Maximum number of files to return
        
    Returns:
        FileListResponse: List of user's files
        
    Example:
        GET /api/files?skip=0&limit=10
        Headers: Authorization: Bearer <token>
    """
    try:
        # Query files for current user
        files = db.query(FileUpload).filter(
            FileUpload.user_id == current_user.id
        ).order_by(FileUpload.uploaded_at.desc()).offset(skip).limit(limit).all()
        
        # Get total count
        total = db.query(FileUpload).filter(
            FileUpload.user_id == current_user.id
        ).count()
        
        logger.info(f"Listed {len(files)} files for user {current_user.username}")
        
        return {
            "total": total,
            "files": files
        }
    except Exception as e:
        logger.error(f"Error listing files: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to list files"
        )


@router.get("/{file_id}", response_model=FileUploadResponse)
async def get_file_info(
    file_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get information about a specific file.
    
    Args:
        file_id: ID of the file
        current_user: Current authenticated user
        db: Database session
        
    Returns:
        FileUploadResponse: File information
        
    Raises:
        HTTPException: If file not found or unauthorized
        
    Example:
        GET /api/files/1
        Headers: Authorization: Bearer <token>
    """
    try:
        db_file = db.query(FileUpload).filter(FileUpload.id == file_id).first()
        
        if not db_file:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="File not found"
            )
        
        # Check if user owns the file
        if db_file.user_id != current_user.id:
            logger.warning(f"Unauthorized file access attempt by user {current_user.username}")
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You don't have permission to access this file"
            )
        
        return db_file
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting file info: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get file information"
        )


@router.delete("/{file_id}", response_model=MessageResponse)
async def delete_file(
    file_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Delete a file.
    
    Args:
        file_id: ID of the file to delete
        current_user: Current authenticated user
        db: Database session
        
    Returns:
        MessageResponse: Deletion confirmation
        
    Raises:
        HTTPException: If file not found or unauthorized
        
    Example:
        DELETE /api/files/1
        Headers: Authorization: Bearer <token>
    """
    try:
        db_file = db.query(FileUpload).filter(FileUpload.id == file_id).first()
        
        if not db_file:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="File not found"
            )
        
        # Check if user owns the file
        if db_file.user_id != current_user.id:
            logger.warning(f"Unauthorized file deletion attempt by user {current_user.username}")
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You don't have permission to delete this file"
            )
        
        # Delete file from disk
        if os.path.exists(db_file.file_path):
            try:
                os.remove(db_file.file_path)
            except Exception as e:
                logger.error(f"Error deleting file from disk: {str(e)}")
        
        # Delete file record from database
        db.delete(db_file)
        db.commit()
        
        logger.info(f"✅ File deleted: {db_file.filename} by user {current_user.username}")
        
        return {
            "message": "File deleted successfully",
            "success": True
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting file: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to delete file"
        )
