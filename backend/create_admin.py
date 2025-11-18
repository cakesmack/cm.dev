#!/usr/bin/env python
"""Create an admin user for the portfolio site"""

import sys
import getpass
from app.db import SessionLocal
from app.models.user import User
from passlib.context import CryptContext

# Password hasher
pwd_context = CryptContext(schemes=['bcrypt'], deprecated='auto')


def create_admin_user(email: str, password: str, full_name: str, company_name: str = None):
    """Create or update admin user"""
    db = SessionLocal()
    try:
        # Check if user exists
        existing_user = db.query(User).filter(User.email == email).first()

        if existing_user:
            print(f"\n⚠️  User {email} already exists!")
            print("Use --update flag to update the password")
            return False

        # Create admin user
        hashed_password = pwd_context.hash(password)
        admin = User(
            email=email,
            hashed_password=hashed_password,
            full_name=full_name,
            company_name=company_name or "Craig Mackenzie Dev",
            role="admin",
            is_active=True
        )
        db.add(admin)
        db.commit()
        db.refresh(admin)

        print(f"\n✅ Admin user created successfully!")
        print(f"   ID: {admin.id}")
        print(f"   Email: {admin.email}")
        print(f"   Name: {admin.full_name}")
        print(f"\nYou can now log in at: /admin")
        return True

    except Exception as e:
        print(f"\n❌ Error creating admin user: {e}")
        db.rollback()
        return False
    finally:
        db.close()


def update_admin_password(email: str, password: str):
    """Update password for existing admin user"""
    db = SessionLocal()
    try:
        user = db.query(User).filter(User.email == email).first()

        if not user:
            print(f"\n❌ User {email} not found!")
            return False

        user.hashed_password = pwd_context.hash(password)
        db.commit()

        print(f"\n✅ Password updated for {email}")
        return True

    except Exception as e:
        print(f"\n❌ Error updating password: {e}")
        db.rollback()
        return False
    finally:
        db.close()


if __name__ == "__main__":
    print("\n=== Admin User Manager ===\n")

    # Parse command line arguments
    update_mode = "--update" in sys.argv
    if update_mode:
        sys.argv.remove("--update")

    # Get email and full name
    if len(sys.argv) < 2:
        email = input("Email (default: craig@cmack.dev): ").strip() or "craig@cmack.dev"
    else:
        email = sys.argv[1]

    if not update_mode:
        if len(sys.argv) < 3:
            full_name = input("Full Name (default: Craig Mackenzie): ").strip() or "Craig Mackenzie"
            company_name = input("Company Name (default: Craig Mackenzie Dev): ").strip() or "Craig Mackenzie Dev"
        else:
            full_name = sys.argv[2]
            company_name = sys.argv[3] if len(sys.argv) > 3 else "Craig Mackenzie Dev"

    # Securely prompt for password
    password = getpass.getpass("Enter admin password: ")
    if not password or len(password) < 8:
        print("❌ Password must be at least 8 characters long!")
        sys.exit(1)

    confirm = getpass.getpass("Confirm password: ")
    if password != confirm:
        print("❌ Passwords don't match!")
        sys.exit(1)

    # Create or update user
    if update_mode:
        success = update_admin_password(email, password)
    else:
        success = create_admin_user(email, password, full_name, company_name)

    sys.exit(0 if success else 1)
