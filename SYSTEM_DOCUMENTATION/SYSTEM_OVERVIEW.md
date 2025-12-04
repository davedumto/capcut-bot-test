# CapCut Account Sharing System - System Overview

## Executive Summary
The CapCut Account Sharing MVP is a comprehensive three-service platform that enables multiple users to share a single CapCut Pro account through automated session management and password rotation.

## System Architecture
```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│                 │    │                 │    │                 │
│   Frontend      │────│   Backend       │────│   Bot Service   │
│   (Next.js)     │    │   (FastAPI)     │    │   (FastAPI)     │
│   Port: 3000    │    │   Port: 8000    │    │   Port: 5001    │
│                 │    │                 │    │                 │
└─────────────────┘    └─────────────────┘    └─────────────────┘
                              │
                              │
                    ┌─────────────────┐
                    │                 │
                    │   PostgreSQL    │
                    │   Database      │
                    │   Port: 5432    │
                    │                 │
                    └─────────────────┘
```

## Core Services

### 1. Frontend Service (Next.js)
**Port:** 3000  
**Purpose:** User interface for booking CapCut sessions

**Key Components:**
- `app/page.tsx` - Main booking flow with 3-step wizard (form → slots → confirmation)
- `components/BookingForm.tsx` - User details collection form
- `components/SlotSelector.tsx` - Time slot selection with real-time availability
- `components/ConfirmationModal.tsx` - Booking confirmation with session details
- `lib/api.ts` - API client for backend communication

**Features:**
- 3-step booking process (Name/Email → Slot Selection → Confirmation)
- Real-time slot availability checking
- Responsive design with custom color scheme (gold/pale/rough/darknavy)
- No authentication required (public booking system)
- Automatic session detail fetching after booking

### 2. Backend Service (FastAPI)
**Port:** 8000  
**Purpose:** Core business logic, database management, and session scheduling

**Key Components:**
- `app/main.py` - FastAPI application with CORS, scheduler initialization
- `app/models/database.py` - SQLAlchemy models (Users, Sessions, Passwords, DailyLogs)
- `app/api/slots.py` - Time slot generation and availability endpoints
- `app/api/bookings.py` - Session booking and user management
- `app/api/sessions.py` - Session details and status tracking
- `app/scheduler/jobs.py` - Automated session start/end management
- `app/services/password_service.py` - Password generation and cleanup
- `app/services/bot_service.py` - Communication with bot service
- `app/services/email_service.py` - User notification system

**Features:**
- Automatic 30-minute time slot generation (6 AM - 10:30 PM)
- 1.5-hour session duration per booking
- APScheduler for automated session management (starts every minute)
- Password rotation between sessions
- Email notifications to users
- PostgreSQL database with proper relationships
- CORS enabled for frontend communication

### 3. Bot Service (FastAPI)
**Port:** 5001  
**Purpose:** Automated CapCut password management using browser automation

**Key Components:**
- `app.py` - FastAPI application entry point
- `routes/reset_password.py` - Password reset API endpoint
- `services/capcut_bot.py` - 11-step forgot password flow implementation
- `services/gmail_handler.py` - IMAP email processing for reset links
- `services/password_generator.py` - Secure password generation
- `config.py` - Pydantic configuration management

**Features:**
- Playwright-based browser automation for CapCut website
- 11-step forgot password flow with email verification
- Gmail IMAP integration for reset link extraction
- Stealth browsing techniques to avoid detection
- Configurable headless/headed mode for debugging
- Strong password generation with customizable complexity

## Database Schema

### Core Tables
```sql
-- Users: Customer information
users (id, name, email, created_at)

-- Sessions: Booking records with timing
sessions (id, user_id, user_name, user_email, start_time, end_time, 
         status, current_password_id, next_user_email, created_at, updated_at)

-- Passwords: Temporary credentials for sessions  
passwords (id, password_hash, plain_password, session_id, is_active, 
          created_at, expires_at)

-- Daily Logs: Usage analytics
daily_logs (id, date, total_slots, booked_slots, no_shows, created_at)
```

### Key Relationships
- Users → Sessions (one-to-many)
- Sessions → Passwords (one-to-many)
- Password rotation happens automatically between sessions

## Session Management Workflow

1. **User Books Session**
   - Frontend: User fills form → selects time slot → confirms booking
   - Backend: Creates user record → creates session record → returns session ID
   - Frontend: Shows confirmation with session details

2. **Session Starts (Automated)**
   - Scheduler detects session start time
   - Bot service generates new password via forgot password flow
   - Password stored in database and sent to user via email
   - Session status updated to "active"

3. **Session Ends (Automated)**
   - Scheduler detects session end time
   - Bot service rotates password for next user
   - Current session marked as "completed"
   - Next user notified if applicable

## Security Features
- No user authentication required (public system)
- Temporary password storage with automatic cleanup
- Browser automation with stealth techniques
- CORS protection on backend APIs
- Database password hashing for stored credentials

## Configuration Management
- Environment variables via `.env` files
- Pydantic settings validation across all services
- Configurable headless/headed browser mode
- Gmail IMAP credentials for email processing
- Database connection strings and service URLs

## Current Deployment Status
- ✅ All three services running locally
- ✅ Database tables created and relationships established
- ✅ Frontend-Backend-Bot communication working
- ⚠️ Gmail IMAP requires real app password for production
- ⚠️ CapCut automation needs testing with real credentials

## Technology Stack
- **Frontend:** Next.js 15, React 19, TypeScript, Tailwind CSS
- **Backend:** FastAPI, SQLAlchemy, APScheduler, PostgreSQL
- **Bot:** FastAPI, Playwright, IMAP, Pydantic
- **Database:** PostgreSQL 14+
- **Deployment:** Docker ready (Dockerfiles present)