-- Module 7: Performance Indexes
-- Add indexes for frequently queried columns

-- Sessions: Query by status and time ranges
CREATE INDEX IF NOT EXISTS idx_sessions_status ON sessions(status);
CREATE INDEX IF NOT EXISTS idx_sessions_start_time ON sessions(start_time);
CREATE INDEX IF NOT EXISTS idx_sessions_end_time ON sessions(end_time);
CREATE INDEX IF NOT EXISTS idx_sessions_tenant_id ON sessions(tenant_id);

-- Payments: Query by user and status
CREATE INDEX IF NOT EXISTS idx_payments_user_id ON payments(user_id);
CREATE INDEX IF NOT EXISTS idx_payments_status ON payments(status);

-- Bot Jobs: Query by status and tenant
CREATE INDEX IF NOT EXISTS idx_bot_jobs_status ON bot_jobs(status);
CREATE INDEX IF NOT EXISTS idx_bot_jobs_tenant_id ON bot_jobs(tenant_id);

-- Time Slots: Query by availability and date
CREATE INDEX IF NOT EXISTS idx_time_slots_available ON time_slots(available);
CREATE INDEX IF NOT EXISTS idx_time_slots_date ON time_slots(date);

-- Users: Query by type
CREATE INDEX IF NOT EXISTS idx_users_user_type ON users(user_type);
