from sqlalchemy.orm import Session
from app.models.database import User
from decimal import Decimal

class UsageService:
    
    def track_session(self, user_email: str, hours: float, db: Session):
        user = db.query(User).filter_by(email=user_email).first()
        if not user:
            return False
        
        user.total_sessions += 1
        current_hours = Decimal(user.total_hours)
        user.total_hours = str(current_hours + Decimal(str(hours)))
        db.commit()
        return True
    
    def get_stats(self, user_email: str, db: Session):
        user = db.query(User).filter_by(email=user_email).first()
        if not user:
            return None
        
        return {
            "total_sessions": user.total_sessions,
            "total_hours": float(user.total_hours),
            "avg_session_hours": float(user.total_hours) / max(user.total_sessions, 1)
        }

usage_service = UsageService()