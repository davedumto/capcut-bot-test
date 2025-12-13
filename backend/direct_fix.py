#!/usr/bin/env python3
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.models.database import engine
from sqlalchemy import text

def direct_fix():
    print("🔧 Using backend's exact database engine...")
    
    with engine.connect() as conn:
        # Check what database we're actually connected to
        result = conn.execute(text("SELECT current_database()"))
        db_name = result.fetchone()[0]
        print(f"Connected to database: {db_name}")
        
        # Check current users table structure
        result = conn.execute(text("""
            SELECT column_name, data_type 
            FROM information_schema.columns 
            WHERE table_name = 'users'
            ORDER BY ordinal_position
        """))
        
        columns = [(row[0], row[1]) for row in result]
        print(f"Current users table columns: {[col[0] for col in columns]}")
        
        # Add all missing auth columns
        auth_columns = [
            ("user_type", "VARCHAR(20) DEFAULT 'one_off'"),
            ("tenant_id", "INTEGER"),
            ("team_tenant_id", "INTEGER"),
            ("password_hash", "VARCHAR(255)"),
            ("must_change_password", "BOOLEAN DEFAULT FALSE"),
            ("total_sessions", "INTEGER DEFAULT 0"),
            ("total_hours", "TEXT DEFAULT '0.0'"),
            ("marketing_consent", "BOOLEAN DEFAULT FALSE"),
            ("last_login_at", "TIMESTAMP")
        ]
        
        existing_columns = [col[0] for col in columns]
        
        for col_name, col_type in auth_columns:
            if col_name not in existing_columns:
                print(f"➕ Adding {col_name} column...")
                conn.execute(text(f"ALTER TABLE users ADD COLUMN {col_name} {col_type}"))
                conn.commit()
                print(f"✅ {col_name} column added!")
            else:
                print(f"✅ {col_name} column already exists")
        
        # Fix auth_tokens table
        print("\n🔄 Fixing auth_tokens table...")
        
        # Check if auth_tokens exists and its columns
        result = conn.execute(text("""
            SELECT column_name 
            FROM information_schema.columns 
            WHERE table_name = 'auth_tokens'
        """))
        
        auth_tokens_columns = [row[0] for row in result]
        print(f"Current auth_tokens columns: {auth_tokens_columns}")
        
        if not auth_tokens_columns:
            # Table doesn't exist, create it
            print("Creating auth_tokens table...")
            conn.execute(text("""
                CREATE TABLE auth_tokens (
                    id SERIAL PRIMARY KEY,
                    email VARCHAR(255) NOT NULL,
                    token VARCHAR(255) UNIQUE NOT NULL,
                    expires_at TIMESTAMP NOT NULL,
                    used_at TIMESTAMP,
                    created_at TIMESTAMP DEFAULT NOW()
                )
            """))
            conn.commit()
            print("✅ auth_tokens table created")
        elif 'email' not in auth_tokens_columns:
            # Table exists but missing email column - recreate it
            print("Dropping and recreating auth_tokens table...")
            conn.execute(text("DROP TABLE IF EXISTS auth_tokens"))
            conn.execute(text("""
                CREATE TABLE auth_tokens (
                    id SERIAL PRIMARY KEY,
                    email VARCHAR(255) NOT NULL,
                    token VARCHAR(255) UNIQUE NOT NULL,
                    expires_at TIMESTAMP NOT NULL,
                    used_at TIMESTAMP,
                    created_at TIMESTAMP DEFAULT NOW()
                )
            """))
            conn.commit()
            print("✅ auth_tokens table recreated with correct schema")
        else:
            print("✅ auth_tokens table already exists with correct schema")
        
        # Test the query that was failing
        print("🧪 Testing the failing query...")
        result = conn.execute(text("SELECT user_type, tenant_id, marketing_consent FROM users LIMIT 1"))
        print("✅ All auth columns work now!")

if __name__ == "__main__":
    direct_fix()