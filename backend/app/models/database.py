from sqlalchemy import create_engine, Column, Integer, String, DateTime, Boolean, Text, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship
from sqlalchemy.sql import func
from datetime import datetime
from app.core.config import settings

# Database setup
engine = create_engine(settings.database_url)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


# Database Models (from instructions.md schema)
class User(Base):
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String(255), nullable=False, unique=True)
    name = Column(String(255), nullable=False)
    user_type = Column(String(20), nullable=False, default='one_off')  # 'one_off', 'manager', 'team_member'
    
    # Manager-specific
    tenant_id = Column(Integer, nullable=True)  # For managers: their tenant
    
    # Team member-specific  
    team_tenant_id = Column(Integer, nullable=True)  # For team members: manager's tenant
    
    # Password auth (for managers only)
    password_hash = Column(String(255), nullable=True)  # Only for managers
    must_change_password = Column(Boolean, default=False)  # Force password change on first login
    
    # Usage tracking
    total_sessions = Column(Integer, default=0)
    total_hours = Column(Text, default='0.0')  # Store as text to avoid decimal precision issues
    
    # Marketing
    marketing_consent = Column(Boolean, default=False)
    
    # Subscription
    subscription_status = Column(String(20), default="inactive")
    subscription_expires_at = Column(DateTime, nullable=True)
    paystack_customer_code = Column(String(100), nullable=True)
    paystack_authorization_code = Column(String(255), nullable=True)
    
    # Timestamps
    created_at = Column(DateTime, default=func.now())
    last_login_at = Column(DateTime, nullable=True)
    
    # Relationships
    sessions = relationship("Session", back_populates="user")


class AuthToken(Base):
    __tablename__ = "auth_tokens"
    
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String(255), nullable=False, index=True)
    token = Column(String(255), unique=True, nullable=False, index=True)
    expires_at = Column(DateTime, nullable=False)
    used_at = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=func.now())


class Password(Base):
    __tablename__ = "passwords"
    
    id = Column(Integer, primary_key=True, index=True)
    password_hash = Column(String(255), nullable=False)
    plain_password = Column(String(255))  # Store temporarily for email, delete after 1 hour
    session_id = Column(Integer, ForeignKey("sessions.id"))
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=func.now())
    expires_at = Column(DateTime)
    
    # Relationships
    session = relationship("Session", back_populates="passwords")


class TimeSlot(Base):
    __tablename__ = "time_slots"
    __table_args__ = {'extend_existing': True}
    
    id = Column(String(50), primary_key=True, index=True)  # tenant_1_slot_1, slot_1 (for Slotio)
    slot_number = Column(Integer, nullable=False, index=True)  # 1, 2, 3, ..., 16
    start_time = Column(DateTime, nullable=False, index=True)
    end_time = Column(DateTime, nullable=False, index=True)
    date = Column(DateTime, nullable=False, index=True)  # Date this slot belongs to (for daily reset)
    available = Column(Boolean, default=True, index=True)
    tenant_id = Column(Integer, ForeignKey("tenants.id"), nullable=True, index=True)  # NULL = Slotio pool
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())
    
    # Relationships
    sessions = relationship("Session", back_populates="time_slot")


class Session(Base):
    __tablename__ = "sessions"
    __table_args__ = {'extend_existing': True}
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    user_name = Column(String(255))
    user_email = Column(String(255))
    start_time = Column(DateTime, nullable=False)
    end_time = Column(DateTime, nullable=False)
    status = Column(String(50), default="pending")  # pending, active, completed, no-show
    current_password_id = Column(Integer)
    next_user_email = Column(String(255))
    slot_id = Column(String(20), ForeignKey("time_slots.id"), nullable=True)  # Link to TimeSlot
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())
    
    # Relationships
    user = relationship("User", back_populates="sessions")
    passwords = relationship("Password", back_populates="session")
    time_slot = relationship("TimeSlot", back_populates="sessions")


class Tenant(Base):
    __tablename__ = "tenants"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255))  # Team name
    manager_id = Column(Integer, ForeignKey("users.id"), unique=True, nullable=True)  # Nullable for Slotio accounts
    capcut_email = Column(String(255))
    capcut_password_encrypted = Column(Text)
    gmail_email = Column(String(255))  
    gmail_password_encrypted = Column(Text)
    is_slotio_account = Column(Boolean, default=False)  # Platform vs manager account
    subscription_status = Column(String(20), default="active")
    allow_multiple_bookings = Column(Boolean, default=False)  # Toggle for multiple bookings per day
    total_team_sessions = Column(Integer, default=0)  # Team usage stats
    total_team_hours = Column(Integer, default=0)
    created_at = Column(DateTime, default=func.now())
    
    manager = relationship("User", foreign_keys=[manager_id])
    team_members = relationship("TeamMember", back_populates="tenant")


class TeamMember(Base):
    __tablename__ = "team_members"
    
    id = Column(Integer, primary_key=True, index=True)
    tenant_id = Column(Integer, ForeignKey("tenants.id"), nullable=False)
    email = Column(String(255), nullable=False)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    added_at = Column(DateTime, default=func.now())
    
    tenant = relationship("Tenant", back_populates="team_members")
    user = relationship("User", foreign_keys=[user_id])
    
    __table_args__ = (
        {"extend_existing": True},
    )


class DailyLog(Base):
    __tablename__ = "daily_logs"
    
    id = Column(Integer, primary_key=True, index=True)
    date = Column(DateTime)
    total_slots = Column(Integer)
    booked_slots = Column(Integer)
    no_shows = Column(Integer)
    created_at = Column(DateTime, default=func.now())


class Payment(Base):
    __tablename__ = "payments"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    reference = Column(String(100), unique=True, nullable=False, index=True)
    amount = Column(Integer, nullable=False)  # In kobo
    type = Column(String(20), nullable=False)  # session, subscription
    status = Column(String(20), default="pending", index=True)
    paystack_response = Column(Text, nullable=True)
    created_at = Column(DateTime, default=func.now())
    
    user = relationship("User")


class BotJob(Base):
    __tablename__ = "bot_jobs"
    
    id = Column(Integer, primary_key=True, index=True)
    session_id = Column(Integer, ForeignKey("sessions.id"), nullable=False)
    job_type = Column(String(50), nullable=False)  # password_reset, session_end
    status = Column(String(20), default="pending", index=True)  # pending, processing, completed, failed
    attempts = Column(Integer, default=0)
    error_message = Column(Text, nullable=True)
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())
    
    session = relationship("Session")


# Database dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# Create tables
def create_tables():
    Base.metadata.create_all(bind=engine)