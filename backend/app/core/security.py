"""
Security utilities for password hashing, encryption, and JWT auth
As specified in instructions.md Phase 8 and Module 1
"""

import bcrypt
import secrets
from datetime import datetime, timedelta
from typing import Optional, Dict, Any
from cryptography.fernet import Fernet
from jose import JWTError, jwt
from app.core.config import settings
import logging

logger = logging.getLogger(__name__)


def hash_password(password: str) -> str:
    """Hash password using bcrypt for database storage"""
    try:
        salt = bcrypt.gensalt()
        hashed = bcrypt.hashpw(password.encode('utf-8'), salt)
        return hashed.decode('utf-8')
    except Exception as e:
        logger.error(f"Failed to hash password: {e}")
        raise


def verify_password(password: str, hashed: str) -> bool:
    """Verify password against hash"""
    try:
        return bcrypt.checkpw(password.encode('utf-8'), hashed.encode('utf-8'))
    except Exception as e:
        logger.error(f"Failed to verify password: {e}")
        return False


def get_encryption_cipher():
    """Get consistent encryption cipher from SECRET_KEY"""
    import base64
    import hashlib
    
    # Use SECRET_KEY to generate consistent encryption key
    secret_bytes = settings.secret_key.encode()[:32].ljust(32, b'0')
    key_hash = hashlib.sha256(secret_bytes).digest()
    fernet_key = base64.urlsafe_b64encode(key_hash)
    return Fernet(fernet_key)


def encrypt_password(password: str) -> str:
    """Encrypt password for temporary storage"""
    try:
        cipher = get_encryption_cipher()
        encrypted = cipher.encrypt(password.encode('utf-8'))
        return encrypted.decode('utf-8')
    except Exception as e:
        logger.error(f"Failed to encrypt password: {e}")
        raise


def decrypt_password(encrypted_password: str) -> str:
    """Decrypt password from storage"""
    try:
        cipher = get_encryption_cipher()
        decrypted = cipher.decrypt(encrypted_password.encode('utf-8'))
        return decrypted.decode('utf-8')
    except Exception as e:
        logger.error(f"Failed to decrypt password: {e}")
        raise


# JWT Auth utilities
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_DAYS = 7


def create_access_token(data: Dict[str, Any], expires_delta: Optional[timedelta] = None) -> str:
    """Create JWT access token"""
    to_encode = data.copy()
    
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(days=ACCESS_TOKEN_EXPIRE_DAYS)
    
    to_encode.update({"exp": expire})
    
    try:
        encoded_jwt = jwt.encode(to_encode, settings.secret_key, algorithm=ALGORITHM)
        return encoded_jwt
    except Exception as e:
        logger.error(f"Failed to create JWT token: {e}")
        raise


def verify_token(token: str) -> Optional[Dict[str, Any]]:
    """Verify and decode JWT token"""
    try:
        payload = jwt.decode(token, settings.secret_key, algorithms=[ALGORITHM])
        return payload
    except JWTError as e:
        logger.warning(f"JWT verification failed: {e}")
        return None


# Magic Link utilities
def generate_magic_token() -> str:
    """Generate secure 32-byte hex token for magic links"""
    return secrets.token_hex(32)


def generate_temp_password() -> str:
    """Generate temporary password for manager invites"""
    return secrets.token_urlsafe(12)


# FastAPI dependency for current user
from fastapi import HTTPException, Request
from fastapi.security import HTTPBearer
from sqlalchemy.orm import Session

security = HTTPBearer(auto_error=False)

def get_current_user(request: Request) -> dict:
    """Get current user from JWT token in cookies"""
    token = request.cookies.get("access_token")
    if not token:
        raise HTTPException(401, "Not authenticated")
    
    payload = verify_token(token)
    if not payload:
        raise HTTPException(401, "Invalid token")
    
    return payload