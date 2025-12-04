#!/bin/bash

# Railway startup script for CapCut Sharing Platform
# This script sets up the multi-service application

echo "🚀 Starting CapCut Sharing Platform on Railway..."

# Check if this is the web service (frontend)
if [ "$RAILWAY_SERVICE_NAME" = "frontend" ] || [ "$PORT" = "3000" ]; then
    echo "Starting Frontend service..."
    cd frontend
    npm run build
    npm start
    
# Check if this is the backend service
elif [ "$RAILWAY_SERVICE_NAME" = "backend" ] || [ "$PORT" = "8000" ]; then
    echo "Starting Backend service..."
    cd backend
    python -m uvicorn app.main:app --host 0.0.0.0 --port $PORT
    
# Check if this is the bot service
elif [ "$RAILWAY_SERVICE_NAME" = "bot" ] || [ "$PORT" = "5000" ]; then
    echo "Starting Bot service..."
    cd bot
    python app.py
    
# Default to frontend if no specific service detected
else
    echo "No specific service detected, defaulting to frontend..."
    cd frontend
    npm run build
    npm start
fi