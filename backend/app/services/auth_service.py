from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from app.models.database import User, AuthToken, TeamMember, Tenant
from app.models.auth_schemas import UserCreateRequest, EmailCheckResponse
from app.core.security import hash_password, verify_password, generate_magic_token, create_access_token
from app.services.email_service import email_service
from app.core.config import settings


class AuthService:
    
    def check_email_route(self, db: Session, email: str) -> EmailCheckResponse:
        # Check if email is in any team first
        team_membership = db.query(TeamMember).filter_by(email=email).first()
        
        if team_membership:
            tenant = db.query(Tenant).filter_by(id=team_membership.tenant_id).first()
            manager = db.query(User).filter_by(id=tenant.manager_id).first() if tenant else None
            
            return EmailCheckResponse(
                route="team_member",
                tenant_name=tenant.name if tenant else "Team",
                manager_email=manager.email if manager else None
            )
        
        # Check if user exists
        user = db.query(User).filter_by(email=email).first()
        
        if user:
            if user.user_type == "manager":
                return EmailCheckResponse(route="manager_dashboard")
            return EmailCheckResponse(route="pay_per_edit", is_returning=True)
        
        return EmailCheckResponse(route="pay_per_edit", is_new=True)
    
    def create_magic_link(self, db: Session, email: str, name: str = None, marketing_consent: bool = False) -> bool:
        db.query(AuthToken).filter(AuthToken.email == email).delete()
        
        token = generate_magic_token()
        auth_token = AuthToken(
            email=email,
            token=token,
            expires_at=datetime.utcnow() + timedelta(minutes=15)
        )
        db.add(auth_token)
        
        # Create or update user if name provided
        if name:
            user = db.query(User).filter_by(email=email).first()
            if not user:
                user = User(email=email, name=name, marketing_consent=marketing_consent)
                db.add(user)
            else:
                user.name = name
                user.marketing_consent = marketing_consent
        
        db.commit()
        
        magic_link = f"{settings.frontend_url}/auth/verify?token={token}"
        return email_service.send_magic_link(email, magic_link)
    
    def verify_magic_token(self, db: Session, token: str):
        auth_token = db.query(AuthToken).filter(
            AuthToken.token == token,
            AuthToken.used_at.is_(None),
            AuthToken.expires_at > datetime.utcnow()
        ).first()
        
        if not auth_token:
            return None
        
        auth_token.used_at = datetime.utcnow()
        user = db.query(User).filter_by(email=auth_token.email).first()
        if user:
            user.last_login_at = datetime.utcnow()
        db.commit()
        return user
    
    def create_jwt_token(self, user: User) -> str:
        return create_access_token({
            "sub": user.email,
            "email": user.email,
            "user_type": user.user_type,
            "name": user.name
        })
    
    def create_user_account(self, db: Session, user_data: UserCreateRequest):
        user = User(
            email=user_data.email,
            name=user_data.name,
            user_type="one_off",
            marketing_consent=user_data.marketing_consent
        )
        db.add(user)
        db.commit()
        db.refresh(user)
        return user
    
    def password_login(self, db: Session, email: str, password: str):
        user = db.query(User).filter_by(email=email, user_type="manager").first()
        if user and user.password_hash and verify_password(password, user.password_hash):
            user.last_login_at = datetime.utcnow()
            db.commit()
            return user
        return None
    
    def change_password(self, db: Session, user_id: int, current_password: str, new_password: str) -> bool:
        user = db.query(User).filter_by(id=user_id, user_type="manager").first()
        if not user:
            return False
            
        if not user.must_change_password and not verify_password(current_password, user.password_hash):
            return False
            
        user.password_hash = hash_password(new_password)
        user.must_change_password = False
        db.commit()
        return True
    
    def send_password_reset_email(self, db: Session, user: User) -> bool:
        """Send password reset email to manager with magic link that redirects to password change"""
        # Delete any existing tokens for this email
        db.query(AuthToken).filter(AuthToken.email == user.email).delete()
        
        # Create a special reset token
        token = generate_magic_token()
        auth_token = AuthToken(
            email=user.email,
            token=token,
            expires_at=datetime.utcnow() + timedelta(hours=1)  # 1 hour expiry for reset
        )
        db.add(auth_token)
        
        # Mark user as must_change_password so they're prompted after verify
        user.must_change_password = True
        db.commit()
        
        # Send reset email with magic link
        reset_link = f"{settings.frontend_url}/auth/verify?token={token}"
        return email_service.send_password_reset(user.email, reset_link)
    
    def create_jwt_token(self, user: User) -> str:
        return create_access_token({
            "sub": str(user.id),
            "email": user.email,
            "user_type": user.user_type
        })


auth_service = AuthService()