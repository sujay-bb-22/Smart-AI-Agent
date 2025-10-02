#!/bin/bash

# Run database migrations
alembic -c alembic.ini upgrade head

# Start the application
uvicorn app.main:app --host 0.0.0.0 --port 8080
