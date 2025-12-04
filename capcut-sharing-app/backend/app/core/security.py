"""
Security utilities for password hashing and encryption
As specified in instructions.md Phase 8
"""

import bcrypt
from cryptography.fernet import Fernet
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