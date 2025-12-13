from fastapi import APIRouter, Depends, HTTPException, Response, Cookie, Request
from sqlalchemy.orm import Session
from app.models.database import get_db, User
from app.models.auth_schemas import *
from app.services.auth_service import auth_service
from app.core.security import verify_token
from app.core.rate_limiter import limiter, get_rate_limit
from app.core.config import settings
from datetime import datetime

router = APIRouter()


def get_current_user(token: str = Cookie(None, alias="access_token"), db: Session = Depends(get_db)):
    if not token:
        return None
    payload = verify_token(token)
    if not payload:
        return None
    return db.query(User).filter_by(email=payload["sub"]).first()


@router.post("/auth/check-email", response_model=EmailCheckResponse)
def check_email(request: MagicLinkRequest, db: Session = Depends(get_db)):
    return auth_service.check_email_route(db, request.email)


@router.post("/auth/magic-link")
@limiter.limit(get_rate_limit("auth_magic_link"))
async def request_magic_link(request: Request, magic_request: MagicLinkRequest, db: Session = Depends(get_db)):
    """Send magic link (legacy endpoint) - Rate limited: 3/hour"""
    success = auth_service.create_magic_link(
        db, magic_request.email, magic_request.name, magic_request.marketing_consent
    )
    return {"success": success, "message": "Magic link sent!" if success else "Failed to send magic link"}


@router.post("/auth/send-magic-link")
@limiter.limit(get_rate_limit("auth_magic_link"))
async def send_magic_link(request: Request, magic_request: MagicLinkRequest, db: Session = Depends(get_db)):
    """Send magic link for passwordless authentication - Rate limited: 3/hour"""
    success = auth_service.create_magic_link(
        db, magic_request.email, magic_request.name, magic_request.marketing_consent
    )
    return {"success": success, "message": "Magic link sent!" if success else "Failed to send magic link"}


@router.get("/auth/verify")
def verify_magic_link(token: str, response: Response, db: Session = Depends(get_db)):
    user = auth_service.verify_magic_token(db, token)
    if not user:
        raise HTTPException(400, "Invalid or expired token")
    
    jwt_token = auth_service.create_jwt_token(user)
    response.set_cookie(
        "access_token", 
        jwt_token, 
        max_age=7*24*60*60, 
        httponly=True,
        samesite="lax",
        secure=settings.is_production(),  # HTTPS only in production
        path="/"
    )
    
    # Return user data with must_change_password flag
    return {
        "success": True, 
        "user": {
            "id": user.id,
            "email": user.email,
            "name": user.name,
            "user_type": user.user_type,
            "must_change_password": user.must_change_password or False
        }
    }


@router.post("/auth/create-account")
def create_account(user_data: UserCreateRequest, db: Session = Depends(get_db)):
    if db.query(User).filter_by(email=user_data.email).first():
        raise HTTPException(400, "Account already exists")
    
    user = auth_service.create_user_account(db, user_data)
    return {"success": True, "user_id": user.id}


@router.post("/auth/login")
@limiter.limit(get_rate_limit("auth_login"))
async def password_login(request: Request, body: PasswordLoginRequest, response: Response, db: Session = Depends(get_db)):
    """Password-based login - Rate limited: 5/minute"""
    user = auth_service.password_login(db, body.email, body.password)
    if not user:
        raise HTTPException(401, "Invalid email or password")
    
    jwt_token = auth_service.create_jwt_token(user)
    response.set_cookie(
        "access_token", 
        jwt_token, 
        max_age=7*24*60*60, 
        httponly=True,
        samesite="lax",
        secure=settings.is_production(),  # HTTPS only in production
        path="/"
    )
    return {"success": True, "user": user, "must_change_password": user.must_change_password}


@router.post("/auth/change-password")
def change_password(request: ChangePasswordRequest, req: Request, db: Session = Depends(get_db)):
    access_token = req.cookies.get("access_token")
    if not access_token:
        raise HTTPException(401, "Not authenticated")
    
    payload = verify_token(access_token)
    if not payload:
        raise HTTPException(401, "Invalid token")
    
    # Token stores user ID in 'sub' field
    user_id = payload.get("sub")
    user = db.query(User).filter_by(id=int(user_id)).first()
    
    if not user:
        raise HTTPException(404, "User not found")
    
    success = auth_service.change_password(db, user.id, request.current_password, request.new_password)
    return {"success": success}


@router.post("/auth/forgot-password")
@limiter.limit(get_rate_limit("auth_magic_link"))
async def forgot_password(request: Request, email_request: MagicLinkRequest, db: Session = Depends(get_db)):
    """Send password reset link to manager's email - Rate limited: 3/hour"""
    user = db.query(User).filter_by(email=email_request.email).first()
    
    if not user:
        # Return success even if user doesn't exist (security - don't reveal valid emails)
        return {"success": True, "message": "If an account exists, a reset link has been sent."}
    
    if user.user_type != "manager":
        # Only managers can reset via this flow
        return {"success": False, "message": "Password reset is only available for manager accounts. Regular users use magic links."}
    
    # Generate reset token and send email
    success = auth_service.send_password_reset_email(db, user)
    
    return {
        "success": success, 
        "message": "If an account exists, a reset link has been sent."
    }


@router.post("/auth/logout")
def logout(response: Response):
    response.delete_cookie("access_token", path="/")
    return {"success": True}


@router.get("/auth/me")
def get_me(token: str = Cookie(None, alias="access_token"), db: Session = Depends(get_db)):
    if not token:
        raise HTTPException(401, "Not authenticated")
    payload = verify_token(token)
    if not payload:
        raise HTTPException(401, "Invalid token")
    user = db.query(User).filter_by(id=int(payload["sub"])).first()
    if not user:
        raise HTTPException(404, "User not found")
    return {
        "id": user.id,
        "email": user.email,
        "name": user.name,
        "user_type": user.user_type,
        "must_change_password": user.must_change_password or False
    }