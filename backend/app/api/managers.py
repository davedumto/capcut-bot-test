from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.models.database import get_db, User, Tenant, TeamMember
from app.core.security import get_current_user
from app.services.encryption_service import encryption_service
from pydantic import BaseModel, EmailStr
from typing import List

router = APIRouter()

class TeamMemberAdd(BaseModel):
    email: EmailStr

class CredentialsUpdate(BaseModel):
    capcut_email: str
    capcut_password: str
    gmail_email: str
    gmail_password: str

@router.get("/team")
def get_team(current_user: dict = Depends(get_current_user), db: Session = Depends(get_db)):
    if current_user["user_type"] != "manager":
        raise HTTPException(403, "Manager access required")
    
    user = db.query(User).filter_by(email=current_user["email"]).first()
    if not user:
        raise HTTPException(404, "User not found")
    
    tenant = db.query(Tenant).filter_by(manager_id=user.id).first()
    if not tenant:
        # Create tenant if doesn't exist
        tenant = Tenant(manager_id=user.id)
        db.add(tenant)
        db.commit()
        db.refresh(tenant)
    
    team_members = db.query(TeamMember).filter_by(tenant_id=tenant.id).all()
    
    return {
        "team_members": [
            {
                "id": member.id,
                "email": member.email,
                "user_id": member.user_id,
                "added_at": member.added_at.isoformat()
            }
            for member in team_members
        ],
        "credentials": {
            "capcut_email": encryption_service.decrypt(tenant.capcut_email or ""),
            "gmail_email": encryption_service.decrypt(tenant.gmail_email or "")
        },
        "settings": {
            "allow_multiple_bookings": tenant.allow_multiple_bookings or False
        }
    }


class SettingsUpdate(BaseModel):
    allow_multiple_bookings: bool


@router.patch("/settings")
def update_settings(
    settings: SettingsUpdate,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Update manager team settings"""
    if current_user["user_type"] != "manager":
        raise HTTPException(403, "Manager access required")
    
    user = db.query(User).filter_by(email=current_user["email"]).first()
    if not user:
        raise HTTPException(404, "User not found")
    
    tenant = db.query(Tenant).filter_by(manager_id=user.id).first()
    if not tenant:
        raise HTTPException(404, "Team not found")
    
    tenant.allow_multiple_bookings = settings.allow_multiple_bookings
    db.commit()
    
    return {
        "success": True,
        "settings": {
            "allow_multiple_bookings": tenant.allow_multiple_bookings
        }
    }

@router.post("/team")
def add_team_member(
    member: TeamMemberAdd,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    if current_user["user_type"] != "manager":
        raise HTTPException(403, "Manager access required")
    
    user = db.query(User).filter_by(email=current_user["email"]).first()
    if not user:
        raise HTTPException(404, "User not found")
    
    tenant = db.query(Tenant).filter_by(manager_id=user.id).first()
    if not tenant:
        tenant = Tenant(manager_id=user.id)
        db.add(tenant)
        db.commit()
        db.refresh(tenant)
    
    # Check if email belongs to a manager
    existing_manager = db.query(User).filter_by(email=member.email, user_type="manager").first()
    if existing_manager:
        raise HTTPException(400, "Cannot add a manager as a team member. Managers have their own accounts.")
    
    # Check if already exists in team
    existing = db.query(TeamMember).filter_by(
        tenant_id=tenant.id, 
        email=member.email
    ).first()
    
    if existing:
        raise HTTPException(400, "Team member already exists")
    
    # Check if user exists and update their type or create team member record
    existing_user = db.query(User).filter_by(email=member.email).first()
    if existing_user:
        # Update existing user to be a team member
        existing_user.user_type = "team_member"
        existing_user.team_tenant_id = tenant.id
    
    # Add team member record
    team_member = TeamMember(
        tenant_id=tenant.id,
        email=member.email,
        user_id=existing_user.id if existing_user else None
    )
    
    try:
        db.add(team_member)
        db.commit()
        db.refresh(team_member)
    except Exception as e:
        db.rollback()
        if "Team member limit" in str(e):
            raise HTTPException(400, "Team member limit (12) reached")
        raise HTTPException(400, f"Failed to add team member: {str(e)}")
    
    return {"success": True, "member": {
        "id": team_member.id,
        "email": team_member.email,
        "added_at": team_member.added_at.isoformat()
    }}

@router.delete("/team/{member_id}")
def remove_team_member(
    member_id: int,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    if current_user["user_type"] != "manager":
        raise HTTPException(403, "Manager access required")
    
    user = db.query(User).filter_by(email=current_user["email"]).first()
    if not user:
        raise HTTPException(404, "User not found")
    
    tenant = db.query(Tenant).filter_by(manager_id=user.id).first()
    if not tenant:
        raise HTTPException(404, "No team found")
    
    member = db.query(TeamMember).filter_by(
        id=member_id, 
        tenant_id=tenant.id
    ).first()
    
    if not member:
        raise HTTPException(404, "Team member not found")
    
    # If this team member has a linked user, convert them back to one_off
    if member.user_id:
        linked_user = db.query(User).filter_by(id=member.user_id).first()
        if linked_user:
            linked_user.user_type = "one_off"
            linked_user.team_tenant_id = None
    else:
        # Check by email if user_id wasn't set
        linked_user = db.query(User).filter_by(email=member.email).first()
        if linked_user and linked_user.user_type == "team_member":
            linked_user.user_type = "one_off"
            linked_user.team_tenant_id = None
    
    db.delete(member)
    db.commit()
    
    return {"success": True}

@router.post("/credentials")
def update_credentials(
    creds: CredentialsUpdate,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    if current_user["user_type"] != "manager":
        raise HTTPException(403, "Manager access required")
    
    user = db.query(User).filter_by(email=current_user["email"]).first()
    if not user:
        raise HTTPException(404, "User not found")
    
    tenant = db.query(Tenant).filter_by(manager_id=user.id).first()
    if not tenant:
        tenant = Tenant(manager_id=user.id)
        db.add(tenant)
        db.commit()
        db.refresh(tenant)
    
    # Encrypt and store credentials
    tenant.capcut_email = encryption_service.encrypt(creds.capcut_email)
    tenant.capcut_password_encrypted = encryption_service.encrypt(creds.capcut_password)
    tenant.gmail_email = encryption_service.encrypt(creds.gmail_email)
    tenant.gmail_password_encrypted = encryption_service.encrypt(creds.gmail_password)
    
    db.commit()
    
    return {"success": True}