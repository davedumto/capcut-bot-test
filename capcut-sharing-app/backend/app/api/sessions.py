from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from datetime import datetime
from app.models.database import get_db, Session as SessionModel
from app.models.schemas import ActiveSessionResponse, SessionDetailsResponse
from typing import Optional

router = APIRouter()


@router.get("/sessions/active", response_model=Optional[ActiveSessionResponse])
async def get_active_session(db: Session = Depends(get_db)):
    """
    Get current active session
    As per instructions.md API format
    """
    try:
        current_time = datetime.now()
        
        # Find session that is currently active (current time is between start and end)
        active_session = db.query(SessionModel).filter(
            SessionModel.start_time <= current_time,
            SessionModel.end_time >= current_time,
            SessionModel.status == "active"
        ).first()
        
        if not active_session:
            return None
        
        return ActiveSessionResponse(
            session_id=f"sess_{active_session.id}",
            user_email=active_session.user_email,
            start_time=active_session.start_time.isoformat(),
            end_time=active_session.end_time.isoformat()
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get active session: {str(e)}")


@router.get("/sessions/{session_id}", response_model=SessionDetailsResponse)
async def get_session_details(session_id: str, db: Session = Depends(get_db)):
    """
    Get details for a specific session
    Used by frontend after booking to get session details
    """
    try:
        # Parse session_id (format: "sess_123")
        if not session_id.startswith("sess_"):
            raise HTTPException(status_code=400, detail="Invalid session ID format")
        
        session_db_id = int(session_id.replace("sess_", ""))
        
        session = db.query(SessionModel).filter(SessionModel.id == session_db_id).first()
        
        if not session:
            raise HTTPException(status_code=404, detail="Session not found")
        
        return SessionDetailsResponse(
            session_id=session_id,
            user_name=session.user_name,
            user_email=session.user_email,
            start_time=session.start_time.isoformat(),
            end_time=session.end_time.isoformat(),
            status=session.status
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get session details: {str(e)}")