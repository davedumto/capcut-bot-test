from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.orm import Session
from datetime import datetime, timedelta
import pytz
import secrets
from pydantic import BaseModel
from app.models.database import get_db, User, Session as SessionModel, TimeSlot, Payment, Tenant
from app.models.schemas import BookingRequest, BookingResponse
from app.services.slots_service import slots_service
from app.services.paystack_service import paystack_service
from app.core.security import verify_token

router = APIRouter()

# West Africa Time (UTC+1)
WAT_TZ = pytz.timezone('Africa/Lagos')
def get_wat_now():
    return datetime.now(WAT_TZ).replace(tzinfo=None)


@router.get("/bookings/price")
async def get_booking_price(email: str, db: Session = Depends(get_db)):
    """Get the current booking price for a user based on today's bookings"""
    today_start = get_wat_now().replace(hour=0, minute=0, second=0, microsecond=0)
    today_end = today_start + timedelta(days=1)
    
    bookings_today = db.query(SessionModel).filter(
        SessionModel.user_email == email,
        SessionModel.created_at >= today_start,
        SessionModel.created_at < today_end
    ).count()
    
    # Pricing: 1st slot = ₦500, additional slots = ₦1000
    base_price = 500
    if bookings_today == 0:
        price = base_price
    else:
        price = base_price * 2  # ₦1000 for additional slots
    
    return {
        "price": price,
        "price_kobo": price * 100,
        "bookings_today": bookings_today,
        "is_first_booking": bookings_today == 0
    }


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
        current_time = get_wat_now()
        if slot_start <= current_time:
            raise HTTPException(
                status_code=400,
                detail="This slot has already started. Please choose a future slot."
            )
        
        # Removed: one-booking-per-day limit
        # Users can now book multiple slots per day, but additional slots cost extra
        
        # Count user's bookings today for pricing
        today_start = get_wat_now().replace(hour=0, minute=0, second=0, microsecond=0)
        today_end = today_start + timedelta(days=1)
        
        bookings_today = db.query(SessionModel).filter(
            SessionModel.user_email == booking.email,
            SessionModel.created_at >= today_start,
            SessionModel.created_at < today_end
        ).count()
        
        # Pricing: 1st slot = ₦500, additional slots = ₦1000 (₦500 + ₦500 extra)
        base_price_kobo = 50000  # ₦500 in kobo
        if bookings_today == 0:
            price_kobo = base_price_kobo  # ₦500 for first slot
        else:
            price_kobo = base_price_kobo * 2  # ₦1000 for additional slots
        
        # Validation: Check slot capacity (N bookings where N = Slotio accounts)
        from app.models.database import Tenant
        
        # Get Slotio account count
        slotio_accounts = db.query(Tenant).filter_by(is_slotio_account=True).all()
        slotio_count = len(slotio_accounts)
        
        if slotio_count == 0:
            raise HTTPException(
                status_code=500,
                detail="No Slotio accounts configured. Please contact support."
            )
        
        # Count existing bookings for this slot
        existing_bookings = db.query(SessionModel).filter(
            SessionModel.slot_id == booking.slot_id,
            SessionModel.status.in_(["pending", "active"])
        ).all()
        
        current_booking_count = len(existing_bookings)
        
        # Check if slot is full
        if current_booking_count >= slotio_count:
            raise HTTPException(
                status_code=400,
                detail=f"This slot is fully booked ({current_booking_count}/{slotio_count} capacity)"
            )
        
        # Create or get user
        user = db.query(User).filter_by(email=booking.email).first()
        if not user:
            user = User(name=booking.name, email=booking.email, user_type='one_off')
            db.add(user)
            db.flush()
        
        # Create new session
        session = SessionModel(
            user_id=user.id,
            user_name=user.name,
            user_email=user.email,
            start_time=stored_slot.start_time,
            end_time=stored_slot.end_time,
            status="pending",
            slot_id=stored_slot.id
        )
        db.add(session)
        db.flush()
        
        # Create payment with progressive pricing
        reference = f"pst_{secrets.token_hex(16)}"
        payment = Payment(
            user_id=user.id,
            reference=reference,
            amount=price_kobo,  # Progressive price based on bookings today
            type='session',
            status='pending'
        )
        db.add(payment)
        
        # Initialize payment with progressive price
        paystack_result = paystack_service.initialize_transaction(
            email=booking.email,
            amount=price_kobo,
            reference=reference
        )
        
        if not paystack_result.get('status'):
            raise HTTPException(400, "Payment initialization failed")
        
        # Commit transaction
        db.commit()
        
        return BookingResponse(
            success=True,
            session_id=str(session.id),
            message="Proceed to payment",
            payment_reference=reference,
            authorization_url=paystack_result['data']['authorization_url']
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to create booking: {str(e)}")


class TeamBookingRequest(BaseModel):
    slot_id: str


@router.post("/team-bookings")
async def create_team_booking(booking: TeamBookingRequest, request: Request, db: Session = Depends(get_db)):
    """
    Create a booking for a team member - no payment required.
    Uses authenticated user from cookie.
    """
    try:
        # Get user from cookie
        access_token = request.cookies.get("access_token")
        if not access_token:
            raise HTTPException(401, "Not authenticated")
        
        payload = verify_token(access_token)
        if not payload:
            raise HTTPException(401, "Invalid token")
        
        user_id = payload.get("sub")
        user = db.query(User).filter_by(id=int(user_id)).first()
        
        if not user:
            raise HTTPException(404, "User not found")
        
        if user.user_type != "team_member":
            raise HTTPException(403, "Only team members can use this endpoint")
        
        # Get manager's tenant 
        tenant = db.query(Tenant).filter_by(id=user.team_tenant_id).first()
        
        # Check if user already has a booking today (if multiple bookings not allowed)
        if tenant and not tenant.allow_multiple_bookings:
            today_start = get_wat_now().replace(hour=0, minute=0, second=0, microsecond=0)
            today_end = today_start + timedelta(days=1)
            
            existing_booking = db.query(SessionModel).filter(
                SessionModel.user_id == user.id,
                SessionModel.start_time >= today_start,
                SessionModel.start_time < today_end,
                SessionModel.status.in_(["paid", "active"])
            ).first()
            
            if existing_booking:
                raise HTTPException(400, "You already have a booking for today. Only one booking per day is allowed.")
        
        # Get the slot
        stored_slot = slots_service.get_slot_by_id(db, booking.slot_id)
        if not stored_slot:
            raise HTTPException(404, f"Slot {booking.slot_id} not found")
        
        if not stored_slot.available:
            raise HTTPException(400, "Slot is no longer available")
        
        # Verify slot hasn't started
        current_time = get_wat_now()
        if stored_slot.start_time <= current_time:
            raise HTTPException(400, "Cannot book a slot that has already started")
        
        # Create session without payment
        session = SessionModel(
            user_id=user.id,
            user_name=user.name,
            user_email=user.email,
            start_time=stored_slot.start_time,
            end_time=stored_slot.end_time,
            status="paid",  # Already paid through manager's subscription
            slot_id=stored_slot.id
        )
        
        db.add(session)
        
        # Mark slot as unavailable
        stored_slot.available = False
        
        db.commit()
        db.refresh(session)
        
        return {
            "success": True,
            "session_id": str(session.id),
            "message": "Booking confirmed! No payment required for team members."
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to create booking: {str(e)}")