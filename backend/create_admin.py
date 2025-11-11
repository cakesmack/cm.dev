from sqlalchemy.orm import Session
from app.db import SessionLocal, engine, Base
from app.models.user import User
from app.core.security import get_password_hash
import sys

# Create tables
Base.metadata.create_all(bind=engine)

def create_admin_user(email: str, password: str, full_name: str, company_name: str):
    db = SessionLocal()
    try:
        # Check if user exists
        existing_user = db.query(User).filter(User.email == email).first()
        if existing_user:
            print(f"User with email {email} already exists!")
            return

        # Create admin user
        hashed_password = get_password_hash(password)
        admin = User(
            email=email,
            hashed_password=hashed_password,
            full_name=full_name,
            company_name=company_name,
            role="admin",
            is_active=True
        )
        db.add(admin)
        db.commit()
        db.refresh(admin)
        print(f"Admin user created successfully! ID: {admin.id}")
    except Exception as e:
        print(f"Error creating admin user: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    if len(sys.argv) < 4:
        print("Usage: python create_admin.py <email> <password> <full_name> [company_name]")
        sys.exit(1)

    email = sys.argv[1]
    password = sys.argv[2]
    full_name = sys.argv[3]
    company_name = sys.argv[4] if len(sys.argv) > 4 else None

    create_admin_user(email, password, full_name, company_name)
