#!/usr/bin/env python
"""Auto-create admin user on first deployment"""

import os
from app.db import SessionLocal
from app.models.user import User
from passlib.context import CryptContext

pwd_context = CryptContext(schemes=['bcrypt'], deprecated='auto')

def init_admin():
    """Create default admin user if none exists"""
    db = SessionLocal()
    try:
        # Check if any admin users exist
        existing = db.query(User).first()
        if existing:
            print(f"✓ Admin user already exists: {existing.email}")
            return

        # Get credentials from environment variables
        admin_email = os.getenv('ADMIN_EMAIL', 'craig@cmack.dev')
        admin_password = os.getenv('ADMIN_PASSWORD', 'changeme123')  # Default - user must change
        admin_name = os.getenv('ADMIN_NAME', 'Craig Mackenzie')

        # Create admin user
        hashed_password = pwd_context.hash(admin_password)
        admin = User(
            email=admin_email,
            hashed_password=hashed_password,
            full_name=admin_name,
            company_name='Craig Mackenzie Dev',
            role='admin',
            is_active=True
        )

        db.add(admin)
        db.commit()
        print(f"✓ Created admin user: {admin_email}")
        print(f"  Default password: {admin_password}")
        print(f"  IMPORTANT: Change this password immediately after first login!")

    except Exception as e:
        print(f"✗ Error creating admin user: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    init_admin()
