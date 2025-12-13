"""
Input Validation Utilities
Provides reusable validators and sanitizers for API inputs
"""

import re
import bleach
from typing import Any, Union
from pydantic import field_validator


class InputValidators:
    """Collection of reusable input validators"""
    
    # Regex patterns
    EMAIL_PATTERN = re.compile(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$')
    NIGERIAN_PHONE_PATTERN = re.compile(r'^(\+234|0)[789][01]\d{8}$')
    ALPHANUMERIC_PATTERN = re.compile(r'^[a-zA-Z0-9\s]+$')
    URL_PATTERN = re.compile(r'^https?://[\w\-]+(\.[\w\-]+)+[/#?]?.*$')
    
    @staticmethod
    def validate_email(email: str) -> str:
        """Validate email format"""
        if not InputValidators.EMAIL_PATTERN.match(email):
            raise ValueError('Invalid email format')
        if len(email) > 254:  # RFC 5321
            raise ValueError('Email address too long')
        return email.lower().strip()
    
    @staticmethod
    def validate_nigerian_phone(phone: str) -> str:
        """Validate Nigerian phone number format"""
        # Remove spaces and dashes
        clean_phone = phone.replace(' ', '').replace('-', '')
        
        if not InputValidators.NIGERIAN_PHONE_PATTERN.match(clean_phone):
            raise ValueError('Invalid Nigerian phone number. Use format: +2348012345678 or 08012345678')
        
        return clean_phone
    
    @staticmethod
    def validate_string_length(value: str, min_len: int = 1, max_len: int = 255, field_name: str = "Field") -> str:
        """Validate string length"""
        value = value.strip()
        if len(value) < min_len:
            raise ValueError(f'{field_name} must be at least {min_len} characters')
        if len(value) > max_len:
            raise ValueError(f'{field_name} must not exceed {max_len} characters')
        return value
    
    @staticmethod
    def validate_alphanumeric(value: str, allow_spaces: bool = True) -> str:
        """Validate alphanumeric with optional spaces"""
        if not allow_spaces:
            value = value.replace(' ', '')
        
        if not InputValidators.ALPHANUMERIC_PATTERN.match(value):
            raise ValueError('Only alphanumeric characters and spaces allowed')
        
        return value.strip()
    
    @staticmethod
    def sanitize_html(value: str) -> str:
        """Remove all HTML tags and scripts"""
        # Strip all HTML tags
        clean_text = bleach.clean(value, tags=[], strip=True)
        return clean_text.strip()
    
    @staticmethod
    def validate_url(url: str) -> str:
        """Validate URL format"""
        if not InputValidators.URL_PATTERN.match(url):
            raise ValueError('Invalid URL format. Must start with http:// or https://')
        if len(url) > 2048:
            raise ValueError('URL too long')
        return url.strip()
    
    @staticmethod
    def validate_password_strength(password: str) -> str:
        """Validate password meets minimum security requirements"""
        if len(password) < 8:
            raise ValueError('Password must be at least 8 characters')
        
        # Check for at least one letter and one number
        has_letter = bool(re.search(r'[a-zA-Z]', password))
        has_number = bool(re.search(r'\d', password))
        
        if not (has_letter and has_number):
            raise ValueError('Password must contain at least one letter and one number')
        
        return password
    
    @staticmethod
    def validate_numeric_range(value: Union[int, float], min_val: Union[int, float], max_val: Union[int, float], field_name: str = "Value") -> Union[int, float]:
        """Validate numeric value is within range"""
        if value < min_val:
            raise ValueError(f'{field_name} must be at least {min_val}')
        if value > max_val:
            raise ValueError(f'{field_name} must not exceed {max_val}')
        return value


# Pydantic field validators (can be reused across models)
def email_validator(cls, v: str) -> str:
    """Reusable email validator for Pydantic models"""
    return InputValidators.validate_email(v)


def phone_validator(cls, v: str) -> str:
    """Reusable phone validator for Pydantic models"""
    return InputValidators.validate_nigerian_phone(v)


def name_validator(cls, v: str) -> str:
    """Reusable name validator"""
    return InputValidators.validate_string_length(
        InputValidators.sanitize_html(v), 
        min_len=2, 
        max_len=100, 
        field_name="Name"
    )
