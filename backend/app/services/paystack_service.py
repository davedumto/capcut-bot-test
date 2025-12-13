import requests
import hmac
import hashlib
from app.core.config import settings

class PaystackService:
    
    def __init__(self):
        self.secret_key = settings.paystack_secret_key
        self.base_url = "https://api.paystack.co"
    
    def initialize_transaction(self, email: str, amount: int, reference: str, callback_path: str = "/payment/verify"):
        url = f"{self.base_url}/transaction/initialize"
        headers = {
            "Authorization": f"Bearer {self.secret_key}",
            "Content-Type": "application/json"
        }
        data = {
            "email": email,
            "amount": amount,  # In kobo
            "reference": reference,
            "callback_url": f"{settings.frontend_url}{callback_path}"
        }
        
        response = requests.post(url, json=data, headers=headers)
        return response.json()
    
    def verify_transaction(self, reference: str):
        url = f"{self.base_url}/transaction/verify/{reference}"
        headers = {"Authorization": f"Bearer {self.secret_key}"}
        
        response = requests.get(url, headers=headers)
        return response.json()
    
    def charge_authorization(self, authorization_code: str, email: str, amount: int):
        """Charge a saved card for recurring billing"""
        url = f"{self.base_url}/transaction/charge_authorization"
        headers = {
            "Authorization": f"Bearer {self.secret_key}",
            "Content-Type": "application/json"
        }
        data = {
            "authorization_code": authorization_code,
            "email": email,
            "amount": amount
        }
        
        response = requests.post(url, json=data, headers=headers)
        return response.json()
    
    def verify_signature(self, body: bytes, signature: str) -> bool:
        computed = hmac.new(
            self.secret_key.encode(),
            body,
            hashlib.sha512
        ).hexdigest()
        return computed == signature

paystack_service = PaystackService()
