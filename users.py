"""
User Management Routes
======================

API endpoints for user management:
- Get user profile
- Update user profile
- Delete user account

Endpoints:
- GET /api/users/profile - Get user profile
- PUT /api/users/profile - Update user profile
- DELETE /api/users/account - Delete account

Author: Manus AI
Version: 1.0.0
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from pydantic import BaseModel, EmailStr, Field
from typing import Optional
import logging

# Import from parent modules
import sys
sys.path.append('..')
from database import get_db, User
from routes.auth import get_current_user

logger = logging.getLogger(__name__)
router = APIRouter()


# ============================================================================
# REQUEST/RESPONSE MODELS
# ============================================================================

class UserProfileResponse(BaseModel):
    """User profile response"""
    id: int
    username: str
    email: str
    full_name: Optional[str]
    is_active: bool
    
    class Config:
        from_attributes = True
        json_schema_extra = {
            "example": {
                "id": 1,
                "username": "johndoe",
                "email": "john@example.com",
                "full_name": "John Doe",
                "is_active": True
            }
        }


class UpdateProfileRequest(BaseModel):
    """Update profile request"""
    full_name: Optional[str] = Field(None, max_length=100, description="Full name")
    email: Optional[EmailStr] = Field(None, description="Email address")
    
    class Config:
        json_schema_extra = {
            "example": {
                "full_name": "John Doe",
                "email": "newemail@example.com"
            }
        }


class MessageResponse(BaseModel):
    """Generic message response"""
    message: str
    success: bool = True


# ============================================================================
# ROUTES
# ============================================================================

@router.get("/profile", response_model=UserProfileResponse)
async def get_profile(current_user: User = Depends(get_current_user)):
    """
    Get current user's profile information.
    
    Args:
        current_user: Current authenticated user
        
    Returns:
        UserProfileResponse: User profile information
        
    Example:
        GET /api/users/profile
        Headers: Authorization: Bearer <token>
    """
    logger.info(f"Profile retrieved for user {current_user.username}")
    return current_user


@router.put("/profile", response_model=UserProfileResponse)
async def update_profile(
    request: UpdateProfileRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Update current user's profile information.
    
    Args:
        request: Update profile request
        current_user: Current authenticated user
        db: Database session
        
    Returns:
        UserProfileResponse: Updated user profile
        
    Raises:
        HTTPException: If email already exists
        
    Example:
        PUT /api/users/profile
        Headers: Authorization: Bearer <token>
        Body: {
            "full_name": "John Doe",
            "email": "newemail@example.com"
        }
    """
    try:
        # Update full name if provided
        if request.full_name is not None:
            current_user.full_name = request.full_name
        
        # Update email if provided
        if request.email is not None:
            # Check if email is already used by another user
            existing_user = db.query(User).filter(
                User.email == request.email,
                User.id != current_user.id
            ).first()
            
            if existing_user:
                logger.warning(f"Email update failed: Email already in use")
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Email already in use"
                )
            
            current_user.email = request.email
        
        # Commit changes
        db.commit()
        db.refresh(current_user)
        
        logger.info(f"✅ Profile updated for user {current_user.username}")
        return current_user
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error updating profile: {str(e)}")
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to update profile"
        )


@router.delete("/account", response_model=MessageResponse)
async def delete_account(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Delete current user's account.
    
    WARNING: This action is irreversible!
    
    Args:
        current_user: Current authenticated user
        db: Database session
        
    Returns:
        MessageResponse: Deletion confirmation
        
    Example:
        DELETE /api/users/account
        Headers: Authorization: Bearer <token>
    """
    try:
        username = current_user.username
        
        # Delete user from database
        db.delete(current_user)
        db.commit()
        
        logger.warning(f"⚠️ User account deleted: {username}")
        
        return {
            "message": "User account deleted successfully. Please clear your tokens.",
            "success": True
        }
    
    except Exception as e:
        logger.error(f"Error deleting account: {str(e)}")
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to delete account"
        )
