from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.models.database import get_db, BotJob, Tenant
from pydantic import BaseModel
from datetime import datetime

router = APIRouter()

class UpdateJobStatus(BaseModel):
    status: str
    error_message: str = None

class CompleteJobRequest(BaseModel):
    new_password: str

@router.get("/next")
async def get_next_job(db: Session = Depends(get_db)):
    job = db.query(BotJob).filter_by(status='pending').order_by(BotJob.created_at).first()
    
    if not job:
        return {"job": None}
    
    # Get tenant info
    tenant = db.query(Tenant).filter_by(id=job.tenant_id).first()
    
    return {
        "job": {
            "id": job.id,
            "tenant_id": job.tenant_id,
            "session_id": job.session_id,
            "job_type": job.job_type,
            "capcut_email": tenant.capcut_email if tenant else None,
            "gmail_email": tenant.gmail_email if tenant else None,
            "gmail_app_password": tenant.gmail_app_password if tenant else None
        }
    }

@router.patch("/{job_id}/status")
async def update_job_status(job_id: int, update: UpdateJobStatus, db: Session = Depends(get_db)):
    job = db.query(BotJob).filter_by(id=job_id).first()
    if not job:
        raise HTTPException(404, "Job not found")
    
    job.status = update.status
    if update.error_message:
        job.error_message = update.error_message
    
    if update.status == 'processing':
        job.started_at = datetime.now()
    
    job.attempts += 1
    db.commit()
    
    return {"success": True}

@router.post("/{job_id}/complete")
async def complete_job(job_id: int, req: CompleteJobRequest, db: Session = Depends(get_db)):
    from app.models.database import Session as SessionModel, Password
    from app.services.email_service import email_service
    
    job = db.query(BotJob).filter_by(id=job_id).first()
    if not job:
        raise HTTPException(404, "Job not found")
    
    # Mark job complete
    job.status = 'completed'
    job.completed_at = datetime.now()
    
    # Get session
    session = db.query(SessionModel).filter_by(id=job.session_id).first()
    if session:
        # Create password record
        password = Password(
            plain_password=req.new_password,
            session_id=session.id,
            is_active=True
        )
        db.add(password)
        session.current_password_id = password.id
        
        # Send credentials email
        try:
            email_service.send_credentials_email(
                to_email=session.user_email,
                password=req.new_password
            )
        except Exception as e:
            print(f"Failed to send credentials email: {e}")
    
    db.commit()
    
    return {"success": True, "message": "Job completed and credentials sent"}
