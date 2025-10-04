#!/bin/bash

# Change to the backend directory
cd backend

# Run database migrations
echo "Running database migrations..."
python -m alembic upgrade head

# Start the application
echo "Starting FastAPI server..."
python -m uvicorn main:app --host 0.0.0.0 --port ${PORT:-8000}
