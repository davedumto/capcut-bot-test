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
    Get time slots for today - SLOTIO POOL ONLY (for one-off users)
    - Returns only slots with tenant_id=NULL (Slotio accounts)
    - Team members use /api/users/team-member-data instead
    """
    try:
        current_time = get_wat_now()
        
        # Get stored slots from database using slots_service
        # Pass tenant_id=None for Slotio pool (one-off users)
        stored_slots = slots_service.get_available_slots(db, current_time, tenant_id=None)
        
        # Get Slotio account count for capacity check
        from app.models.database import Tenant
        slotio_count = db.query(Tenant).filter_by(is_slotio_account=True).count()
        
        if slotio_count == 0:
            slotio_count = 1  # Default to 1 if no accounts configured yet
        
        # Initialize slots list
        slots = []
        
        for stored_slot in stored_slots:
            # Check if slot has actually started (for past slots)
            slot_has_started = stored_slot.start_time <= current_time
            
            # Count existing bookings for this slot
            booking_count = db.query(SessionModel).filter(
                SessionModel.slot_id == stored_slot.id,
                SessionModel.status.in_(["pending", "active"])
            ).count()
            
            # Slot is available if:
            # 1. Has not started yet (current time is before slot start time)  
            # 2. Booking count is less than Slotio account count
            is_available = (
                not slot_has_started and 
                booking_count < slotio_count
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