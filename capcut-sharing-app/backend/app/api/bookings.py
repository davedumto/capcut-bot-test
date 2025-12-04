from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from datetime import datetime, timedelta
from app.models.database import get_db, User, Session as SessionModel, TimeSlot
from app.models.schemas import BookingRequest, BookingResponse
from app.services.slots_service import slots_service

router = APIRouter()


@router.post("/bookings", response_model=BookingResponse)
async def create_booking(booking: BookingRequest, db: Session = Depends(get_db)):
    """
    Create a new booking
    As per instructions.md:
    - Validate email hasn't booked a slot today
    - Validate name hasn't booked a slot today  
    - Validate slot is still available
    - Save booking to database
    """
    try:
        # Get the actual stored TimeSlot from database
        stored_slot = slots_service.get_slot_by_id(db, booking.slot_id)
        
        if not stored_slot:
            raise HTTPException(
                status_code=404,
                detail=f"Slot {booking.slot_id} not found. Please refresh the page and try again."
            )
        
        # Use stored slot times (more accurate than calculated times)
        slot_start = stored_slot.start_time
        slot_end = stored_slot.end_time
        
        # Verify slot is still available
        if not stored_slot.available:
            raise HTTPException(
                status_code=400,
                detail="This slot is no longer available. Please choose a different slot."
            )
        
        # Verify slot hasn't already started
        current_time = datetime.now()
        if slot_start <= current_time:
            raise HTTPException(
                status_code=400,
                detail="This slot has already started. Please choose a future slot."
            )
        
        # Validation 1: Check if email hasn't booked today
        today_start = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
        today_end = today_start + timedelta(days=1)
        
        existing_email_booking = db.query(SessionModel).filter(
            SessionModel.user_email == booking.email,
            SessionModel.created_at >= today_start,
            SessionModel.created_at < today_end,
            SessionModel.status.in_(["pending", "active"])
        ).first()
        
        if existing_email_booking:
            raise HTTPException(
                status_code=400, 
                detail="This email has already booked a slot today. Each email can only book one slot per day."
            )
        
        # Validation 2: Check if name hasn't booked today
        existing_name_booking = db.query(SessionModel).filter(
            SessionModel.user_name == booking.name,
            SessionModel.created_at >= today_start,
            SessionModel.created_at < today_end,
            SessionModel.status.in_(["pending", "active"])
        ).first()
        
        if existing_name_booking:
            raise HTTPException(
                status_code=400, 
                detail="This name has already booked a slot today. Each name can only book one slot per day."
            )
        
        # Validation 3: Double-check no session exists for this specific slot
        existing_slot_booking = db.query(SessionModel).filter(
            SessionModel.slot_id == booking.slot_id,
            SessionModel.status.in_(["pending", "active"])
        ).first()
        
        if existing_slot_booking:
            raise HTTPException(
                status_code=400, 
                detail="This slot is no longer available"
            )
        
        # Create or get user
        user = db.query(User).filter(User.email == booking.email).first()
        if not user:
            user = User(name=booking.name, email=booking.email)
            db.add(user)
            db.commit()
            db.refresh(user)
        
        # Create session with slot_id reference
        session = SessionModel(
            user_id=user.id,
            user_name=booking.name,
            user_email=booking.email,
            start_time=slot_start,
            end_time=slot_end,
            status="pending",
            slot_id=booking.slot_id  # Link to TimeSlot
        )
        
        db.add(session)
        
        # Mark the slot as booked
        slots_service.mark_slot_booked(db, booking.slot_id)
        
        db.commit()
        db.refresh(session)
        
        return BookingResponse(
            success=True,
            session_id=f"sess_{session.id}",
            message="Booked successfully"
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to create booking: {str(e)}")