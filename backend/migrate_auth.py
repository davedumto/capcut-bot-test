#!/usr/bin/env python3
"""
Migration script to add authentication columns to existing users table
Module 1: Authentication
"""
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.core.config import settings
import psycopg2
from urllib.parse import urlparse

def migrate_database():
    # Parse database URL
    url = urlparse(settings.database_url)
    print(f"🔗 Connecting to database: {url.hostname}:{url.port or 5432}")
    
    # Connect to database
    conn = psycopg2.connect(
        host=url.hostname or 'localhost',
        port=url.port or 5432,
        database=url.path[1:] if url.path else 'capcut_db',  # Remove leading slash
        user=url.username or 'user',
        password=url.password or 'password'
    )
    
    cur = conn.cursor()
    
    try:
        print("🔄 Adding authentication columns to users table...")
        
        # Add new columns to users table
        auth_columns = [
            "ALTER TABLE users ADD COLUMN IF NOT EXISTS user_type VARCHAR(20) DEFAULT 'one_off'",
            "ALTER TABLE users ADD COLUMN IF NOT EXISTS tenant_id INTEGER",
            "ALTER TABLE users ADD COLUMN IF NOT EXISTS team_tenant_id INTEGER", 
            "ALTER TABLE users ADD COLUMN IF NOT EXISTS password_hash VARCHAR(255)",
            "ALTER TABLE users ADD COLUMN IF NOT EXISTS must_change_password BOOLEAN DEFAULT FALSE",
            "ALTER TABLE users ADD COLUMN IF NOT EXISTS total_sessions INTEGER DEFAULT 0",
            "ALTER TABLE users ADD COLUMN IF NOT EXISTS total_hours TEXT DEFAULT '0.0'",
            "ALTER TABLE users ADD COLUMN IF NOT EXISTS marketing_consent BOOLEAN DEFAULT FALSE",
            "ALTER TABLE users ADD COLUMN IF NOT EXISTS last_login_at TIMESTAMP"
        ]
        
        for sql in auth_columns:
            cur.execute(sql)
            print(f"✅ {sql}")
        
        # Create auth_tokens table
        print("\n🔄 Creating auth_tokens table...")
        cur.execute("""
            CREATE TABLE IF NOT EXISTS auth_tokens (
                id SERIAL PRIMARY KEY,
                email VARCHAR(255) NOT NULL,
                token VARCHAR(255) UNIQUE NOT NULL,
                expires_at TIMESTAMP NOT NULL,
                used_at TIMESTAMP,
                created_at TIMESTAMP DEFAULT NOW()
            )
        """)
        print("✅ auth_tokens table created")
        
        # Create indexes
        print("\n🔄 Creating indexes...")
        indexes = [
            "CREATE INDEX IF NOT EXISTS idx_auth_tokens_email ON auth_tokens(email)",
            "CREATE INDEX IF NOT EXISTS idx_auth_tokens_token ON auth_tokens(token)", 
            "CREATE INDEX IF NOT EXISTS idx_users_user_type ON users(user_type)"
        ]
        
        for sql in indexes:
            try:
                cur.execute(sql)
                print(f"✅ {sql}")
            except Exception as e:
                print(f"⚠️ Index creation failed (ignoring): {e}")
        
        conn.commit()
        print("\n🎉 Migration completed successfully!")
        
    except Exception as e:
        conn.rollback()
        print(f"❌ Migration failed: {e}")
        raise
    finally:
        cur.close()
        conn.close()

if __name__ == "__main__":
    migrate_database()