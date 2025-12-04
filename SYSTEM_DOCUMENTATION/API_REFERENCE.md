# CapCut Account Sharing System - API Reference

## Backend API Endpoints (Port 8000)

### Base URL
```
http://localhost:8000
```

### Common Response Format
All API responses follow a consistent structure:
```json
{
  "success": true,
  "data": {},
  "message": "Optional status message"
}
```

---

## Slot Management APIs

### GET /api/slots
Get available time slots for booking.

**Response:**
```json
{
  "slots": [
    {
      "id": "slot_20241123_0630",
      "start_time": "2024-11-23T06:30:00",
      "end_time": "2024-11-23T08:00:00", 
      "available": true
    }
  ]
}
```

**Slot Generation Logic:**
- 30-minute intervals from 6:00 AM to 10:30 PM daily
- 1.5-hour session duration
- Last slot starts at 10:30 PM, ends at 12:00 AM
- Slots marked unavailable if already booked

---

## Booking Management APIs

### POST /api/bookings
Create a new session booking.

**Request Body:**
```json
{
  "name": "John Doe",
  "email": "john@example.com", 
  "slot_id": "slot_20241123_0630"
}
```

**Response:**
```json
{
  "success": true,
  "session_id": "sess_123",
  "message": "Booking confirmed for 6:30 AM - 8:00 AM"
}
```

**Error Response:**
```json
{
  "success": false,
  "detail": "Slot no longer available"
}
```

**Business Logic:**
1. Validate slot availability
2. Create or find existing user by email
3. Create session record with status "pending"
4. Return formatted session ID

---

## Session Management APIs

### GET /api/sessions/active
Get current active session (if any).

**Response (Active Session):**
```json
{
  "session_id": "sess_123",
  "user_email": "john@example.com",
  "start_time": "2024-11-23T14:30:00",
  "end_time": "2024-11-23T16:00:00"
}
```

**Response (No Active Session):**
```json
null
```

### GET /api/sessions/{session_id}
Get details for a specific session.

**Path Parameters:**
- `session_id`: Session identifier (format: "sess_123")

**Response:**
```json
{
  "session_id": "sess_123",
  "user_name": "John Doe",
  "user_email": "john@example.com", 
  "start_time": "2024-11-23T14:30:00",
  "end_time": "2024-11-23T16:00:00",
  "status": "pending"
}
```

**Session Statuses:**
- `pending`: Booked but not yet started
- `active`: Currently in progress
- `completed`: Successfully finished
- `no-show`: User did not use session

---

## Health Check APIs

### GET /
Root endpoint with basic service information.

**Response:**
```json
{
  "message": "CapCut Sharing Backend API",
  "version": "1.0.0", 
  "status": "running"
}
```

### GET /health
Health check endpoint for monitoring.

**Response:**
```json
{
  "status": "healthy",
  "timestamp": "2024-11-21"
}
```

### GET /scheduler/status
Get scheduler status and active jobs.

**Response:**
```json
{
  "scheduler_running": true,
  "jobs_count": 3,
  "jobs": [
    {
      "id": "session_start_job",
      "name": "Check for sessions to start",
      "next_run": "2024-11-23 21:23:00",
      "trigger": "interval[0:01:00]"
    }
  ]
}
```

---

## Bot Service API (Port 5001)

### Base URL
```
http://localhost:5001
```

### POST /bot/reset-password
Reset CapCut account password using automated flow.

**Request Body:**
```json
{
  "email": "daevid621@gmail.com",
  "new_password": "SecureP@ss123"
}
```

**Response (Success):**
```json
{
  "success": true,
  "new_password": "SecureP@ss123",
  "message": "Password reset successfully"
}
```

**Response (Failure):**
```json
{
  "success": false,
  "detail": "Error: Could not find forgot password button"
}
```

### GET /health
Bot service health check.

**Response:**
```json
{
  "status": "Bot service is running"
}
```

---

## Frontend API Integration

### API Client (lib/api.ts)
Type-safe API client with error handling:

```typescript
interface TimeSlot {
  id: string
  start_time: string
  end_time: string
  available: boolean
}

interface BookingRequest {
  name: string
  email: string
  slot_id: string
}

interface BookingResponse {
  success: boolean
  session_id: string
  message: string
}

// Usage examples
const slots = await getSlots()
const booking = await createBooking({
  name: "John Doe",
  email: "john@example.com", 
  slot_id: "slot_20241123_0630"
})
const session = await getSessionDetails("sess_123")
```

### Error Handling
```typescript
try {
  const response = await apiClient.request('/api/slots')
} catch (error) {
  if (error.message.includes('fetch')) {
    throw new Error('Unable to connect to booking system')
  }
  throw error
}
```

---

## Database Schema Reference

### Users Table
```sql
CREATE TABLE users (
  id SERIAL PRIMARY KEY,
  name VARCHAR(255) NOT NULL,
  email VARCHAR(255) NOT NULL UNIQUE,
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

### Sessions Table  
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

### Passwords Table
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

### Daily Logs Table
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

---

## Environment Configuration

### Backend (.env)
```bash
DATABASE_URL=postgresql://user:password@localhost:5432/capcut_db
BOT_SERVICE_URL=http://localhost:5001
FRONTEND_URL=http://localhost:3000
SECRET_KEY=d0jHLe60pCHdQMd_JTfTJkWR5XOPsghB1EGtgO78Vsk
GMAIL_USER=daevid621@gmail.com
GMAIL_APP_PASSWORD=vrecwdtlranpytll
ENVIRONMENT=development
```

### Bot Service (.env)
```bash
CAPCUT_EMAIL=daevid621@gmail.com
CAPCUT_PASSWORD=Doomsday2022
GMAIL_EMAIL=daevid621@gmail.com
GMAIL_APP_PASSWORD=vrecwdtlranpytll
ENVIRONMENT=development
HEADLESS=false
DEBUG=true
```

### Frontend (.env.local)
```bash
NEXT_PUBLIC_API_URL=http://localhost:8000
```

---

## Rate Limiting & Constraints

### Session Management
- Maximum 1 active session per time slot
- Sessions cannot overlap for same user
- 24-hour advance booking window
- No same-day cancellations

### Bot Service
- Password reset cooldown: 5 minutes between attempts
- Maximum 3 retry attempts per password reset
- Email fetch timeout: 60 seconds
- Browser automation timeout: 30 seconds per step

### Database Constraints
- Unique email addresses in users table
- Foreign key constraints prevent orphaned records
- Session times must be valid (start < end)
- Password expiration enforced at application level