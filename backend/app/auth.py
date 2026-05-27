import logging
from datetime import datetime, timedelta, timezone

import jwt
from pwdlib import PasswordHash

from app.config import get_settings

logger = logging.getLogger(__name__)

pwd_hash = PasswordHash.recommended()


def hash_password(password: str) -> str:
    """Hash a plain-text password using Argon2."""
    return pwd_hash.hash(password)


def verify_password(plain: str, hashed: str) -> bool:
    """Verify a plain-text password against a stored hash."""
    return pwd_hash.verify(plain, hashed)


def create_access_token(data: dict) -> str:
    """Create a signed JWT containing the supplied claims."""
    settings = get_settings()
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire, "iat": datetime.now(timezone.utc)})
    return jwt.encode(to_encode, settings.JWT_SECRET, algorithm=settings.JWT_ALGORITHM)


def decode_access_token(token: str) -> dict:
    """Decode and validate a JWT, returning the payload dict."""
    settings = get_settings()
    return jwt.decode(token, settings.JWT_SECRET, algorithms=[settings.JWT_ALGORITHM])
