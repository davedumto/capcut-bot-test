"""
Pydantic schemas for request/response validation
As specified in instructions.md
"""

from pydantic import BaseModel, EmailStr, validator, Field
from typing import Optional, List
from datetime import datetime
import re


# Request/Response Schemas for API Endpoints

class TimeSlotSchema(BaseModel):
    """Time slot response schema"""
    id: str
    start_time: str
    end_time: str
    available: bool = True

    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }


class SlotsResponse(BaseModel):
    """Response schema for GET /api/slots"""
    slots: List[TimeSlotSchema]


class BookingRequest(BaseModel):
    """Request schema for POST /api/bookings"""
    name: str = Field(..., min_length=2, max_length=100)
    email: EmailStr
    slot_id: str
    
    @validator('name')
    def validate_name(cls, v):
        if not v or len(v.strip()) < 2:
            raise ValueError('Name must be at least 2 characters long')
        if len(v.strip()) > 100:
            raise ValueError('Name must be less than 100 characters')
        if not re.match(r'^[a-zA-Z\s\-\.\']+$', v.strip()):
            raise ValueError('Name can only contain letters, spaces, hyphens, periods, and apostrophes')
        return v.strip()
    
    @validator('slot_id')
    def validate_slot_id(cls, v):
        if not re.match(r'^slot_\d+$', v):
            raise ValueError('Invalid slot ID format')
        return v


class BookingResponse(BaseModel):
    success: bool
    session_id: str
    message: str
    payment_reference: Optional[str] = None
    authorization_url: Optional[str] = None


class ActiveSessionResponse(BaseModel):
    """Response schema for GET /api/sessions/active"""
    session_id: str
    user_email: str
    start_time: str
    end_time: str

    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }


class SessionDetailsResponse(BaseModel):
    """Response schema for GET /api/sessions/{id}"""
    session_id: str
    user_name: str
    user_email: str
    start_time: str
    end_time: str
    status: str

    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }


# Database Model Schemas

class UserCreate(BaseModel):
    """Schema for creating a new user"""
    name: str
    email: EmailStr


class UserSchema(BaseModel):
    """Schema for user data"""
    id: int
    name: str
    email: str
    created_at: datetime

    class Config:
        from_attributes = True


class SessionCreate(BaseModel):
    """Schema for creating a new session"""
    user_id: Optional[int] = None
    user_name: str
    user_email: str
    start_time: datetime
    end_time: datetime
    status: str = "pending"


class SessionSchema(BaseModel):
    """Schema for session data"""
    id: int
    user_id: Optional[int]
    user_name: str
    user_email: str
    start_time: datetime
    end_time: datetime
    status: str
    current_password_id: Optional[int]
    next_user_email: Optional[str]
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class PasswordCreate(BaseModel):
    """Schema for creating a new password"""
    password_hash: str
    plain_password: Optional[str] = None
    session_id: Optional[int] = None
    is_active: bool = True
    expires_at: Optional[datetime] = None


class PasswordSchema(BaseModel):
    """Schema for password data"""
    id: int
    password_hash: str
    plain_password: Optional[str]
    session_id: Optional[int]
    is_active: bool
    created_at: datetime
    expires_at: Optional[datetime]

    class Config:
        from_attributes = True


class DailyLogSchema(BaseModel):
    """Schema for daily log data"""
    id: int
    date: datetime
    total_slots: int
    booked_slots: int
    no_shows: int
    created_at: datetime

    class Config:
        from_attributes = True


# Error Response Schemas

class ErrorResponse(BaseModel):
    """Standard error response schema"""
    detail: str
    error_code: Optional[str] = None


class ValidationErrorResponse(BaseModel):
    """Validation error response schema"""
    detail: str
    errors: List[dict]


# Bot Service Schemas

class BotLogoutRequest(BaseModel):
    """Request schema for bot logout"""
    email: str


class BotLogoutResponse(BaseModel):
    """Response schema for bot logout"""
    success: bool
    message: str


class BotResetPasswordRequest(BaseModel):
    """Request schema for bot reset password"""
    email: str
    new_password: str


class BotResetPasswordResponse(BaseModel):
    """Response schema for bot reset password"""
    success: bool
    new_password: str
    message: str