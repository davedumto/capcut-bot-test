#!/usr/bin/env python3
"""
Database schema fix - Add missing slot_id column to sessions table
This script fixes the schema mismatch causing the VPS deployment issues
"""

import os
import sys
from sqlalchemy import create_engine, text
from sqlalchemy.exc import ProgrammingError

def fix_database_schema():
    """Add the missing slot_id column to sessions table"""
    
    # Database connection string - use environment variable
    database_url = os.getenv('DATABASE_URL', 'postgresql://capcut_user:SecureCapCut2024!@localhost:5432/capcut_db')
    
    print(f"🔗 Connecting to database...")
    
    try:
        engine = create_engine(database_url)
        
        with engine.begin() as conn:
            # Check if slot_id column already exists
            print("🔍 Checking if slot_id column exists...")
            
            result = conn.execute(text("""
                SELECT column_name 
                FROM information_schema.columns 
                WHERE table_name = 'sessions' 
                AND column_name = 'slot_id'
            """))
            
            if result.fetchone():
                print("✅ slot_id column already exists - no migration needed")
                return True
            
            print("➕ Adding slot_id column to sessions table...")
            
            # Add the slot_id column
            conn.execute(text("""
                ALTER TABLE sessions 
                ADD COLUMN slot_id VARCHAR(20)
            """))
            
            print("🔗 Adding foreign key constraint...")
            
            # Add foreign key constraint (if time_slots table exists)
            try:
                conn.execute(text("""
                    ALTER TABLE sessions 
                    ADD CONSTRAINT fk_sessions_slot_id 
                    FOREIGN KEY (slot_id) REFERENCES time_slots(id)
                """))
                print("✅ Foreign key constraint added successfully")
            except ProgrammingError as e:
                if "does not exist" in str(e):
                    print("⚠️  time_slots table doesn't exist yet - skipping foreign key constraint")
                    print("   (This is normal if time_slots are created dynamically)")
                else:
                    raise
            
            print("✅ Database schema updated successfully!")
            
        # Verify the column was added (separate connection for verification)
        with engine.connect() as conn:
            result = conn.execute(text("""
                SELECT column_name, data_type, is_nullable
                FROM information_schema.columns 
                WHERE table_name = 'sessions' 
                AND column_name = 'slot_id'
            """))
            
            column_info = result.fetchone()
            if column_info:
                print(f"✅ Verification: slot_id column added - {column_info[1]}, nullable: {column_info[2]}")
                return True
            else:
                print("❌ Verification failed - column not found after addition")
                return False
                
    except Exception as e:
        print(f"❌ Database migration failed: {e}")
        return False

if __name__ == "__main__":
    print("🔧 CapCut Database Schema Fix")
    print("=" * 40)
    
    success = fix_database_schema()
    
    if success:
        print("\n🎉 Migration completed successfully!")
        print("\nNext steps:")
        print("1. Run this script on your VPS")
        print("2. Restart your services: docker-compose -f docker-compose.backend.yml restart")
        print("3. Test the API: curl http://localhost:8000/api/slots")
        sys.exit(0)
    else:
        print("\n❌ Migration failed!")
        sys.exit(1)