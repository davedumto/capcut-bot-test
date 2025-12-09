"""
Slots Service - Manages 24-hour slot generation and daily reset
Provides smooth integration with existing system
"""

from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from app.models.database import TimeSlot, Session as SessionModel
import logging

logger = logging.getLogger(__name__)

class SlotsService:
    
    def generate_daily_slots(self, db: Session, target_date: datetime = None) -> list[TimeSlot]:
        """
        Generate 16 slots for a 24-hour period (12:00 AM - 12:00 AM)
        Each slot is 1.5 hours (90 minutes)
        
        Slot Schedule:
        1. 12:00 AM - 1:30 AM
        2. 1:30 AM - 3:00 AM  
        3. 3:00 AM - 4:30 AM
        ...continuing every 1.5 hours...
        16. 10:30 PM - 12:00 AM
        """
        if target_date is None:
            target_date = datetime.now()
        
        # Start at midnight of the target date
        day_start = target_date.replace(hour=0, minute=0, second=0, microsecond=0)
        
        slots = []
        
        for slot_number in range(1, 17):  # 16 slots total
            # Each slot starts 90 minutes after the previous
            slot_start = day_start + timedelta(minutes=90 * (slot_number - 1))
            slot_end = slot_start + timedelta(minutes=90)
            
            # Create slot with familiar ID format (slot_1, slot_2, etc.)
            slot_id = f"slot_{slot_number}"
            
            slot = TimeSlot(
                id=slot_id,
                slot_number=slot_number,
                start_time=slot_start,
                end_time=slot_end,
                date=day_start,
                available=True
            )
            
            slots.append(slot)
            
        return slots
    
    def initialize_daily_slots(self, db: Session, target_date: datetime = None) -> None:
        """
        Initialize slots for a specific date.
        Safe to call multiple times - will not duplicate slots.
        """
        if target_date is None:
            target_date = datetime.now()
        
        day_start = target_date.replace(hour=0, minute=0, second=0, microsecond=0)
        
        # Check if slots already exist for this date
        existing_slots = db.query(TimeSlot).filter(
            TimeSlot.date == day_start
        ).count()
        
        if existing_slots > 0:
            logger.info(f"Slots already exist for {day_start.date()}, skipping initialization")
            return
        
        # Generate and save new slots one by one to handle any conflicts
        slots = self.generate_daily_slots(db, target_date)
        
        for slot in slots:
            try:
                # Check if this specific slot already exists
                existing_slot = db.query(TimeSlot).filter(TimeSlot.id == slot.id).first()
                if not existing_slot:
                    db.add(slot)
                    db.flush()  # Flush to catch any conflicts early
            except Exception as e:
                logger.warning(f"Slot {slot.id} might already exist, skipping: {e}")
                db.rollback()
                continue
        
        try:
            db.commit()
            logger.info(f"Created slots for {day_start.date()}")
        except Exception as e:
            logger.error(f"Error committing slots: {e}")
            db.rollback()
    
    def reset_daily_slots(self, db: Session, target_date: datetime = None) -> None:
        """
        Reset slots for midnight - UPDATE all slots with new day's date and times.
        This happens every day at 12:00 AM.
        
        Since slot IDs are fixed (slot_1 through slot_16), we UPDATE existing slots
        rather than creating new ones.
        """
        if target_date is None:
            target_date = datetime.now()
        
        day_start = target_date.replace(hour=0, minute=0, second=0, microsecond=0)
        
        # 1. Clear old completed sessions from previous day
        previous_day = day_start - timedelta(days=1)
        old_sessions = db.query(SessionModel).filter(
            SessionModel.start_time >= previous_day,
            SessionModel.start_time < day_start,
            SessionModel.status.in_(["completed", "no-show"])
        )
        
        deleted_sessions = old_sessions.count()
        old_sessions.delete()
        
        # 2. Update all 16 slots with new day's date and times
        updated_count = 0
        for slot_number in range(1, 17):
            slot_id = f"slot_{slot_number}"
            
            # Calculate new start/end times for this slot
            slot_start = day_start + timedelta(minutes=90 * (slot_number - 1))
            slot_end = slot_start + timedelta(minutes=90)
            
            # Try to get existing slot
            existing_slot = db.query(TimeSlot).filter(TimeSlot.id == slot_id).first()
            
            if existing_slot:
                # UPDATE existing slot with new date/times and mark available
                existing_slot.start_time = slot_start
                existing_slot.end_time = slot_end
                existing_slot.date = day_start
                existing_slot.available = True
                updated_count += 1
            else:
                # CREATE new slot if it doesn't exist (first run)
                new_slot = TimeSlot(
                    id=slot_id,
                    slot_number=slot_number,
                    start_time=slot_start,
                    end_time=slot_end,
                    date=day_start,
                    available=True
                )
                db.add(new_slot)
                updated_count += 1
        
        db.commit()
        
        logger.info(f"Daily reset complete: {updated_count} slots reset for {day_start.date()}, {deleted_sessions} old sessions cleared")
    
    def get_slot_by_id(self, db: Session, slot_id: str) -> TimeSlot:
        """
        Get a specific slot by ID (e.g., 'slot_1', 'slot_2')
        Since slot IDs are unique across the system, no date filter needed.
        """
        return db.query(TimeSlot).filter(
            TimeSlot.id == slot_id
        ).first()
    
    def mark_slot_booked(self, db: Session, slot_id: str) -> bool:
        """
        Mark a slot as booked (available=False)
        Returns True if successful, False if slot not found or already booked
        """
        slot = self.get_slot_by_id(db, slot_id)
        
        if not slot:
            logger.error(f"Slot {slot_id} not found")
            return False
        
        if not slot.available:
            logger.error(f"Slot {slot_id} already booked")
            return False
        
        slot.available = False
        db.commit()
        
        logger.info(f"Marked slot {slot_id} as booked")
        return True
    
    def mark_slot_available(self, db: Session, slot_id: str) -> bool:
        """
        Mark a slot as available (for cancellations, etc.)
        """
        slot = self.get_slot_by_id(db, slot_id)
        
        if not slot:
            logger.error(f"Slot {slot_id} not found")
            return False
        
        slot.available = True
        db.commit()
        
        logger.info(f"Marked slot {slot_id} as available")
        return True
    
    def get_available_slots(self, db: Session, target_date: datetime = None) -> list[TimeSlot]:
        """
        Get all available slots for today.
        If slots don't exist or are from a previous day, reset them.
        """
        if target_date is None:
            target_date = datetime.now()
        
        day_start = target_date.replace(hour=0, minute=0, second=0, microsecond=0)
        
        # Get all slots ordered by slot_number
        slots = db.query(TimeSlot).order_by(TimeSlot.slot_number).all()
        
        # If no slots exist or first slot has wrong date, reset/create them
        if not slots or (slots and slots[0].date != day_start):
            logger.info(f"Slots need reset: found {len(slots)} slots, date mismatch or empty")
            self.reset_daily_slots(db, target_date)
            # Re-fetch after reset
            slots = db.query(TimeSlot).order_by(TimeSlot.slot_number).all()
        
        return slots

# Create singleton instance
slots_service = SlotsService()