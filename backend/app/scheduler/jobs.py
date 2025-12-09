"""
Scheduler jobs for session management
As specified in instructions.md Phase 5
"""

from datetime import datetime
import pytz
from sqlalchemy.orm import Session
from app.models.database import SessionLocal, Session as SessionModel, Password
from app.services.bot_service import bot_service
from app.services.password_service import password_service
from app.services.email_service import email_service
from app.services.slots_service import slots_service
import logging
import sys
import os
import httpx
from app.core.config import settings

logger = logging.getLogger(__name__)


def get_database_session():
    """Get database session for scheduler jobs"""
    db = SessionLocal()
    try:
        return db
    except Exception as e:
        db.close()
        raise


async def session_start_job():
    """
    Session Start Job - Runs every minute
    As per instructions.md:
    - Check for sessions where current_time >= start_time AND status == 'pending'
    - Call POST /bot/reset-password
    - Generate new strong password
    - Store password in DB (encrypted)
    - Send email to user with credentials
    - Update session.status = 'active'
    """
    db = None
    try:
        db = get_database_session()
        # Use West Africa Time (UTC+1)
        wat_tz = pytz.timezone('Africa/Lagos')
        current_time = datetime.now(wat_tz).replace(tzinfo=None)
        
        # Find sessions that should start
        pending_sessions = db.query(SessionModel).filter(
            SessionModel.start_time <= current_time,
            SessionModel.status == "pending"
        ).all()
        
        for session in pending_sessions:
            try:
                logger.info(f"Starting session {session.id} for {session.user_email}")
                
                # Call bot service via HTTP to reset password
                try:
                    async with httpx.AsyncClient() as client:
                        response = await client.post(
                            f"{settings.bot_service_url}/bot/reset-password",
                            json={},  # Bot will use env vars for email and generate password
                            timeout=300.0  # 5 minutes timeout for bot operations
                        )
                        
                        if response.status_code == 200:
                            bot_result = response.json()
                            success = bot_result.get("success", False)
                            new_password = bot_result.get("new_password")
                        else:
                            logger.error(f"Bot service returned status {response.status_code}: {response.text}")
                            success = False
                            new_password = None
                            
                except Exception as e:
                    logger.error(f"Failed to call bot service: {e}")
                    success = False
                    new_password = None
                
                if success and new_password:
                    
                    # Create password entry in database
                    password_entry_data = password_service.create_password_entry(
                        password=new_password,
                        session_id=session.id
                    )
                    
                    # Save password to database
                    password_entry = Password(**password_entry_data)
                    db.add(password_entry)
                    db.commit()
                    db.refresh(password_entry)
                    
                    # Send email with credentials
                    email_sent = email_service.send_credentials_email(
                        user_name=session.user_name,
                        user_email=session.user_email,
                        password=new_password,
                        start_time=session.start_time.isoformat(),
                        end_time=session.end_time.isoformat()
                    )
                    
                    if email_sent:
                        # Update session status
                        session.status = "active"
                        session.current_password_id = password_entry.id
                        db.commit()
                        logger.info(f"Session {session.id} started successfully")
                    else:
                        logger.error(f"Failed to send email for session {session.id}")
                else:
                    logger.error(f"Bot failed to reset password for session {session.id}")
                    
            except Exception as e:
                logger.error(f"Failed to start session {session.id}: {e}")
                db.rollback()
        
        if db:
            db.close()
                
    except Exception as e:
        logger.error(f"Session start job failed: {e}")
        if db:
            db.close()


async def session_end_job():
    """
    Session End Job - Runs every minute
    As per instructions.md:
    - Check for sessions where current_time >= end_time AND status == 'active'
    - Call POST /bot/logout
    - Call POST /bot/reset-password with new generated password
    - Check for next_session
    - If next_session exists: Send email to next_user with new credentials
    - Update current session status to 'completed'
    """
    db = None
    try:
        db = get_database_session()
        # Use West Africa Time (UTC+1)
        wat_tz = pytz.timezone('Africa/Lagos')
        current_time = datetime.now(wat_tz).replace(tzinfo=None)
        
        # Find sessions that should end
        active_sessions = db.query(SessionModel).filter(
            SessionModel.end_time <= current_time,
            SessionModel.status == "active"
        ).all()
        
        for session in active_sessions:
            try:
                logger.info(f"Ending session {session.id} for {session.user_email}")
                
                # Call bot service via HTTP to reset password for next session
                try:
                    async with httpx.AsyncClient() as client:
                        response = await client.post(
                            f"{settings.bot_service_url}/bot/reset-password",
                            json={},  # Bot will use env vars for email and generate password
                            timeout=300.0  # 5 minutes timeout for bot operations
                        )
                        
                        if response.status_code == 200:
                            bot_result = response.json()
                            success = bot_result.get("success", False)
                            new_password = bot_result.get("new_password")
                        else:
                            logger.error(f"Bot service returned status {response.status_code}: {response.text}")
                            success = False
                            new_password = None
                            
                except Exception as e:
                    logger.error(f"Failed to call bot service: {e}")
                    success = False
                    new_password = None
                
                if success and new_password:
                    # Check for next session (starts right after this one ends)
                    next_session = db.query(SessionModel).filter(
                        SessionModel.start_time == session.end_time,
                        SessionModel.status == "pending"
                    ).first()
                    
                    if next_session:
                        # Send email to next user
                        email_sent = email_service.send_credentials_email(
                            user_name=next_session.user_name,
                            user_email=next_session.user_email,
                            password=new_password,
                            start_time=next_session.start_time.isoformat(),
                            end_time=next_session.end_time.isoformat()
                        )
                        
                        if email_sent:
                            # Update next session status
                            next_session.status = "active"
                            password_entry_data = password_service.create_password_entry(
                                password=new_password,
                                session_id=next_session.id
                            )
                            
                            # Save password to database
                            next_password_entry = Password(**password_entry_data)
                            db.add(next_password_entry)
                            db.commit()
                            db.refresh(next_password_entry)
                            
                            next_session.current_password_id = next_password_entry.id
                    
                    # Update current session status
                    session.status = "completed"
                    db.commit()
                    logger.info(f"Session {session.id} ended successfully")
                else:
                    logger.error(f"Failed to reset password after session {session.id}")
                    
            except Exception as e:
                logger.error(f"Failed to end session {session.id}: {e}")
                db.rollback()
        
        if db:
            db.close()
                
    except Exception as e:
        logger.error(f"Session end job failed: {e}")
        if db:
            db.close()


async def midnight_reset_job():
    """
    Midnight Reset Job - Runs every day at 12:00 AM
    Resets all slots to available and clears old sessions for fresh 24-hour cycle
    """
    db = None
    try:
        db = get_database_session()
        # Use West Africa Time (UTC+1)
        wat_tz = pytz.timezone('Africa/Lagos')
        current_time = datetime.now(wat_tz).replace(tzinfo=None)
        
        logger.info(f"Starting midnight reset job at {current_time}")
        
        # Reset daily slots using slots_service
        slots_service.reset_daily_slots(db, current_time)
        
        logger.info("Midnight reset job completed successfully")
        
        if db:
            db.close()
            
    except Exception as e:
        logger.error(f"Midnight reset job failed: {e}")
        if db:
            db.close()