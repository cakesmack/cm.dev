#!/usr/bin/env python
"""Add short_description column to projects table"""
import sys
import os

# Add the backend directory to the path
sys.path.insert(0, os.path.dirname(__file__))

from sqlalchemy import create_engine, text
from app.core.config import settings

# Create engine
engine = create_engine(settings.DATABASE_URL)

# Add the column
try:
    with engine.connect() as conn:
        conn.execute(text("ALTER TABLE projects ADD COLUMN short_description VARCHAR(200);"))
        conn.commit()
    print("SUCCESS: Added short_description column to projects table!")
except Exception as e:
    if "duplicate column" in str(e).lower():
        print("OK: Column already exists - no changes needed")
    else:
        print(f"ERROR: {e}")
        sys.exit(1)
