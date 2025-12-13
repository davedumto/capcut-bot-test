from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.models.database import get_db, User, Payment, Session as SessionModel
from pydantic import BaseModel, EmailStr
from app.services.auth_service import auth_service
import json

router = APIRouter()

class CompleteBookingRequest(BaseModel):
    reference: str
    email: EmailStr
    name: str
    marketing_consent: bool = False

@router.post("/complete-booking")
async def complete_booking(req: CompleteBookingRequest, db: Session = Depends(get_db)):
    """
    Complete anonymous booking after payment
    Creates user account and links to session
    """
    #Verify payment
    payment = db.query(Payment).filter_by(reference=req.reference).first()
    if not payment:
        raise HTTPException(404, "Payment not found")
    
    if payment.status != 'success':
        raise HTTPException(400, "Payment not successful")
    
    # Create or get user
    user = db.query(User).filter_by(email=req.email).first()
    if not user:
        user = User(
            email=req.email,
            name=req.name,
            user_type='one_off',
            marketing_consent=req.marketing_consent
        )
        db.add(user)
        db.flush()
    
    # Link payment to user
    payment.user_id = user.id
    
    # Find session created during booking (has matching email)
    # Get payment details to find session
    paystack_data = json.loads(payment.paystack_response) if payment.paystack_response else {}
    payment_email = paystack_data.get('customer', {}).get('email', req.email)
    
    # Find session with matching email and no user_id
    session = db.query(SessionModel).filter(
        SessionModel.user_email == payment_email,
        SessionModel.user_id.is_(None),
        SessionModel.status == 'pending'
    ).first()
    
    if session:
        # Link session to user
        session.user_id = user.id
        session.user_name = req.name
        session.user_email = req.email
        
        # Update user stats
        user.total_sessions += 1
        user.total_hours = str(float(user.total_hours or "0.0") + 1.5)
    
    db.commit()
    
    # Create JWT token
    token = auth_service.create_jwt_token(user)
    
    return {
        "success": True,
        "user_id": user.id,
        "session_id": session.id if session else None,
        "token": token
    }
