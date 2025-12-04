# CapCut Sharing MVP

A web application that allows Nigerians to share a single CapCut Pro account through time-slot booking. Users book 1.5-hour slots, receive credentials at session start, and the system automatically logs them out and rotates credentials at session end.

## Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    FRONTEND (port 3000)                    │
│                     Next.js 15 + React 19                  │
│                        UI ONLY                             │
└─────────────────────┬───────────────────────────────────────┘
                      │ HTTP calls
                      ▼
┌─────────────────────────────────────────────────────────────┐
│                   BACKEND (port 8000)                      │
│                  FastAPI + SQLAlchemy                      │
│              Database + Scheduler + Email                  │
└─────────────────────┬───────────────────────────────────────┘
                      │ HTTP calls
                      ▼
┌─────────────────────────────────────────────────────────────┐
│                  BOT SERVICE (port 5000)                   │
│                Flask/FastAPI + Playwright                  │
│              CapCut automation + Gmail IMAP                │
└─────────────────────────────────────────────────────────────┘
```

## Tech Stack

- **Frontend**: Next.js 15 + React 19 + Tailwind CSS + TypeScript
- **Backend**: FastAPI + SQLAlchemy + PostgreSQL
- **Bot**: Python Flask/FastAPI + Playwright
- **Database**: PostgreSQL
- **Email**: SMTP + Gmail IMAP
- **Scheduler**: APScheduler (Python)
- **Container**: Docker Compose

## Project Status

### ✅ Phase 1: Frontend & Database Setup (COMPLETE)
- ✅ Next.js 15 frontend with React 19
- ✅ Database schema (users, sessions, passwords, daily_logs)
- ✅ UI components (BookingForm, SlotSelector, ConfirmationModal)
- ✅ Tailwind CSS styling
- ✅ TypeScript configuration

### ✅ Phase 2: API Endpoints (COMPLETE)
- ✅ FastAPI backend with proper structure
- ✅ POST /api/bookings (with validation)
- ✅ GET /api/slots (1.5-hour slots, 24-hour window)
- ✅ GET /api/sessions/active + GET /api/sessions/{id}
- ✅ Input validation and error handling
- ✅ Database models with SQLAlchemy

### ✅ Phase 3: Frontend Integration (COMPLETE)
- ✅ Frontend calls FastAPI backend
- ✅ Enhanced error handling and user feedback
- ✅ Loading states with spinners
- ✅ Retry mechanisms
- ✅ End-to-end booking flow

### 🔄 Phase 4: Scheduler & Automation (NEXT)
- [ ] APScheduler implementation
- [ ] Session start job
- [ ] Session end job  
- [ ] Email service integration

### 🔄 Phase 5: Bot Service (NEXT)
- [ ] Python bot service
- [ ] CapCut automation
- [ ] Gmail IMAP integration

## Quick Start

### Prerequisites
- Node.js 18+ 
- Python 3.9+
- PostgreSQL 14+
- npm/yarn

### 1. Backend Setup
```bash
cd backend

# Install dependencies
pip install -r requirements.txt

# Set up environment
cp .env.example .env
# Edit .env with your database URL

# Setup database
python setup_database.py

# Start backend server
python run.py
```
Backend will be available at: http://localhost:8000

### 2. Frontend Setup
```bash
cd frontend

# Install dependencies
npm install

# Set up environment
# Ensure .env.local has:
# NEXT_PUBLIC_BACKEND_URL=http://localhost:8000

# Start frontend server
npm run dev
```
Frontend will be available at: http://localhost:3000

### 3. Test Integration
```bash
# From project root
python test_integration.py
```

## API Endpoints

### GET /api/slots
Get available 1.5-hour time slots for next 24 hours
```json
{
  "slots": [
    {
      "id": "slot_1",
      "start_time": "2025-11-21T14:00:00Z", 
      "end_time": "2025-11-21T15:30:00Z",
      "available": true
    }
  ]
}
```

### POST /api/bookings  
Create a new booking
```json
// Request
{
  "name": "John Doe",
  "email": "john@example.com", 
  "slot_id": "slot_1"
}

// Response
{
  "success": true,
  "session_id": "sess_123",
  "message": "Booked successfully"
}
```

### GET /api/sessions/active
Get current active session
```json
{
  "session_id": "sess_123",
  "user_email": "john@example.com",
  "start_time": "2025-11-21T14:00:00Z",
  "end_time": "2025-11-21T15:30:00Z"  
}
```

## Database Schema

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
  user_id INT REFERENCES users(id),
  user_name VARCHAR(255),
  user_email VARCHAR(255),
  start_time TIMESTAMP NOT NULL,
  end_time TIMESTAMP NOT NULL,
  status VARCHAR(50) DEFAULT 'pending',
  current_password_id INT,
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
  session_id INT REFERENCES sessions(id),
  is_active BOOLEAN DEFAULT TRUE,
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  expires_at TIMESTAMP
);
```

### Daily Logs Table
```sql
CREATE TABLE daily_logs (
  id SERIAL PRIMARY KEY,
  date DATE,
  total_slots INT,
  booked_slots INT,
  no_shows INT,
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

## Features Implemented

### ✅ Frontend Features
- Clean, responsive UI with Tailwind CSS
- Multi-step booking flow (form → slots → confirmation)
- Real-time slot availability
- Loading states and error handling
- Retry mechanisms for failed requests
- Mobile-friendly design

### ✅ Backend Features  
- RESTful API with FastAPI
- PostgreSQL database with proper relationships
- Input validation with Pydantic
- Comprehensive error handling
- CORS configuration for frontend
- Database connection pooling

### ✅ Validation Rules
- Email format validation
- Name length and character validation
- Slot ID format validation
- Duplicate booking prevention (same email/name per day)
- Slot availability checking
- Time slot conflict detection

### 🔄 Upcoming Features (Phase 4+)
- Automatic session start/end management
- Email notifications with credentials
- Password rotation and security
- CapCut account automation
- Force logout functionality
- Usage analytics

## Testing

### Manual Testing
1. Start both backend and frontend servers
2. Go to http://localhost:3000
3. Fill in booking form with name and email
4. Select an available time slot
5. Complete booking and verify confirmation

### Automated Testing
```bash
# Test backend API endpoints
cd backend
python test_endpoints.py

# Test integration
python test_integration.py
```

### API Documentation
FastAPI automatically generates API docs:
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

## Development

### Project Structure
```
capcut-sharing-app/
├── frontend/                 # Next.js Frontend
│   ├── app/
│   │   ├── page.tsx         # Main booking page
│   │   └── layout.tsx       # Root layout
│   ├── components/
│   │   ├── BookingForm.tsx  # Name/email form
│   │   ├── SlotSelector.tsx # Time slot selection
│   │   └── ConfirmationModal.tsx # Booking confirmation
│   └── ...
├── backend/                  # FastAPI Backend  
│   ├── app/
│   │   ├── api/             # API routes
│   │   ├── core/            # Configuration
│   │   ├── models/          # Database models
│   │   └── main.py          # FastAPI app
│   └── ...
├── bot/                     # Python Bot Service (TODO)
└── ...
```

### Environment Variables
```bash
# Backend (.env)
DATABASE_URL=postgresql://user:pass@localhost/capcut_db
BOT_SERVICE_URL=http://localhost:5000
GMAIL_USER=your-email@gmail.com
GMAIL_APP_PASSWORD=your-app-password

# Frontend (.env.local) 
NEXT_PUBLIC_BACKEND_URL=http://localhost:8000
```

## Next Steps

1. **Phase 4**: Implement scheduler and session management
2. **Phase 5**: Create Python bot service for CapCut automation  
3. **Phase 6**: Add email service for credential distribution
4. **Phase 7**: Security enhancements and password encryption
5. **Phase 8**: Testing and error handling
6. **Phase 9**: Docker containerization

## Contributing

1. Follow the exact file structure from instructions.md
2. Use the specified tech stack
3. Implement features in the defined phases
4. Test each phase before moving to the next
5. Maintain comprehensive error handling

## Support

- API Documentation: http://localhost:8000/docs
- Backend Health: http://localhost:8000/health
- Frontend: http://localhost:3000