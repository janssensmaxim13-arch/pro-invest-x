# ============================================================================
# ProInvestiX Enterprise API - Security
# JWT Authentication & Password Hashing
# ============================================================================

from datetime import datetime, timedelta
from typing import Any, Optional, Union

from jose import JWTError, jwt
from passlib.context import CryptContext
from pydantic import BaseModel

from app.config import settings

# =============================================================================
# PASSWORD HASHING
# =============================================================================

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a plain password against a hashed password."""
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password: str) -> str:
    """Hash a password."""
    return pwd_context.hash(password)


# =============================================================================
# JWT TOKENS
# =============================================================================

class TokenPayload(BaseModel):
    """JWT token payload structure."""
    sub: str  # Subject (user_id or username)
    exp: datetime  # Expiration time
    type: str  # Token type: "access" or "refresh"
    role: Optional[str] = None


def create_access_token(
    subject: Union[str, Any],
    role: str = None,
    expires_delta: Optional[timedelta] = None,
) -> str:
    """
    Create a JWT access token.
    
    Args:
        subject: The subject of the token (usually user_id)
        role: User role for authorization
        expires_delta: Custom expiration time
    
    Returns:
        Encoded JWT token string
    """
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(
            minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES
        )
    
    to_encode = {
        "sub": str(subject),
        "exp": expire,
        "type": "access",
        "role": role,
    }
    
    encoded_jwt = jwt.encode(
        to_encode,
        settings.SECRET_KEY,
        algorithm=settings.ALGORITHM,
    )
    
    return encoded_jwt


def create_refresh_token(
    subject: Union[str, Any],
    expires_delta: Optional[timedelta] = None,
) -> str:
    """
    Create a JWT refresh token.
    
    Args:
        subject: The subject of the token (usually user_id)
        expires_delta: Custom expiration time
    
    Returns:
        Encoded JWT token string
    """
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(
            days=settings.REFRESH_TOKEN_EXPIRE_DAYS
        )
    
    to_encode = {
        "sub": str(subject),
        "exp": expire,
        "type": "refresh",
    }
    
    encoded_jwt = jwt.encode(
        to_encode,
        settings.SECRET_KEY,
        algorithm=settings.ALGORITHM,
    )
    
    return encoded_jwt


def decode_token(token: str) -> Optional[TokenPayload]:
    """
    Decode and validate a JWT token.
    
    Args:
        token: The JWT token string
    
    Returns:
        TokenPayload if valid, None otherwise
    """
    try:
        payload = jwt.decode(
            token,
            settings.SECRET_KEY,
            algorithms=[settings.ALGORITHM],
        )
        return TokenPayload(**payload)
    except JWTError:
        return None


def verify_token(token: str, token_type: str = "access") -> Optional[TokenPayload]:
    """
    Verify a JWT token and check its type.
    
    Args:
        token: The JWT token string
        token_type: Expected token type ("access" or "refresh")
    
    Returns:
        TokenPayload if valid and correct type, None otherwise
    """
    payload = decode_token(token)
    if payload is None:
        return None
    if payload.type != token_type:
        return None
    return payload
