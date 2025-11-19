#!/bin/bash

# Render startup script for FastAPI app

# Run database migrations/initialization
python -c "from app.db import init_db; init_db()" || echo "Database already initialized"

# Create default admin user if needed
python init_admin.py

# Start the FastAPI app with Uvicorn
uvicorn app.main:app --host 0.0.0.0 --port ${PORT:-8000}
