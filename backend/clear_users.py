#!/usr/bin/env python3
import psycopg2

def clear_users():
    conn = psycopg2.connect(
        host='localhost',
        port=5432,
        database='capcut_db',
        user='user',
        password='password'
    )
    
    cur = conn.cursor()
    
    try:
        # Clear in order due to foreign key constraints
        cur.execute("DELETE FROM auth_tokens")
        print("✅ Cleared auth_tokens table")
        
        cur.execute("DELETE FROM passwords")
        print("✅ Cleared passwords table")
        
        cur.execute("DELETE FROM sessions")
        print("✅ Cleared sessions table")
        
        cur.execute("DELETE FROM users")
        print("✅ Cleared users table")
        
        conn.commit()
        print("🎉 All user data cleared!")
    
    except Exception as e:
        conn.rollback()
        print(f"❌ Error: {e}")
    finally:
        cur.close()
        conn.close()

if __name__ == "__main__":
    clear_users()