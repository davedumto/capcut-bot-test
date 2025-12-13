from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.models.database import get_db
from pydantic import BaseModel
from datetime import datetime

router = APIRouter()

# In-memory storage for bot worker health status
bot_worker_status = {
    "last_heartbeat": None,
    "status": "unknown",
    "consecutive_failures": 0
}

class HeartbeatRequest(BaseModel):
    status: str
    timestamp: str
    consecutive_failures: int

class AlertRequest(BaseModel):
    type: str
    consecutive_failures: int
    timestamp: str

@router.post("/admin/bot-worker/heartbeat")
def receive_heartbeat(request: HeartbeatRequest):
    """Receive heartbeat from bot worker"""
    global bot_worker_status
    bot_worker_status = {
        "last_heartbeat": datetime.fromisoformat(request.timestamp),
        "status": request.status,
        "consecutive_failures": request.consecutive_failures
    }
    return {"success": True}

@router.post("/admin/bot-worker/alert")
def receive_alert(alert: AlertRequest):
    """Receive critical alert from bot worker"""
    print(f"🚨 CRITICAL ALERT: {alert.type}")
    print(f"   Consecutive failures: {alert.consecutive_failures}")
    print(f"   Timestamp: {alert.timestamp}")
    
    # TODO: Send SMS/Email notification in production
    # For now, just log it
    
    return {"success": True}

@router.get("/admin/bot-worker/status")
def get_bot_worker_status():
    """Get current bot worker health status"""
    global bot_worker_status
    
    if not bot_worker_status["last_heartbeat"]:
        return {
            "status": "unknown",
            "message": "No heartbeat received yet",
            "healthy": False
        }
    
    # Check if heartbeat is recent (within last 2 minutes)
    time_since_heartbeat = (datetime.now() - bot_worker_status["last_heartbeat"]).total_seconds()
    is_healthy = time_since_heartbeat < 120  # 2 minutes
    
    return {
        "status": "healthy" if is_healthy else "unhealthy",
        "last_heartbeat": bot_worker_status["last_heartbeat"].isoformat(),
        "seconds_since_heartbeat": int(time_since_heartbeat),
        "consecutive_failures": bot_worker_status["consecutive_failures"],
        "healthy": is_healthy
    }
