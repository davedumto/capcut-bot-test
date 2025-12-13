"""
Database Migration: Add Module 7 & 8 columns
Run this once to add missing columns
"""
from app.models.database import SessionLocal
from sqlalchemy import text

db = SessionLocal()

print("🔄 Running database migrations...")

try:
    # Add tenant_id to sessions
    db.execute(text('ALTER TABLE sessions ADD COLUMN IF NOT EXISTS tenant_id INTEGER REFERENCES tenants(id);'))
    db.execute(text('CREATE INDEX IF NOT EXISTS idx_sessions_tenant_id ON sessions(tenant_id);'))
    print("✅ Added sessions.tenant_id")
    
    # Add columns to tenants
    db.execute(text('ALTER TABLE tenants ADD COLUMN IF NOT EXISTS subscription_expires_at TIMESTAMP;'))
    db.execute(text('ALTER TABLE tenants ADD COLUMN IF NOT EXISTS name VARCHAR(255);'))
    db.execute(text('ALTER TABLE tenants ADD COLUMN IF NOT EXISTS total_team_sessions INTEGER DEFAULT 0;'))
    db.execute(text('ALTER TABLE tenants ADD COLUMN IF NOT EXISTS total_team_hours INTEGER DEFAULT 0;'))
    print("✅ Added tenant columns")
    
    # Add reserved_until to time_slots
    db.execute(text('ALTER TABLE time_slots ADD COLUMN IF NOT EXISTS reserved_until TIMESTAMP;'))
    print("✅ Added time_slots.reserved_until")
    
    db.commit()
    print("\n🎉 Migration complete!")
    
except Exception as e:
    print(f"❌ Migration failed: {e}")
    db.rollback()
finally:
    db.close()
