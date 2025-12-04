#!/bin/bash

# Render startup script for FastAPI app

# Run database migrations
alembic upgrade head

# Start the FastAPI app with Uvicorn
uvicorn app.main:app --host 0.0.0.0 --port ${PORT:-8000}
