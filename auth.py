"""
Authentication Routes
=====================

API endpoints for user authentication:
- User registration
- User login
- Token refresh
- Logout

Endpoints:
- POST /api/auth/register - Register new user
- POST /api/auth/login - Login user
- POST /api/auth/refresh - Refresh access token
- POST /api/auth/logout - Logout user

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
from database import get_db, User, create_user, get_user_by_username, get_user_by_id
from auth import (
    hash_password, verify_password, create_tokens_for_user,
    validate_token_and_get_user_id, verify_token
)

logger = logging.getLogger(__name__)
router = APIRouter()


# ============================================================================
# REQUEST/RESPONSE MODELS
# ============================================================================

class UserRegisterRequest(BaseModel):
    """User registration request model"""
    username: str = Field(..., min_length=3, max_length=50, description="Username (3-50 chars)")
    email: EmailStr = Field(..., description="Valid email address")
    password: str = Field(..., min_length=8, description="Password (minimum 8 chars)")
    full_name: Optional[str] = Field(None, max_length=100, description="Full name")
    
    class Config:
        json_schema_extra = {
            "example": {
                "username": "johndoe",
                "email": "john@example.com",
                "password": "securepassword123",
                "full_name": "John Doe"
            }
        }


class UserLoginRequest(BaseModel):
    """User login request model"""
    username: str = Field(..., description="Username or email")
    password: str = Field(..., description="Password")
    
    class Config:
        json_schema_extra = {
            "example": {
                "username": "johndoe",
                "password": "securepassword123"
            }
        }


class TokenRefreshRequest(BaseModel):
    """Token refresh request model"""
    refresh_token: str = Field(..., description="Refresh token")
    
    class Config:
        json_schema_extra = {
            "example": {
                "refresh_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
            }
        }


class TokenResponse(BaseModel):
    """Token response model"""
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    expires_in: int
    
    class Config:
        json_schema_extra = {
            "example": {
                "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
                "refresh_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
                "token_type": "bearer",
                "expires_in": 1800
            }
        }


class UserResponse(BaseModel):
    """User response model (for API responses)"""
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


class MessageResponse(BaseModel):
    """Generic message response"""
    message: str
    success: bool = True


# ============================================================================
# DEPENDENCY: GET CURRENT USER
# ============================================================================

async def get_current_user(
    authorization: str = None,
    db: Session = Depends(get_db)
) -> User:
    """
    Dependency to get the current authenticated user from JWT token.
    
    Args:
        authorization: Authorization header (Bearer token)
        db: Database session
        
    Returns:
        User: The authenticated user
        
    Raises:
        HTTPException: If token is invalid or user not found
        
    Usage in routes:
        @app.get("/protected")
        def protected_route(current_user: User = Depends(get_current_user)):
            return {"message": f"Hello {current_user.username}"}
    """
    if not authorization:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Missing authorization header",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # Extract token from "Bearer <token>"
    try:
        scheme, token = authorization.split()
        if scheme.lower() != "bearer":
            raise ValueError("Invalid authentication scheme")
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authorization header format",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # Validate token and get user ID
    user_id = validate_token_and_get_user_id(token)
    if user_id is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # Get user from database
    user = get_user_by_id(db, user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found",
        )
    
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User account is inactive",
        )
    
    return user


# ============================================================================
# ROUTES
# ============================================================================

@router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def register(request: UserRegisterRequest, db: Session = Depends(get_db)):
    """
    Register a new user.
    
    Args:
        request: Registration request with username, email, password
        db: Database session
        
    Returns:
        UserResponse: Created user information
        
    Raises:
        HTTPException: If username or email already exists
        
    Example:
        POST /api/auth/register
        {
            "username": "johndoe",
            "email": "john@example.com",
            "password": "securepassword123",
            "full_name": "John Doe"
        }
    """
    # Check if username already exists
    existing_user = get_user_by_username(db, request.username)
    if existing_user:
        logger.warning(f"Registration failed: Username '{request.username}' already exists")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Username already registered"
        )
    
    # Hash password
    hashed_password = hash_password(request.password)
    
    # Create user
    try:
        user = create_user(
            db=db,
            username=request.username,
            email=request.email,
            hashed_password=hashed_password,
            full_name=request.full_name
        )
        logger.info(f"✅ New user registered: {request.username}")
        return user
    
    except Exception as e:
        logger.error(f"Error creating user: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to create user"
        )


@router.post("/login", response_model=TokenResponse)
async def login(request: UserLoginRequest, db: Session = Depends(get_db)):
    """
    Login user and return JWT tokens.
    
    Args:
        request: Login request with username and password
        db: Database session
        
    Returns:
        TokenResponse: Access token, refresh token, and expiration info
        
    Raises:
        HTTPException: If credentials are invalid
        
    Example:
        POST /api/auth/login
        {
            "username": "johndoe",
            "password": "securepassword123"
        }
    """
    # Get user by username
    user = get_user_by_username(db, request.username)
    
    if not user:
        logger.warning(f"Login failed: User '{request.username}' not found")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid username or password"
        )
    
    # Verify password
    if not verify_password(request.password, user.hashed_password):
        logger.warning(f"Login failed: Invalid password for user '{request.username}'")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid username or password"
        )
    
    if not user.is_active:
        logger.warning(f"Login failed: User '{request.username}' is inactive")
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User account is inactive"
        )
    
    # Create tokens
    tokens = create_tokens_for_user(user.id)
    logger.info(f"✅ User logged in: {request.username}")
    
    return tokens.to_dict()


@router.post("/refresh", response_model=TokenResponse)
async def refresh_token(request: TokenRefreshRequest, db: Session = Depends(get_db)):
    """
    Refresh access token using refresh token.
    
    Args:
        request: Refresh token request
        db: Database session
        
    Returns:
        TokenResponse: New access token
        
    Raises:
        HTTPException: If refresh token is invalid
        
    Example:
        POST /api/auth/refresh
        {
            "refresh_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
        }
    """
    # Verify refresh token
    payload = verify_token(request.refresh_token)
    if not payload:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired refresh token"
        )
    
    # Get user ID from token
    user_id_str = payload.get("sub")
    if not user_id_str:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token payload"
        )
    
    try:
        user_id = int(user_id_str)
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid user ID in token"
        )
    
    # Get user from database
    user = get_user_by_id(db, user_id)
    if not user or not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found or inactive"
        )
    
    # Create new tokens
    tokens = create_tokens_for_user(user.id)
    logger.info(f"✅ Token refreshed for user ID: {user_id}")
    
    return tokens.to_dict()


@router.post("/logout", response_model=MessageResponse)
async def logout(current_user: User = Depends(get_current_user)):
    """
    Logout user (client-side token deletion).
    
    Note: JWT tokens cannot be revoked server-side. The client should delete
    the token from localStorage/sessionStorage. For production, implement
    a token blacklist in Redis or database.
    
    Args:
        current_user: Current authenticated user
        
    Returns:
        MessageResponse: Logout confirmation
        
    Example:
        POST /api/auth/logout
        Headers: Authorization: Bearer <token>
    """
    logger.info(f"✅ User logged out: {current_user.username}")
    return {
        "message": "Successfully logged out. Please delete tokens from client storage.",
        "success": True
    }


@router.get("/me", response_model=UserResponse)
async def get_me(current_user: User = Depends(get_current_user)):
    """
    Get current authenticated user information.
    
    Args:
        current_user: Current authenticated user
        
    Returns:
        UserResponse: Current user information
        
    Example:
        GET /api/auth/me
        Headers: Authorization: Bearer <token>
    """
    return current_user
