-- CapCut Sharing MVP Database Schema
-- From instructions.md

-- Table 1: Users (for tracking)
CREATE TABLE users (
  id SERIAL PRIMARY KEY,
  name VARCHAR(255) NOT NULL,
  email VARCHAR(255) NOT NULL UNIQUE,
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Table 2: Bookings/Sessions
CREATE TABLE sessions (
  id SERIAL PRIMARY KEY,
  user_id INT REFERENCES users(id),
  user_name VARCHAR(255),
  user_email VARCHAR(255),
  start_time TIMESTAMP NOT NULL,
  end_time TIMESTAMP NOT NULL,
  status VARCHAR(50) DEFAULT 'pending', -- pending, active, completed, no-show
  current_password_id INT,
  next_user_email VARCHAR(255),
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Table 3: Passwords
CREATE TABLE passwords (
  id SERIAL PRIMARY KEY,
  password_hash VARCHAR(255) NOT NULL,
  plain_password VARCHAR(255), -- Store temporarily for email, delete after 1 hour
  session_id INT REFERENCES sessions(id),
  is_active BOOLEAN DEFAULT TRUE,
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  expires_at TIMESTAMP
);

-- Table 4: Daily Bookings Log (for analytics)
CREATE TABLE daily_logs (
  id SERIAL PRIMARY KEY,
  date DATE,
  total_slots INT,
  booked_slots INT,
  no_shows INT,
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);