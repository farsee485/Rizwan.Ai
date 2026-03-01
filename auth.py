"""
Authentication Module
=====================

This module handles all authentication-related operations:
- Password hashing and verification using bcrypt
- JWT token creation and validation
- User authentication logic
- Token refresh mechanisms

Author: Manus AI
Version: 1.0.0
"""

from datetime import datetime, timedelta, timezone
from typing import Optional, Dict, Any
from jose import JWTError, jwt
from passlib.context import CryptContext
import os

# ============================================================================
# CONFIGURATION
# ============================================================================

# Secret key for JWT encoding - CHANGE THIS IN PRODUCTION!
SECRET_KEY = os.getenv("SECRET_KEY", "your-secret-key-change-this-in-production")

# JWT algorithm
ALGORITHM = "HS256"

# Token expiration time (in minutes)
ACCESS_TOKEN_EXPIRE_MINUTES = 30
REFRESH_TOKEN_EXPIRE_DAYS = 7

# Password hashing context
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


# ============================================================================
# PASSWORD HASHING
# ============================================================================

def hash_password(password: str) -> str:
    """
    Hash a password using bcrypt.
    
    Args:
        password: Plain text password to hash
        
    Returns:
        str: Hashed password
        
    Example:
        hashed = hash_password("mypassword123")
    """
    return pwd_context.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    Verify a plain text password against a hashed password.
    
    Args:
        plain_password: Plain text password to verify
        hashed_password: Hashed password from database
        
    Returns:
        bool: True if password matches, False otherwise
        
    Example:
        is_valid = verify_password("mypassword123", hashed_from_db)
    """
    return pwd_context.verify(plain_password, hashed_password)


# ============================================================================
# JWT TOKEN HANDLING
# ============================================================================

def create_access_token(data: Dict[str, Any], expires_delta: Optional[timedelta] = None) -> str:
    """
    Create a JWT access token.
    
    Args:
        data: Dictionary containing token claims (e.g., {"sub": "user_id"})
        expires_delta: Optional custom expiration time
        
    Returns:
        str: Encoded JWT token
        
    Example:
        token = create_access_token({"sub": "user123"})
    """
    to_encode = data.copy()
    
    # Set expiration time
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    
    to_encode.update({"exp": expire})
    
    # Encode token
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


def create_refresh_token(data: Dict[str, Any]) -> str:
    """
    Create a JWT refresh token with longer expiration.
    
    Args:
        data: Dictionary containing token claims
        
    Returns:
        str: Encoded refresh token
        
    Example:
        refresh_token = create_refresh_token({"sub": "user123"})
    """
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS)
    to_encode.update({"exp": expire})
    
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


def verify_token(token: str) -> Optional[Dict[str, Any]]:
    """
    Verify and decode a JWT token.
    
    Args:
        token: JWT token to verify
        
    Returns:
        dict or None: Decoded token payload if valid, None if invalid
        
    Example:
        payload = verify_token(token_string)
        if payload:
            user_id = payload.get("sub")
    """
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload
    except JWTError as e:
        print(f"Token verification failed: {str(e)}")
        return None


def get_user_id_from_token(token: str) -> Optional[str]:
    """
    Extract user ID from a JWT token.
    
    Args:
        token: JWT token
        
    Returns:
        str or None: User ID if token is valid, None otherwise
        
    Example:
        user_id = get_user_id_from_token(token)
    """
    payload = verify_token(token)
    if payload:
        return payload.get("sub")
    return None


# ============================================================================
# TOKEN RESPONSE MODELS
# ============================================================================

class TokenResponse:
    """
    Represents a token response with access and refresh tokens.
    
    Attributes:
        access_token: JWT access token
        refresh_token: JWT refresh token
        token_type: Type of token (always "bearer")
        expires_in: Seconds until access token expires
    """
    
    def __init__(self, access_token: str, refresh_token: str, expires_in: int = ACCESS_TOKEN_EXPIRE_MINUTES * 60):
        self.access_token = access_token
        self.refresh_token = refresh_token
        self.token_type = "bearer"
        self.expires_in = expires_in
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON response"""
        return {
            "access_token": self.access_token,
            "refresh_token": self.refresh_token,
            "token_type": self.token_type,
            "expires_in": self.expires_in
        }


# ============================================================================
# AUTHENTICATION HELPERS
# ============================================================================

def create_tokens_for_user(user_id: int) -> TokenResponse:
    """
    Create both access and refresh tokens for a user.
    
    Args:
        user_id: ID of the user
        
    Returns:
        TokenResponse: Object containing both tokens
        
    Example:
        tokens = create_tokens_for_user(user.id)
        return tokens.to_dict()
    """
    access_token = create_access_token({"sub": str(user_id)})
    refresh_token = create_refresh_token({"sub": str(user_id)})
    
    return TokenResponse(
        access_token=access_token,
        refresh_token=refresh_token,
        expires_in=ACCESS_TOKEN_EXPIRE_MINUTES * 60
    )


def validate_token_and_get_user_id(token: str) -> Optional[int]:
    """
    Validate a token and return the user ID if valid.
    
    Args:
        token: JWT token to validate
        
    Returns:
        int or None: User ID if token is valid, None otherwise
        
    Example:
        user_id = validate_token_and_get_user_id(token)
        if user_id:
            user = get_user_by_id(db, user_id)
    """
    try:
        user_id_str = get_user_id_from_token(token)
        if user_id_str:
            return int(user_id_str)
    except (ValueError, TypeError):
        pass
    return None
