from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
import logging
import os
from services.capcut_bot import reset_password_forgot_flow
from services.password_generator import generate_strong_password

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
        # Use CAPCUT_EMAIL from env if not provided
        if not request.email:
            request.email = os.getenv('CAPCUT_EMAIL')
            
        # Generate password if not provided
        if not request.new_password:
            request.new_password = generate_strong_password()
        
        logger.info(f"Starting password reset for {request.email}")
        
        # Run the forgot password flow
        result = await reset_password_forgot_flow(
            email=request.email,
            new_password=request.new_password
        )
        
        if result["success"]:
            logger.info(f"Password reset successful for {request.email}")
            return ResetPasswordResponse(
                success=True,
                new_password=request.new_password,
                message="Password reset successfully"
            )
        else:
            logger.error(f"Password reset failed: {result['message']}")
            raise HTTPException(
                status_code=500,
                detail=f"Password reset failed: {result['message']}"
            )
            
    except Exception as e:
        logger.error(f"Error in reset_password: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Error: {str(e)}"
        )