"""
Pydantic schemas for authentication with enhanced validation
Module 1: Authentication + Module 4: Input Validation
"""

from pydantic import BaseModel, EmailStr, field_validator, constr
from typing import Optional
from datetime import datetime
from app.utils.validators import InputValidators, name_validator


# Magic Link Requests
class MagicLinkRequest(BaseModel):
    email: EmailStr
    name: Optional[constr(min_length=2, max_length=100)] = None
    marketing_consent: bool = False
    
    @field_validator('name')
    @classmethod
    def validate_name(cls, v):
        if v:
            # Sanitize HTML and validate
            v = InputValidators.sanitize_html(v)
            return InputValidators.validate_string_length(v, min_len=2, max_len=100, field_name="Name")
        return v


class MagicLinkResponse(BaseModel):
    success: bool
    message: str


class VerifyTokenRequest(BaseModel):
    token: constr(min_length=1, max_length=500)
    
    @field_validator('token')
    @classmethod
    def validate_token(cls, v):
        # Remove any HTML/script tags
        return InputValidators.sanitize_html(v.strip())


# Password Auth Requests  
class PasswordLoginRequest(BaseModel):
    email: EmailStr
    password: constr(min_length=1, max_length=255)


class ChangePasswordRequest(BaseModel):
    current_password: str
    new_password: constr(min_length=8, max_length=255)
    
    @field_validator('new_password')
    @classmethod
    def validate_new_password(cls, v):
        return InputValidators.validate_password_strength(v)


# User Responses
class UserResponse(BaseModel):
    id: int
    email: str
    name: str
    user_type: str
    total_sessions: int
    total_hours: str
    marketing_consent: bool
    created_at: datetime
    last_login_at: Optional[datetime]
    must_change_password: bool = False
    
    class Config:
        from_attributes = True


class AuthResponse(BaseModel):
    success: bool
    user: Optional[UserResponse] = None
    message: str
    must_change_password: bool = False


# User Creation (for new account flow)
class UserCreateRequest(BaseModel):
    email: EmailStr
    name: constr(min_length=2, max_length=100)
    marketing_consent: bool = False
    
    @field_validator('name')
    @classmethod
    def validate_name(cls, v):
        # Sanitize HTML and validate
        v = InputValidators.sanitize_html(v)
        return InputValidators.validate_string_length(v, min_len=2, max_len=100, field_name="Name")


class EmailCheckResponse(BaseModel):
    route: str  # 'team_member', 'manager_dashboard', 'pay_per_edit'
    is_new: bool = False
    is_returning: bool = False
    tenant_name: Optional[str] = None
    manager_email: Optional[str] = None
    price: Optional[int] = 500