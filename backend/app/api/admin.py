from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import func, extract
from app.models.database import get_db, User, Tenant, BotJob, Payment, Session as SessionModel, TeamMember
from pydantic import BaseModel, EmailStr
from datetime import datetime, timedelta
import secrets
import string

router = APIRouter()

class AddManagerRequest(BaseModel):
    email: EmailStr
    name: str

class AddSlotioRequest(BaseModel):
    name: str
    capcut_email: EmailStr
    gmail_email: EmailStr
    gmail_app_password: str

class UpdateSlotioRequest(BaseModel):
    is_slotio_account: bool = True

def generate_temp_password():
    chars = string.ascii_letters + string.digits
    return ''.join(secrets.choice(chars) for _ in range(12))

@router.get("/analytics")
async def get_analytics(db: Session = Depends(get_db)):
    try:
        total_revenue_raw = db.query(func.sum(Payment.amount)).filter_by(status="success").scalar()
        total_revenue = (total_revenue_raw / 100) if total_revenue_raw else 0
        
        total_sessions = db.query(SessionModel).filter(SessionModel.created_at.isnot(None)).count()
        total_hours = total_sessions * 1.5
        
        slotio_sessions_count = 0
        slotio_revenue = 0
        
        # Calculate peak hours (last 30 days)
        peak_hours = []
        thirty_days_ago = datetime.now() - timedelta(days=30)
        
        try:
            # Group sessions by hour of day
            for hour in range(24):
                hour_count = db.query(SessionModel).filter(
                    SessionModel.created_at >= thirty_days_ago,
                    extract('hour', SessionModel.start_time) == hour
                ).count()
                
                peak_hours.append({
                    "hour": f"{hour:02d}:00",
                    "sessions": hour_count
                })
        except Exception as e:
            print(f"Peak hours query error: {e}")
            peak_hours = []
        
        last_7_days = []
        for i in range(6, -1, -1):
            date = datetime.now() - timedelta(days=i)
            day_start = date.replace(hour=0, minute=0, second=0, microsecond=0)
            day_end = day_start + timedelta(days=1)
            
            daily_revenue = 0
            daily_sessions = 0
            try:
                payments = db.query(Payment).filter(
                    Payment.status == "success",
                    Payment.created_at >= day_start,
                    Payment.created_at < day_end
                ).all()
                daily_revenue = sum(p.amount for p in payments) / 100
                
                # Count sessions for this day
                daily_sessions = db.query(SessionModel).filter(
                    SessionModel.created_at >= day_start,
                    SessionModel.created_at < day_end
                ).count()
            except Exception as e:
                print(f"Analytics query error for {day_start.strftime('%m/%d')}: {e}")
            
            last_7_days.append({
                "date": day_start.strftime("%m/%d"),
                "sessions": daily_sessions,
                "revenue": daily_revenue
            })
        
        return {
            "total_revenue": total_revenue,
            "slotio_revenue": slotio_revenue,
            "total_sessions": total_sessions,
            "total_hours": total_hours,
            "slotio_sessions": slotio_sessions_count,
            "peak_hours": peak_hours,
            "last_7_days": last_7_days
        }
    except Exception as e:
        print(f"Analytics error: {e}")
        return {
            "total_revenue": 0,
            "slotio_revenue": 0,
            "total_sessions": 0,
            "total_hours": 0,
            "slotio_sessions": 0,
            "peak_hours": [],
            "last_7_days": []
        }

@router.post("/managers")
async def add_manager(req: AddManagerRequest, db: Session = Depends(get_db)):
    existing = db.query(User).filter_by(email=req.email).first()
    
    if existing:
        # Check if already a manager
        if existing.user_type == "manager":
            raise HTTPException(400, "User is already a manager")
        
        # Promote existing user to manager
        existing.user_type = "manager"
        existing.name = req.name  # Update name if provided
        db.commit()
        db.refresh(existing)
        
        # Create tenant for this manager
        tenant = Tenant(manager_id=existing.id, name=f"{req.name}'s Team")
        db.add(tenant)
        db.commit()
        
        return {
            "success": True,
            "manager_id": existing.id,
            "message": "User promoted to manager",
            "temp_password": None  # They use their existing password
        }
    
    # Create new manager
    temp_password = generate_temp_password()
    
    from app.core.security import hash_password
    user = User(
        email=req.email,
        name=req.name,
        user_type="manager",
        password_hash=hash_password(temp_password),
        must_change_password=True
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    
    tenant = Tenant(manager_id=user.id, name=f"{req.name}'s Team")
    db.add(tenant)
    db.commit()
    
    return {
        "success": True,
        "manager_id": user.id,
        "temp_password": temp_password
    }

@router.get("/managers")
async def list_managers(db: Session = Depends(get_db)):
    managers = db.query(User).filter_by(user_type="manager").all()
    return [{
        "id": m.id,
        "name": m.name,
        "email": m.email,
        "created_at": m.created_at,
        "last_login": m.last_login_at
    } for m in managers]

@router.post("/managers/{manager_id}/reset-password")
async def reset_manager_password(manager_id: int, db: Session = Depends(get_db)):
    """Reset a manager's password and return a new temporary password"""
    manager = db.query(User).filter_by(id=manager_id, user_type="manager").first()
    if not manager:
        raise HTTPException(404, "Manager not found")
    
    temp_password = generate_temp_password()
    
    from app.core.security import hash_password
    manager.password_hash = hash_password(temp_password)
    manager.must_change_password = True
    
    db.commit()
    
    return {
        "success": True,
        "temp_password": temp_password,
        "message": f"Password reset for {manager.email}. They must change it on first login."
    }

@router.delete("/managers/{manager_id}")
async def remove_manager(manager_id: int, db: Session = Depends(get_db)):
    """
    Remove a manager - converts them and their team members to normal users.
    They can still login but will use the system as one-off users.
    """
    manager = db.query(User).filter_by(id=manager_id, user_type="manager").first()
    if not manager:
        raise HTTPException(404, "Manager not found")
    
    # Find manager's tenant
    tenant = db.query(Tenant).filter_by(manager_id=manager_id).first()
    
    if tenant:
        # Convert all team member users to one_off users
        team_member_users = db.query(User).filter_by(team_tenant_id=tenant.id).all()
        for member in team_member_users:
            member.user_type = "one_off"
            member.team_tenant_id = None
        
        # Delete team member records from the team_members table
        db.query(TeamMember).filter_by(tenant_id=tenant.id).delete()
        
        # Delete the tenant
        db.delete(tenant)
    
    # Convert manager to one_off user
    manager.user_type = "one_off"
    manager.tenant_id = None
    
    db.commit()
    
    return {
        "success": True, 
        "message": "Manager and team members converted to regular users"
    }

@router.post("/slotio-accounts")
async def add_slotio_account(req: AddSlotioRequest, db: Session = Depends(get_db)):
    # For Slotio accounts, we store the email so we can identify which account is which
    tenant = Tenant(
        name=req.name,
        capcut_email=req.capcut_email,
        is_slotio_account=True,
        total_team_sessions=0,
        total_team_hours=0
    )
    db.add(tenant)
    db.commit()
    db.refresh(tenant)
    
    return {"success": True, "tenant_id": tenant.id}

@router.get("/slotio-accounts")
async def list_slotio_accounts(db: Session = Depends(get_db)):
    try:
        accounts = db.query(Tenant).filter_by(is_slotio_account=True).all()
        return [{
            "id": a.id,
            "name": a.name or "Unnamed Account",
            "capcut_email": a.capcut_email or "",
            "total_sessions": a.total_team_sessions or 0,
            "total_hours": a.total_team_hours or 0
        } for a in accounts]
    except Exception as e:
        print(f"Slotio accounts error: {e}")
        return []

@router.patch("/slotio-accounts/{tenant_id}")
async def update_slotio_account(tenant_id: int, req: UpdateSlotioRequest, db: Session = Depends(get_db)):
    tenant = db.query(Tenant).filter_by(id=tenant_id).first()
    if not tenant:
        raise HTTPException(404, "Account not found")
    
    tenant.is_slotio_account = req.is_slotio_account
    db.commit()
    return {"success": True}

@router.delete("/slotio-accounts/{tenant_id}")
async def remove_slotio_account(tenant_id: int, db: Session = Depends(get_db)):
    # Check if this account exists
    tenant = db.query(Tenant).filter_by(id=tenant_id, is_slotio_account=True).first()
    if not tenant:
        raise HTTPException(404, "Account not found")
    
    # Count total Slotio accounts
    total_accounts = db.query(Tenant).filter_by(is_slotio_account=True).count()
    
    # Cannot delete the last account - must have at least 1
    if total_accounts <= 1:
        raise HTTPException(
            400, 
            "Cannot delete the last Slotio account. Add a new account first, then delete this one."
        )
    
    db.delete(tenant)
    db.commit()
    return {"success": True}

@router.get("/bot-jobs")
async def list_bot_jobs(status: str = None, db: Session = Depends(get_db)):
    query = db.query(BotJob)
    if status:
        query = query.filter_by(status=status)
    
    jobs = query.order_by(BotJob.created_at.desc()).limit(50).all()
    return [{
        "id": j.id,
        "session_id": j.session_id,
        "status": j.status,
        "attempts": j.attempts,
        "error_message": j.error_message,
        "created_at": j.created_at
    } for j in jobs]

@router.post("/bot-jobs/{job_id}/retry")
async def retry_bot_job(job_id: int, db: Session = Depends(get_db)):
    job = db.query(BotJob).filter_by(id=job_id).first()
    if not job:
        raise HTTPException(404, "Job not found")
    
    job.status = "pending"
    job.error_message = None
    db.commit()
    return {"success": True}

@router.get("/stats")
async def get_platform_stats(db: Session = Depends(get_db)):
    total_managers = db.query(User).filter_by(user_type="manager").count()
    total_pay_per_edit = db.query(User).filter_by(user_type="one_off").count()
    
    today = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
    today_sessions = db.query(SessionModel).filter(SessionModel.created_at >= today).count()
    
    active_sessions = db.query(SessionModel).filter_by(status="active").count()
    
    total_revenue_raw = db.query(func.sum(Payment.amount)).filter_by(status="success").scalar()
    total_revenue = (total_revenue_raw / 100) if total_revenue_raw else 0
    
    pending_jobs = db.query(BotJob).filter_by(status="pending").count()
    failed_jobs = db.query(BotJob).filter_by(status="failed").count()
    
    return {
        "total_managers": total_managers,
        "total_pay_per_edit_users": total_pay_per_edit,
        "today_sessions": today_sessions,
        "active_sessions": active_sessions,
        "total_revenue": total_revenue,
        "pending_bot_jobs": pending_jobs,
        "failed_bot_jobs": failed_jobs
    }
