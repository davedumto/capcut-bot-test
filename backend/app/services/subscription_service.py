from app.models.database import SessionLocal, User
from app.services.paystack_service import paystack_service
from datetime import datetime, timedelta
from sqlalchemy import text

def create_subscription(user: User, authorization_code: str, customer_code: str, db_session):
    """Activate subscription after first payment"""
    user.subscription_status = 'active'
    user.subscription_expires_at = datetime.now() + timedelta(days=30)
    user.paystack_customer_code = customer_code
    user.paystack_authorization_code = authorization_code
    db_session.commit()

def charge_subscription(user: User):
    """Charge saved card for renewal"""
    if not user.paystack_authorization_code:
        return {"success": False, "message": "No saved card"}
    
    amount = 500000  # ₦5,000 in kobo
    
    result = paystack_service.charge_authorization(
        authorization_code=user.paystack_authorization_code,
        email=user.email,
        amount=amount
    )
    
    return result

def renew_all_subscriptions():
    """Cron job to renew expiring subscriptions"""
    db = SessionLocal()
    
    try:
        # Find subscriptions expiring today or earlier
        today = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
        expiring_users = db.query(User).filter(
            User.user_type == 'manager',
            User.subscription_status == 'active',
            User.subscription_expires_at <= today
        ).all()
        
        print(f"Found {len(expiring_users)} subscriptions to renew")
        
        for user in expiring_users:
            result = charge_subscription(user)
            
            if result.get('status') and result.get('data', {}).get('status') == 'success':
                # Renewal successful
                user.subscription_expires_at = datetime.now() + timedelta(days=30)
                print(f"✅ Renewed subscription for {user.email}")
            else:
                # Renewal failed
                user.subscription_status = 'expired'
                print(f"❌ Failed to renew subscription for {user.email}: {result.get('message')}")
        
        db.commit()
        return {"renewed": len([u for u in expiring_users if u.subscription_status == 'active'])}
        
    finally:
        db.close()
