"""
Password generation and encryption service
As specified in instructions.md
"""

import secrets
import string
import bcrypt
import pytz
from cryptography.fernet import Fernet
from app.core.config import settings
import logging
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)

# West Africa Time (UTC+1)
WAT_TZ = pytz.timezone('Africa/Lagos')
def get_wat_now():
    return datetime.now(WAT_TZ).replace(tzinfo=None)


class PasswordService:
    def __init__(self):
        # Use SECRET_KEY to generate consistent encryption key
        # Note: In production, store this securely
        secret_bytes = settings.secret_key.encode()[:32].ljust(32, b'0')  # Ensure 32 bytes
        
        # Generate a consistent Fernet key from SECRET_KEY
        import base64
        import hashlib
        
        # Create a 32-byte key using SHA-256 hash of secret
        key_hash = hashlib.sha256(secret_bytes).digest()
        # Fernet needs base64-encoded 32-byte key
        fernet_key = base64.urlsafe_b64encode(key_hash)
        self.cipher = Fernet(fernet_key)

    def generate_strong_password(self, length: int = 16) -> str:
        """
        Generate a strong password using secrets module
        As specified in instructions.md: 16 chars, mixed case, numbers, special chars
        """
        try:
            # Define character sets
            uppercase = string.ascii_uppercase
            lowercase = string.ascii_lowercase
            digits = string.digits
            special = "!@#$%^&*"
            
            # Ensure at least one character from each set
            password = [
                secrets.choice(uppercase),
                secrets.choice(lowercase), 
                secrets.choice(digits),
                secrets.choice(special)
            ]
            
            # Fill the rest randomly from all character sets
            all_chars = uppercase + lowercase + digits + special
            for _ in range(length - 4):
                password.append(secrets.choice(all_chars))
            
            # Shuffle the password list to avoid predictable patterns
            secrets.SystemRandom().shuffle(password)
            
            result = ''.join(password)
            logger.info(f"Generated strong password of length {len(result)}")
            return result
            
        except Exception as e:
            logger.error(f"Failed to generate password: {e}")
            # Fallback to simpler generation
            return secrets.token_urlsafe(16)

    def hash_password(self, password: str) -> str:
        """Hash password using bcrypt for database storage"""
        try:
            salt = bcrypt.gensalt()
            hashed = bcrypt.hashpw(password.encode('utf-8'), salt)
            return hashed.decode('utf-8')
        except Exception as e:
            logger.error(f"Failed to hash password: {e}")
            raise

    def verify_password(self, password: str, hashed: str) -> bool:
        """Verify password against hash"""
        try:
            return bcrypt.checkpw(password.encode('utf-8'), hashed.encode('utf-8'))
        except Exception as e:
            logger.error(f"Failed to verify password: {e}")
            return False

    def encrypt_password(self, password: str) -> str:
        """Encrypt password for temporary storage"""
        try:
            encrypted = self.cipher.encrypt(password.encode('utf-8'))
            return encrypted.decode('utf-8')
        except Exception as e:
            logger.error(f"Failed to encrypt password: {e}")
            raise

    def decrypt_password(self, encrypted_password: str) -> str:
        """Decrypt password from storage"""
        try:
            decrypted = self.cipher.decrypt(encrypted_password.encode('utf-8'))
            return decrypted.decode('utf-8')
        except Exception as e:
            logger.error(f"Failed to decrypt password: {e}")
            raise

    def create_password_entry(self, password: str, session_id: int) -> dict:
        """
        Create password entry for database
        Returns both hashed and encrypted versions
        As per instructions.md: Delete plain passwords after 1 hour
        """
        try:
            # Set expiration time to 1 hour from now (WAT)
            expires_at = get_wat_now() + timedelta(hours=1)
            
            return {
                "password_hash": self.hash_password(password),
                "plain_password": self.encrypt_password(password),
                "session_id": session_id,
                "is_active": True,
                "expires_at": expires_at
            }
        except Exception as e:
            logger.error(f"Failed to create password entry: {e}")
            raise
    
    def cleanup_expired_passwords(self):
        """
        Clean up expired plain text passwords from database
        As per instructions.md: Delete plain passwords after 1 hour
        """
        try:
            from app.models.database import SessionLocal, Password
            
            db = SessionLocal()
            try:
                current_time = get_wat_now()
                
                # Find expired passwords
                expired_passwords = db.query(Password).filter(
                    Password.expires_at <= current_time,
                    Password.plain_password.isnot(None)
                ).all()
                
                # Clear plain text passwords but keep hashes
                for pwd in expired_passwords:
                    pwd.plain_password = None
                    logger.info(f"Cleared expired plain password for session {pwd.session_id}")
                
                db.commit()
                logger.info(f"Cleaned up {len(expired_passwords)} expired passwords")
                
            finally:
                db.close()
                
        except Exception as e:
            logger.error(f"Failed to cleanup expired passwords: {e}")


# Singleton instance
password_service = PasswordService()