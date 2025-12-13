from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.orm import Session
from app.models.database import get_db, Payment, User
from app.services.paystack_service import paystack_service
from pydantic import BaseModel, EmailStr
from datetime import datetime, timedelta
import secrets
import json

router = APIRouter()

class PaymentInitRequest(BaseModel):
    email: EmailStr
    amount: int
    type: str  # 'session' or 'subscription'

@router.post("/initialize")
def initialize_payment(req: PaymentInitRequest, db: Session = Depends(get_db)):
    user = db.query(User).filter_by(email=req.email).first()
    if not user:
        user = User(email=req.email, name=req.email.split('@')[0], user_type='one_off')
        db.add(user)
        db.commit()
        db.refresh(user)
    
    reference = f"pst_{secrets.token_hex(16)}"
    
    payment = Payment(
        user_id=user.id,
        reference=reference,
        amount=req.amount,
        type=req.type,
        status='pending'
    )
    db.add(payment)
    db.commit()
    
    result = paystack_service.initialize_transaction(req.email, req.amount, reference)
    
    if not result.get('status'):
        raise HTTPException(400, "Payment initialization failed")
    
    return {
        "authorization_url": result['data']['authorization_url'],
        "reference": reference
    }

@router.post("/webhook")
async def paystack_webhook(request: Request, db: Session = Depends(get_db)):
    signature = request.headers.get('x-paystack-signature')
    body = await request.body()
    
    if not paystack_service.verify_signature(body, signature):
        raise HTTPException(400, "Invalid signature")
    
    event = json.loads(body)
    
    if event['event'] == 'charge.success':
        reference = event['data']['reference']
        payment = db.query(Payment).filter_by(reference=reference).first()
        
        if payment:
            payment.status = 'success'
            payment.paystack_response = json.dumps(event['data'])
            
            # Handle subscription activation
            if payment.type == 'subscription':
                user = db.query(User).filter_by(id=payment.user_id).first()
                if user:
                    user.subscription_status = 'active'
                    user.subscription_expires_at = datetime.now() + timedelta(days=30)
                    
                    authorization = event['data'].get('authorization', {})
                    user.paystack_authorization_code = authorization.get('authorization_code')
                    user.paystack_customer_code = event['data'].get('customer', {}).get('customer_code')
            
            db.commit()
    
    return {"status": "ok"}

@router.get("/verify/{reference}")
def verify_payment(reference: str, db: Session = Depends(get_db)):
    payment = db.query(Payment).filter_by(reference=reference).first()
    if not payment:
        raise HTTPException(404, "Payment not found")
    
    result = paystack_service.verify_transaction(reference)
    
    if result.get('status') and result['data']['status'] == 'success':
        payment.status = 'success'
        payment.paystack_response = json.dumps(result['data'])
        db.commit()
    
    return {
        "status": payment.status,
        "amount": payment.amount,
        "type": payment.type
    }


@router.get("/history")
def get_payment_history(request: Request, db: Session = Depends(get_db)):
    """Get payment history for authenticated user"""
    # Get user from cookie
    from app.core.security import verify_token
    access_token = request.cookies.get("access_token")
    
    if not access_token:
        raise HTTPException(401, "Not authenticated")
    
    payload = verify_token(access_token)
    if not payload:
        raise HTTPException(401, "Invalid token")
    
    # Get email from token and find user
    email = payload.get("email")
    user = db.query(User).filter_by(email=email).first()
    
    if not user:
        return {"payments": []}
    
    # Get all payments for this user by user_id
    payments = db.query(Payment).filter_by(user_id=user.id).order_by(Payment.created_at.desc()).all()
    
    return {
        "payments": [
            {
                "id": p.id,
                "amount": p.amount,
                "status": p.status,
                "type": p.type,
                "reference": p.reference,
                "created_at": p.created_at.isoformat()
            }
            for p in payments
        ]
    }

