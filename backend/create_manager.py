#!/usr/bin/env python3
import psycopg2

def create_manager():
    conn = psycopg2.connect(
        host='localhost',
        port=5432,
        database='capcut_db',
        user='user',
        password='password'
    )
    
    cur = conn.cursor()
    
    try:
        # Create a manager user
        manager_email = "manager@example.com"
        manager_name = "John Manager"
        
        cur.execute("""
            INSERT INTO users (email, name, user_type, tenant_id, total_sessions, total_hours, marketing_consent)
            VALUES (%s, %s, 'manager', 1, 5, '12.5', false)
        """, (manager_email, manager_name))
        
        print(f"✅ Created manager: {manager_name} ({manager_email})")
        
        # Create some team members
        team_members = [
            ("alice@team.com", "Alice Smith"),
            ("bob@team.com", "Bob Johnson"),
            ("carol@team.com", "Carol Davis")
        ]
        
        for email, name in team_members:
            cur.execute("""
                INSERT INTO users (email, name, user_type, team_tenant_id, total_sessions, total_hours, marketing_consent)
                VALUES (%s, %s, 'team_member', 1, 2, '3.0', false)
            """, (email, name))
            print(f"✅ Created team member: {name} ({email})")
        
        conn.commit()
        print("\n🎉 Manager and team created successfully!")
        print(f"\nTo test manager dashboard:")
        print(f"1. Go to http://localhost:3000/auth")
        print(f"2. Enter: {manager_email}")
        print(f"3. Use password login (or create magic link)")
        print(f"4. Dashboard will show manager view with team stats!")
        
    except Exception as e:
        conn.rollback()
        print(f"❌ Error: {e}")
    finally:
        cur.close()
        conn.close()

if __name__ == "__main__":
    create_manager()