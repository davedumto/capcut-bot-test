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
    name = Column(String(255), nullable=False)
    email = Column(String(255), nullable=False, unique=True)
    created_at = Column(DateTime, default=func.now())
    
    # Relationships
    sessions = relationship("Session", back_populates="user")




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
    
    id = Column(String(20), primary_key=True, index=True)  # slot_1, slot_2, etc.
    slot_number = Column(Integer, nullable=False, index=True)  # 1, 2, 3, ..., 16
    start_time = Column(DateTime, nullable=False, index=True)
    end_time = Column(DateTime, nullable=False, index=True)
    date = Column(DateTime, nullable=False, index=True)  # Date this slot belongs to (for daily reset)
    available = Column(Boolean, default=True, index=True)
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


class DailyLog(Base):
    __tablename__ = "daily_logs"
    
    id = Column(Integer, primary_key=True, index=True)
    date = Column(DateTime)
    total_slots = Column(Integer)
    booked_slots = Column(Integer)
    no_shows = Column(Integer)
    created_at = Column(DateTime, default=func.now())


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