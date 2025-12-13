from app.core.security import get_encryption_cipher

class EncryptionService:
    
    def encrypt(self, data: str) -> str:
        if not data:
            return ""
        cipher = get_encryption_cipher()
        return cipher.encrypt(data.encode()).decode()
    
    def decrypt(self, encrypted_data: str) -> str:
        if not encrypted_data:
            return ""
        cipher = get_encryption_cipher()
        return cipher.decrypt(encrypted_data.encode()).decode()

encryption_service = EncryptionService()