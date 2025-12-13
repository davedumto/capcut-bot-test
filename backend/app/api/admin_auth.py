from fastapi import APIRouter, Depends, HTTPException, Response, Cookie
from sqlalchemy.orm import Session
from sqlalchemy import func, extract
from app.models.database import get_db, User, Tenant, BotJob, Payment, Session as SessionModel
from app.core.config import settings
from pydantic import BaseModel, EmailStr
from datetime import datetime, timedelta
from typing import Optional
import secrets
import string

router = APIRouter()

class AdminLoginRequest(BaseModel):
    email: EmailStr
    password: str

@router.post("/login")
async def admin_login(req: AdminLoginRequest, response: Response):
    """Admin login endpoint - credentials from environment variables"""
    if req.email == settings.admin_email and req.password == settings.admin_password:
        # Set admin session cookie
        response.set_cookie(
            key="admin_session",
            value="authenticated",
            httponly=True,
            samesite="lax",
            secure=settings.is_production(),  # HTTPS only in production
            max_age=86400,  # 24 hours
            path="/"
        )
        return {"success": True, "message": "Login successful"}
    else:
        raise HTTPException(status_code=401, detail="Invalid credentials")

@router.get("/check-auth")
async def check_admin_auth(admin_session: Optional[str] = Cookie(None)):
    """Check if admin is authenticated"""
    if admin_session != "authenticated":
        raise HTTPException(status_code=401, detail="Not authenticated")
    return {"authenticated": True}

@router.post("/logout")
async def admin_logout(response: Response):
    """Admin logout endpoint"""
    response.delete_cookie(key="admin_session", path="/")
    return {"success": True, "message": "Logged out"}
