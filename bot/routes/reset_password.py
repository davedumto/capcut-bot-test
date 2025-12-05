from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
import logging
import os
import traceback
import sys

# Add parent directory to path to import bot.py
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Import the WORKING bot class from bot.py (not the broken services/capcut_bot.py)
from bot import CapCutPasswordResetBot

router = APIRouter()
logger = logging.getLogger(__name__)

class ResetPasswordRequest(BaseModel):
    email: str = None  # Will use CAPCUT_EMAIL from env if not provided
    new_password: str = None  # Optional, generates if not provided

class ResetPasswordResponse(BaseModel):
    success: bool
    new_password: str = None
    message: str

@router.post("/reset-password", response_model=ResetPasswordResponse)
async def reset_password(request: ResetPasswordRequest):
    """
    Reset CapCut password using forgot password flow
    
    Called by backend scheduler when:
    - Session starts (needs initial password)
    - Session ends (needs new password for next user)
    
    Returns: {"success": true, "new_password": "..."}
    """
    try:
        # Get credentials from environment
        capcut_email = request.email or os.getenv('CAPCUT_EMAIL')
        gmail_email = os.getenv('GMAIL_EMAIL')
        gmail_app_password = os.getenv('GMAIL_APP_PASSWORD')
        
        if not capcut_email:
            raise ValueError("CAPCUT_EMAIL environment variable not set")
        if not gmail_email:
            raise ValueError("GMAIL_EMAIL environment variable not set")
        if not gmail_app_password:
            raise ValueError("GMAIL_APP_PASSWORD environment variable not set")
        
        logger.info(f"Starting password reset for {capcut_email}")
        
        # Use the WORKING CapCutPasswordResetBot class from bot.py
        # This has cookies handling, robust selectors, and anti-detection
        bot = CapCutPasswordResetBot(
            capcut_email=capcut_email,
            gmail_email=gmail_email,
            gmail_app_password=gmail_app_password,
            headless=True  # Run headless in production
        )
        
        # Run the complete 14-step flow
        success, new_password = await bot.run_complete_flow()
        
        if success and new_password:
            logger.info(f"Password reset successful for {capcut_email}")
            return ResetPasswordResponse(
                success=True,
                new_password=new_password,
                message="Password reset successfully"
            )
        else:
            logger.error(f"Password reset failed for {capcut_email}")
            raise HTTPException(
                status_code=500,
                detail="Password reset failed - bot did not succeed"
            )
            
    except HTTPException:
        raise
    except Exception as e:
        error_msg = f"Error: {str(e)}"
        logger.error(f"Error in reset_password: {error_msg}")
        logger.error(f"Full traceback: {traceback.format_exc()}")
        raise HTTPException(
            status_code=500,
            detail=error_msg
        )