#!/usr/bin/env python3
import psycopg2
import os

def migrate():
    # Get database URL from env or use default
    db_url = os.getenv('DATABASE_URL', 'postgresql://user:password@localhost:5432/capcut_db')
    
    # Parse connection string
    conn = psycopg2.connect(db_url)
    cur = conn.cursor()
    
    try:
        print("🔄 Adding missing columns to database...")
        
        # 1. Add columns to tenants table
        print("  → Adding tenants.name...")
        cur.execute("""
            ALTER TABLE tenants 
            ADD COLUMN IF NOT EXISTS name VARCHAR(255);
        """)
        
        print("  → Adding tenants.is_slotio_account...")
        cur.execute("""
            ALTER TABLE tenants 
            ADD COLUMN IF NOT EXISTS is_slotio_account BOOLEAN DEFAULT FALSE;
        """)
        
        print("  → Adding tenants.total_team_sessions...")
        cur.execute("""
            ALTER TABLE tenants 
            ADD COLUMN IF NOT EXISTS total_team_sessions INTEGER DEFAULT 0;
        """)
        
        print("  → Adding tenants.total_team_hours...")
        cur.execute("""
            ALTER TABLE tenants 
            ADD COLUMN IF NOT EXISTS total_team_hours INTEGER DEFAULT 0;
        """)
        
        print("  → Making tenants.manager_id nullable...")
        cur.execute("""
            ALTER TABLE tenants 
            ALTER COLUMN manager_id DROP NOT NULL;
        """)
        
        # 2. Add columns to bot_jobs table
        print("  → Adding bot_jobs.updated_at...")
        cur.execute("""
            ALTER TABLE bot_jobs 
            ADD COLUMN IF NOT EXISTS updated_at TIMESTAMP DEFAULT NOW();
        """)
        
        # 3. Update existing records
        print("  → Updating existing tenant records...")
        cur.execute("""
            UPDATE tenants 
            SET name = COALESCE(name, 'Unnamed Team')
            WHERE name IS NULL;
        """)
        
        cur.execute("""
            UPDATE bot_jobs 
            SET updated_at = COALESCE(updated_at, created_at)
            WHERE updated_at IS NULL;
        """)
        
        conn.commit()
        print("✅ Migration completed successfully!")
        
    except Exception as e:
        conn.rollback()
        print(f"❌ Migration failed: {e}")
        raise
    finally:
        cur.close()
        conn.close()

if __name__ == "__main__":
    migrate()
