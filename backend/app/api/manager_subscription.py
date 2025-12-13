from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.models.database import get_db, User, Payment
from app.services.paystack_service import paystack_service
from app.core.security import get_current_user
from datetime import datetime, timedelta
import secrets
import json

router = APIRouter()

@router.post("/subscribe")
async def initialize_subscription(
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    user = db.query(User).filter_by(email=current_user["email"]).first()
    if not user or user.user_type != 'manager':
        raise HTTPException(403, "Only managers can subscribe")
    
    if user.subscription_status == 'active':
        raise HTTPException(400, "Already subscribed")
    
    reference = f"sub_{secrets.token_hex(16)}"
    amount = 500000
    
    payment = Payment(
        user_id=user.id,
        reference=reference,
        amount=amount,
        type='subscription',
        status='pending'
    )
    db.add(payment)
    db.commit()
    
    result = paystack_service.initialize_transaction(
        email=user.email,
        amount=amount,
        reference=reference,
        callback_path="/manager/subscribe/activate"
    )
    
    if not result.get('status'):
        raise HTTPException(400, "Payment initialization failed")
    
    return {
        "authorization_url": result['data']['authorization_url'],
        "reference": reference
    }

@router.get("/status")
async def get_subscription_status(
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    user = db.query(User).filter_by(email=current_user["email"]).first()
    if not user:
        raise HTTPException(404, "User not found")
    
    # Get subscription status from TENANT, not User
    subscription_status = None
    expires_at = None
    days_remaining = None
    
    if user.tenant_id:
        from app.models.database import Tenant
        tenant = db.query(Tenant).filter_by(id=user.tenant_id).first()
        if tenant:
            subscription_status = tenant.subscription_status
    
    return {
        "subscription_status": subscription_status or "inactive",
        "status": subscription_status or "inactive",  # For backward compat
        "expires_at": expires_at,
        "days_remaining": days_remaining
    }

@router.post("/activate")
async def activate_subscription(
    reference: str,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    user = db.query(User).filter_by(email=current_user["email"]).first()
    if not user:
        raise HTTPException(404, "User not found")
    
    payment = db.query(Payment).filter_by(reference=reference, user_id=user.id).first()
    if not payment or payment.status != 'success':
        raise HTTPException(400, "Payment not successful")
    
    paystack_data = json.loads(payment.paystack_response) if payment.paystack_response else {}
    authorization = paystack_data.get('authorization', {})
    
    if not authorization.get('authorization_code'):
        raise HTTPException(400, "No authorization code found")
    
    user.subscription_status = 'active'
    user.subscription_expires_at = datetime.now() + timedelta(days=30)
    user.paystack_customer_code = paystack_data.get('customer', {}).get('customer_code')
    user.paystack_authorization_code = authorization.get('authorization_code')
    db.commit()
    
    return {
        "success": True,
        "status": user.subscription_status,
        "expires_at": user.subscription_expires_at.isoformat()
    }
