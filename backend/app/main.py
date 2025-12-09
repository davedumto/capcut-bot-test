import sys
import os

# Add the parent directory (backend) to Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.interval import IntervalTrigger
from app.api import slots, bookings, sessions
from app.models.database import create_tables
from app.core.config import settings
from app.scheduler.jobs import session_start_job, session_end_job
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize scheduler
scheduler = AsyncIOScheduler()

# Create FastAPI app
app = FastAPI(
    title="CapCut Sharing Backend",
    description="Backend API for CapCut account sharing platform",
    version="1.0.0"
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=[settings.frontend_url, "http://localhost:3000"],  # Frontend URL
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include API routes
app.include_router(slots.router, prefix="/api", tags=["slots"])
app.include_router(bookings.router, prefix="/api", tags=["bookings"])
app.include_router(sessions.router, prefix="/api", tags=["sessions"])


@app.on_event("startup")
async def startup_event():
    """Initialize database tables and start scheduler on startup"""
    # Create database tables
    create_tables()
    logger.info("✅ Database tables created successfully")
    
    # Configure scheduler jobs
    # Session Start Job - runs every minute to check for sessions that should start
    scheduler.add_job(
        session_start_job,
        trigger=IntervalTrigger(minutes=1),
        id="session_start_job",
        name="Check for sessions to start",
        replace_existing=True
    )
    
    # Session End Job - runs every minute to check for sessions that should end
    scheduler.add_job(
        session_end_job,
        trigger=IntervalTrigger(minutes=1),
        id="session_end_job", 
        name="Check for sessions to end",
        replace_existing=True
    )
    
    # Password Cleanup Job - runs every 10 minutes to clean up expired passwords
    from app.services.password_service import password_service
    scheduler.add_job(
        password_service.cleanup_expired_passwords,
        trigger=IntervalTrigger(minutes=10),
        id="password_cleanup_job",
        name="Clean up expired passwords",
        replace_existing=True
    )
    
    # Midnight Reset Job - runs daily at midnight to reset all slots
    from apscheduler.triggers.cron import CronTrigger
    from app.scheduler.jobs import midnight_reset_job
    scheduler.add_job(
        midnight_reset_job,
        trigger=CronTrigger(hour=0, minute=0),  # Every day at 12:00 AM
        id="midnight_reset_job",
        name="Reset daily slots at midnight",
        replace_existing=True
    )
    
    # Start the scheduler
    scheduler.start()
    logger.info("✅ Scheduler started - running session management and password cleanup jobs")


@app.on_event("shutdown")
async def shutdown_event():
    """Gracefully shutdown scheduler"""
    if scheduler.running:
        scheduler.shutdown()
        logger.info("✅ Scheduler shutdown successfully")


@app.get("/")
async def root():
    """Health check endpoint"""
    return {
        "message": "CapCut Sharing Backend API", 
        "version": "1.0.0",
        "status": "running"
    }


@app.get("/health")
async def health_check():
    """Health check endpoint for monitoring"""
    return {"status": "healthy", "timestamp": "2024-11-21"}


@app.get("/scheduler/status")
async def scheduler_status():
    """Get scheduler status and job information"""
    jobs = []
    if scheduler.running:
        for job in scheduler.get_jobs():
            jobs.append({
                "id": job.id,
                "name": job.name,
                "next_run": str(job.next_run_time) if job.next_run_time else None,
                "trigger": str(job.trigger)
            })
    
    return {
        "scheduler_running": scheduler.running,
        "jobs_count": len(jobs),
        "jobs": jobs
    }


@app.get("/debug/sessions")
async def debug_sessions():
    """Debug endpoint to check sessions and timezones"""
    from app.models.database import SessionLocal, Session as SessionModel
    from datetime import datetime
    
    db = SessionLocal()
    try:
        sessions = db.query(SessionModel).all()
        current_time = datetime.now()
        current_utc = datetime.utcnow()
        
        session_data = []
        for session in sessions:
            session_data.append({
                "id": session.id,
                "user_name": session.user_name,
                "user_email": session.user_email,
                "start_time": str(session.start_time),
                "start_time_type": str(type(session.start_time)),
                "start_time_tzinfo": str(session.start_time.tzinfo) if hasattr(session.start_time, 'tzinfo') and session.start_time.tzinfo else "naive",
                "end_time": str(session.end_time),
                "status": session.status,
                "slot_id": session.slot_id,
                "comparison_local": session.start_time <= current_time,
                "comparison_utc": session.start_time <= current_utc
            })
        
        return {
            "current_local_time": str(current_time),
            "current_utc_time": str(current_utc),
            "sessions": session_data
        }
    finally:
        db.close()


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)