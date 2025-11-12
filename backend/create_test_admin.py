from sqlalchemy.orm import Session
from app.db import SessionLocal, engine, Base
from app.models.user import User
from app.core.security import get_password_hash

# Create tables
Base.metadata.create_all(bind=engine)

def create_test_admin():
    db = SessionLocal()
    try:
        # Check if user exists
        email = "admin@mackenzie.dev"
        existing_user = db.query(User).filter(User.email == email).first()
        if existing_user:
            print(f"Admin user already exists with ID: {existing_user.id}")
            return

        # Create admin user
        hashed_password = get_password_hash("admin123")
        admin = User(
            email=email,
            hashed_password=hashed_password,
            full_name="Admin User",
            company_name="Mackenzie Dev",
            role="admin",
            is_active=True
        )
        db.add(admin)
        db.commit()
        db.refresh(admin)
        print(f"Test admin user created successfully!")
        print(f"Email: {email}")
        print(f"Password: admin123")
        print(f"ID: {admin.id}")
    except Exception as e:
        print(f"Error creating admin user: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    create_test_admin()
