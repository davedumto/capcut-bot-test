#!/usr/bin/env python3
import psycopg2

def create_constraint():
    conn = psycopg2.connect(
        host='localhost',
        port=5432,
        database='capcut_db',
        user='user',
        password='password'
    )
    
    cur = conn.cursor()
    
    try:
        # Create team limit constraint function
        cur.execute("""
            CREATE OR REPLACE FUNCTION check_team_limit()
            RETURNS TRIGGER AS $$
            BEGIN
                IF (SELECT COUNT(*) FROM team_members WHERE tenant_id = NEW.tenant_id) >= 12 THEN
                    RAISE EXCEPTION 'Team member limit (12) reached';
                END IF;
                RETURN NEW;
            END;
            $$ LANGUAGE plpgsql;
        """)
        
        # Create trigger
        cur.execute("""
            DROP TRIGGER IF EXISTS team_limit_trigger ON team_members;
            CREATE TRIGGER team_limit_trigger
            BEFORE INSERT ON team_members
            FOR EACH ROW EXECUTE FUNCTION check_team_limit();
        """)
        
        # Add unique constraint
        cur.execute("""
            ALTER TABLE team_members 
            ADD CONSTRAINT unique_tenant_email 
            UNIQUE (tenant_id, email);
        """)
        
        conn.commit()
        print("✅ Team limit constraint created")
        
    except Exception as e:
        conn.rollback()
        print(f"❌ Error: {e}")
    finally:
        cur.close()
        conn.close()

if __name__ == "__main__":
    create_constraint()