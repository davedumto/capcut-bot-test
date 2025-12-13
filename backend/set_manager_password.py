#!/usr/bin/env python3
import psycopg2
import bcrypt

def set_manager_password():
    conn = psycopg2.connect(
        host='localhost',
        port=5432,
        database='capcut_db',
        user='user',
        password='password'
    )
    
    cur = conn.cursor()
    
    try:
        # Set a simple password for the manager
        password = "manager123"
        salt = bcrypt.gensalt()
        hashed = bcrypt.hashpw(password.encode('utf-8'), salt)
        
        cur.execute("""
            UPDATE users 
            SET password_hash = %s 
            WHERE email = 'manager@example.com'
        """, (hashed.decode('utf-8'),))
        
        conn.commit()
        print("✅ Manager password set successfully!")
        print("\nLogin credentials:")
        print("Email: manager@example.com")
        print("Password: manager123")
        
    except Exception as e:
        conn.rollback()
        print(f"❌ Error: {e}")
    finally:
        cur.close()
        conn.close()

if __name__ == "__main__":
    set_manager_password()