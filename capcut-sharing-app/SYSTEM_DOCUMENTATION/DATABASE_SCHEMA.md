# CapCut Account Sharing System - Database Schema Documentation

## Overview

The system uses PostgreSQL as the primary database with SQLAlchemy ORM for Python applications. The schema supports user management, session booking, password rotation, and usage analytics.

**Database:** `capcut_db`  
**Connection:** `postgresql://user:password@localhost:5432/capcut_db`

---

## Table Relationships

```
Users (1) ──────────── (Many) Sessions
                            │
                            │
                   (Many) Passwords
                            │
Daily_Logs (Analytics)
```

---

## Core Tables

### 1. Users Table

Stores customer information for session bookings.

```sql
CREATE TABLE users (
    id SERIAL PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    email VARCHAR(255) NOT NULL UNIQUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

**Indexes:**
- Primary key: `users_pkey` on `id`
- Unique constraint: `users_email_key` on `email`
- Index: `ix_users_id` on `id`

**Sample Data:**
```sql
INSERT INTO users (name, email) VALUES
('John Doe', 'john@example.com'),
('Jane Smith', 'jane@example.com');
```

### 2. Sessions Table

Central table for booking records and session management.

```sql
CREATE TABLE sessions (
    id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES users(id),
    user_name VARCHAR(255),
    user_email VARCHAR(255),
    start_time TIMESTAMP NOT NULL,
    end_time TIMESTAMP NOT NULL,
    status VARCHAR(50) DEFAULT 'pending',
    current_password_id INTEGER,
    next_user_email VARCHAR(255),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

**Status Values:**
- `pending`: Booked but not yet started
- `active`: Currently in progress (password generated)
- `completed`: Successfully finished
- `no-show`: User did not use the session

**Foreign Keys:**
- `sessions_user_id_fkey`: References `users(id)`

**Sample Data:**
```sql
INSERT INTO sessions (user_id, user_name, user_email, start_time, end_time, status) VALUES
(1, 'John Doe', 'john@example.com', '2024-11-23 14:00:00', '2024-11-23 15:30:00', 'pending'),
(2, 'Jane Smith', 'jane@example.com', '2024-11-23 16:00:00', '2024-11-23 17:30:00', 'active');
```

### 3. Passwords Table

Temporary storage for session passwords with automatic cleanup.

```sql
CREATE TABLE passwords (
    id SERIAL PRIMARY KEY,
    password_hash VARCHAR(255) NOT NULL,
    plain_password VARCHAR(255),
    session_id INTEGER REFERENCES sessions(id),
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    expires_at TIMESTAMP
);
```

**Security Notes:**
- `password_hash`: Bcrypt hashed password for security
- `plain_password`: Temporary storage for email delivery (auto-deleted after 1 hour)
- `expires_at`: Automatic cleanup timestamp

**Sample Data:**
```sql
INSERT INTO passwords (password_hash, plain_password, session_id, expires_at) VALUES
('$2b$12$hash...', 'TempPass123!', 1, '2024-11-23 15:00:00'),
('$2b$12$hash...', NULL, 2, '2024-11-23 18:00:00');
```

### 4. Daily Logs Table

Analytics and usage tracking for system monitoring.

```sql
CREATE TABLE daily_logs (
    id SERIAL PRIMARY KEY,
    date TIMESTAMP,
    total_slots INTEGER,
    booked_slots INTEGER,
    no_shows INTEGER,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

**Usage:**
- Daily aggregation of booking statistics
- No-show tracking for system optimization
- Capacity planning data

---

## Entity Relationships

### SQLAlchemy Model Definitions

```python
from sqlalchemy import Column, Integer, String, DateTime, Boolean, Text, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship

Base = declarative_base()

class User(Base):
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False)
    email = Column(String(255), nullable=False, unique=True)
    created_at = Column(DateTime, default=func.now())
    
    # Relationships
    sessions = relationship("Session", back_populates="user")

class Session(Base):
    __tablename__ = "sessions"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    user_name = Column(String(255))
    user_email = Column(String(255))
    start_time = Column(DateTime, nullable=False)
    end_time = Column(DateTime, nullable=False)
    status = Column(String(50), default="pending")
    current_password_id = Column(Integer)
    next_user_email = Column(String(255))
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())
    
    # Relationships
    user = relationship("User", back_populates="sessions")
    passwords = relationship("Password", back_populates="session")

class Password(Base):
    __tablename__ = "passwords"
    
    id = Column(Integer, primary_key=True, index=True)
    password_hash = Column(String(255), nullable=False)
    plain_password = Column(String(255))
    session_id = Column(Integer, ForeignKey("sessions.id"))
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=func.now())
    expires_at = Column(DateTime)
    
    # Relationships
    session = relationship("Session", back_populates="passwords")
```

---

## Business Logic Queries

### Session Management Queries

#### Get Available Slots
```sql
-- Get all future slots that aren't booked
SELECT 
    CONCAT('slot_', TO_CHAR(slot_time, 'YYYYMMDD_HH24MI')) as id,
    slot_time as start_time,
    slot_time + INTERVAL '90 minutes' as end_time,
    CASE 
        WHEN s.id IS NULL THEN true 
        ELSE false 
    END as available
FROM (
    SELECT generate_series(
        DATE_TRUNC('day', NOW()) + INTERVAL '6 hours',
        DATE_TRUNC('day', NOW()) + INTERVAL '22.5 hours',
        INTERVAL '30 minutes'
    ) as slot_time
) slots
LEFT JOIN sessions s ON s.start_time = slots.slot_time
WHERE slots.slot_time > NOW()
ORDER BY slots.slot_time;
```

#### Get Active Session
```sql
-- Find currently active session
SELECT 
    CONCAT('sess_', s.id) as session_id,
    s.user_email,
    s.start_time,
    s.end_time
FROM sessions s
WHERE s.start_time <= NOW()
    AND s.end_time >= NOW()
    AND s.status = 'active'
LIMIT 1;
```

#### Session Status Updates
```sql
-- Mark sessions as active when they start
UPDATE sessions 
SET status = 'active', updated_at = NOW()
WHERE start_time <= NOW()
    AND status = 'pending';

-- Mark sessions as completed when they end
UPDATE sessions 
SET status = 'completed', updated_at = NOW()
WHERE end_time <= NOW()
    AND status = 'active';
```

### Password Management Queries

#### Create New Password
```sql
-- Create password for new session
INSERT INTO passwords (password_hash, plain_password, session_id, expires_at)
VALUES (
    crypt('new_password', gen_salt('bf')),
    'new_password',
    session_id,
    NOW() + INTERVAL '1 hour'
);
```

#### Cleanup Expired Passwords
```sql
-- Remove expired plaintext passwords (security)
UPDATE passwords 
SET plain_password = NULL
WHERE expires_at < NOW() 
    AND plain_password IS NOT NULL;

-- Remove old password records
DELETE FROM passwords 
WHERE created_at < NOW() - INTERVAL '7 days';
```

### Analytics Queries

#### Daily Usage Stats
```sql
-- Generate daily statistics
INSERT INTO daily_logs (date, total_slots, booked_slots, no_shows)
SELECT 
    DATE_TRUNC('day', NOW()),
    COUNT(*) as total_slots,
    COUNT(CASE WHEN status != 'pending' THEN 1 END) as booked_slots,
    COUNT(CASE WHEN status = 'no-show' THEN 1 END) as no_shows
FROM sessions
WHERE DATE(start_time) = CURRENT_DATE;
```

#### User Booking History
```sql
-- Get user's booking history
SELECT 
    s.start_time,
    s.end_time,
    s.status,
    CASE 
        WHEN s.status = 'active' THEN 'Currently using CapCut'
        WHEN s.status = 'completed' THEN 'Session completed successfully'
        WHEN s.status = 'no-show' THEN 'Did not attend session'
        ELSE 'Upcoming session'
    END as status_description
FROM sessions s
JOIN users u ON s.user_id = u.id
WHERE u.email = 'user@example.com'
ORDER BY s.start_time DESC;
```

---

## Database Maintenance

### Backup Procedures
```bash
# Create full backup
pg_dump -U user capcut_db > backup_$(date +%Y%m%d_%H%M%S).sql

# Create schema-only backup
pg_dump -U user --schema-only capcut_db > schema_backup.sql

# Create data-only backup
pg_dump -U user --data-only capcut_db > data_backup.sql
```

### Restore Procedures
```bash
# Restore full database
psql -U user -d capcut_db < backup_20241123_140000.sql

# Restore schema only
psql -U user -d capcut_db < schema_backup.sql

# Restore data only  
psql -U user -d capcut_db < data_backup.sql
```

### Cleanup Tasks

#### Automated Cleanup (Scheduled)
```sql
-- Weekly cleanup of old sessions (keep 30 days)
DELETE FROM sessions 
WHERE created_at < NOW() - INTERVAL '30 days';

-- Daily cleanup of expired passwords
DELETE FROM passwords 
WHERE expires_at < NOW() - INTERVAL '1 day';

-- Monthly cleanup of old logs (keep 90 days)
DELETE FROM daily_logs 
WHERE created_at < NOW() - INTERVAL '90 days';
```

#### Manual Cleanup Commands
```sql
-- Reset all sessions for testing
UPDATE sessions SET status = 'completed' WHERE status = 'active';

-- Clear all passwords
TRUNCATE passwords;

-- Reset auto-increment sequences
SELECT setval('users_id_seq', COALESCE(MAX(id), 1)) FROM users;
SELECT setval('sessions_id_seq', COALESCE(MAX(id), 1)) FROM sessions;
```

---

## Performance Optimization

### Recommended Indexes
```sql
-- Improve session queries by start_time
CREATE INDEX idx_sessions_start_time ON sessions(start_time);

-- Improve session queries by status
CREATE INDEX idx_sessions_status ON sessions(status);

-- Improve password cleanup queries
CREATE INDEX idx_passwords_expires_at ON passwords(expires_at);

-- Improve user lookup by email
-- (Already exists as unique constraint)

-- Improve analytics queries
CREATE INDEX idx_daily_logs_date ON daily_logs(date);
```

### Query Performance Tips
```sql
-- Use EXPLAIN ANALYZE to check query performance
EXPLAIN ANALYZE 
SELECT * FROM sessions 
WHERE start_time BETWEEN NOW() AND NOW() + INTERVAL '24 hours';

-- Monitor slow queries
SELECT query, mean_time, calls 
FROM pg_stat_statements 
ORDER BY mean_time DESC 
LIMIT 10;
```

### Connection Management
```python
# SQLAlchemy connection pooling
engine = create_engine(
    database_url,
    pool_size=20,          # Number of connections to maintain
    max_overflow=10,       # Additional connections when needed
    pool_pre_ping=True,    # Verify connections before use
    pool_recycle=3600      # Recycle connections every hour
)
```

---

## Security Considerations

### Password Security
- All passwords are hashed using bcrypt with salt
- Plaintext passwords are automatically deleted after 1 hour
- Password history is not stored (each session gets a fresh password)

### Database Access Control
```sql
-- Create application user with limited permissions
CREATE USER capcut_app WITH PASSWORD 'secure_password';

-- Grant necessary permissions only
GRANT CONNECT ON DATABASE capcut_db TO capcut_app;
GRANT USAGE ON SCHEMA public TO capcut_app;
GRANT SELECT, INSERT, UPDATE, DELETE ON users, sessions, passwords, daily_logs TO capcut_app;
GRANT USAGE ON ALL SEQUENCES IN SCHEMA public TO capcut_app;
```

### Data Privacy
- Email addresses are not indexed beyond unique constraint
- No sensitive user data is stored beyond name and email
- Automatic cleanup prevents data accumulation
- Password rotation ensures old credentials can't be reused