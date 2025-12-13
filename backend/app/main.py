import sys
import os

# Add the parent directory (backend) to Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.interval import IntervalTrigger
from app.api import slots, bookings, sessions, auth, users, managers, admin, payments, bot_jobs, complete_booking, manager_subscription, bot_health, admin_auth
from app.models.database import create_tables
from app.core.config import settings
from app.scheduler.jobs import session_start_job, session_end_job
from app.middleware.security import SecurityHeadersMiddleware
from app.middleware.request_limits import RequestSizeLimitMiddleware
from app.middleware.https_redirect import HTTPSRedirectMiddleware
from app.core.rate_limiter import limiter
from slowapi import _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded
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

# Add SlowAPI rate limiter
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

# Add HTTPS Redirect Middleware (production only)
app.add_middleware(HTTPSRedirectMiddleware)

# Add Request Size Limit Middleware (10MB max)
app.add_middleware(RequestSizeLimitMiddleware, max_size=10 * 1024 * 1024)

# Add Security Headers Middleware (add FIRST for all responses)
app.add_middleware(SecurityHeadersMiddleware)

# Configure CORS - environment-based origins
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.get_cors_origins(),  # Dynamic based on environment
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "PATCH", "DELETE", "OPTIONS"],  # Explicit methods
    allow_headers=["*"],
    max_age=3600,  # Cache preflight requests for 1 hour
)

# Include API routes
app.include_router(auth.router, prefix="/api", tags=["auth"])
app.include_router(users.router, prefix="/api/users", tags=["users"])
app.include_router(managers.router, prefix="/api/managers", tags=["managers"])
app.include_router(admin.router, prefix="/api/admin", tags=["admin"])
app.include_router(admin_auth.router, prefix="/api/admin", tags=["admin-auth"])
app.include_router(bot_health.router, prefix="/api", tags=["bot-health"])
app.include_router(payments.router, prefix="/api/payments", tags=["payments"])
app.include_router(bot_jobs.router, prefix="/api/bot-jobs", tags=["bot-jobs"])
app.include_router(complete_booking.router, prefix="/api",tags=["bookings"])
app.include_router(manager_subscription.router, prefix="/api/manager", tags=["manager-subscription"])
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
    
    # Subscription Renewal Job - runs daily at 2 AM to process renewals
    from app.services.subscription_service import renew_all_subscriptions
    scheduler.add_job(
        renew_all_subscriptions,
        trigger=CronTrigger(hour=2, minute=0),  # Every day at 2:00 AM
        id="subscription_renewal_job",
        name="Process subscription renewals",
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