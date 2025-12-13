from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.models.database import get_db, User, Session as SessionModel, TimeSlot
from app.core.security import get_current_user
from pydantic import BaseModel
from typing import List, Optional

router = APIRouter()

class UserProfile(BaseModel):
    name: str
    email: str
    user_type: str
    total_sessions: int
    total_hours: str
    marketing_consent: bool

class UpdateProfile(BaseModel):
    name: str
    marketing_consent: bool

class CapCutCredentials(BaseModel):
    email: str
    password: str

@router.get("/profile", response_model=UserProfile)
async def get_profile(current_user: dict = Depends(get_current_user), db: Session = Depends(get_db)):
    user = db.query(User).filter_by(email=current_user["email"]).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    # Calculate total sessions and hours dynamically from Sessions table
    sessions = db.query(SessionModel).filter_by(user_id=user.id).all()
    total_sessions = len(sessions)
    # Each session is 1.5 hours
    total_hours = total_sessions * 1.5
    
    return UserProfile(
        name=user.name,
        email=user.email,
        user_type=user.user_type,
        total_sessions=total_sessions,
        total_hours=f"{total_hours:.1f}" if total_hours > 0 else "0",
        marketing_consent=user.marketing_consent
    )

@router.patch("/profile")
async def update_profile(
    update: UpdateProfile,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    user = db.query(User).filter_by(email=current_user["email"]).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    user.name = update.name
    user.marketing_consent = update.marketing_consent
    db.commit()
    
    return {"success": True, "message": "Profile updated"}

@router.get("/team")
async def get_team_data(current_user: dict = Depends(get_current_user), db: Session = Depends(get_db)):
    user = db.query(User).filter_by(email=current_user["email"]).first()
    if not user or user.user_type != "manager":
        raise HTTPException(status_code=403, detail="Manager access required")
    
    team_members = db.query(User).filter_by(team_tenant_id=user.tenant_id).all()
    
    return {
        "team_members": [
            {
                "id": member.id,
                "name": member.name,
                "email": member.email,
                "total_sessions": member.total_sessions,
                "total_hours": member.total_hours,
                "last_login_at": member.last_login_at.isoformat() if member.last_login_at else None
            }
            for member in team_members
        ],
        "capcut_credentials": {"email": "", "password": ""}  # TODO: Implement credential storage
    }

@router.post("/capcut-credentials")
async def save_capcut_credentials(
    credentials: CapCutCredentials,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    user = db.query(User).filter_by(email=current_user["email"]).first()
    if not user or user.user_type != "manager":
        raise HTTPException(status_code=403, detail="Manager access required")
    
    # TODO: Implement secure credential storage
    return {"success": True, "message": "Credentials saved"}

@router.get("/team-member-data")
async def get_team_member_data(current_user: dict = Depends(get_current_user), db: Session = Depends(get_db)):
    import pytz
    from datetime import datetime
    from app.services.slots_service import slots_service
    
    user = db.query(User).filter_by(email=current_user["email"]).first()
    if not user or user.user_type != "team_member":
        raise HTTPException(status_code=403, detail="Team member access required")
    
    # Get manager info
    manager = db.query(User).filter_by(tenant_id=user.team_tenant_id).first()
    
    # Get current time in WAT
    wat = pytz.timezone('Africa/Lagos')
    now = datetime.now(wat).replace(tzinfo=None)
    
    # Get available slots for THIS MANAGER'S TENANT (not Slotio pool!)
    available_slots = slots_service.get_available_slots(db, now, tenant_id=user.team_tenant_id)
    
    # Filter to only future, available slots
    future_available_slots = [
        slot for slot in available_slots 
        if slot.available and slot.start_time > now
    ][:6]  # Limit to 6
    
    # Get user's sessions
    sessions = db.query(SessionModel).filter_by(user_id=user.id).limit(10).all()
    
    return {
        "manager_info": {
            "name": manager.name if manager else "Unknown",
            "email": manager.email if manager else "Unknown",
            "company": "CapCut Team"  # TODO: Add company field
        } if manager else None,
        "available_slots": [
            {
                "id": slot.id,
                "start_time": slot.start_time.isoformat(),
                "end_time": slot.end_time.isoformat(),
                "available": slot.available
            }
            for slot in future_available_slots
        ],
        "sessions": [
            {
                "id": session.id,
                "start_time": session.start_time.isoformat(),
                "end_time": session.end_time.isoformat(),
                "status": session.status,
                "slot_id": session.slot_id
            }
            for session in sessions
        ]
    }