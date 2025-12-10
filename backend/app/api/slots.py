from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from datetime import datetime, timedelta
import pytz
from app.models.database import get_db, Session as SessionModel, TimeSlot
from app.models.schemas import SlotsResponse, TimeSlotSchema
from app.services.slots_service import slots_service

router = APIRouter()

# West Africa Time (UTC+1)
WAT_TZ = pytz.timezone('Africa/Lagos')
def get_wat_now():
    return datetime.now(WAT_TZ).replace(tzinfo=None)


@router.get("/slots", response_model=SlotsResponse)
async def get_available_slots(db: Session = Depends(get_db)):
    """
    Get time slots for today - NOW USES STORED TIMESLOTS
    NEW: 24-hour slots from 12:00 AM to 12:00 AM (16 slots × 1.5 hours)
    - Each slot is 1.5 hours (90 minutes)
    - Slots are: 12:00-1:30, 1:30-3:00, 3:00-4:30, etc.
    - Last slot: 10:30 PM - 12:00 AM (ends exactly at midnight)
    - Returns stored TimeSlot data with real availability status
    """
    try:
        current_time = get_wat_now()
        
        # Get stored slots from database using slots_service
        # This automatically initializes slots if they don't exist
        stored_slots = slots_service.get_available_slots(db, current_time)
        
        # Convert stored TimeSlots to TimeSlotSchema for API response
        slots = []
        
        for stored_slot in stored_slots:
            # Check if slot has actually started (for past slots)
            slot_has_started = stored_slot.start_time <= current_time
            
            # Check if there's an active session for this slot
            existing_session = db.query(SessionModel).filter(
                SessionModel.slot_id == stored_slot.id,
                SessionModel.status.in_(["pending", "active"])
            ).first()
            
            # Slot is available if:
            # 1. Marked as available in database
            # 2. Has not started yet (current time is before slot start time)  
            # 3. No active session exists for this slot
            is_available = (
                stored_slot.available and 
                not slot_has_started and 
                existing_session is None
            )
            
            slots.append(TimeSlotSchema(
                id=stored_slot.id,  # slot_1, slot_2, etc.
                start_time=stored_slot.start_time.isoformat(),
                end_time=stored_slot.end_time.isoformat(),
                available=is_available
            ))
        
        return SlotsResponse(slots=slots)
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get slots: {str(e)}")