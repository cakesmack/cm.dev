"""Reset admin password script"""
import sys
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
from app.core.security import get_password_hash

# Connect to database
engine = create_engine("sqlite:///./mackenzie_dev.db")
Session = sessionmaker(bind=engine)
session = Session()

try:
    # Direct SQL update to avoid model loading issues
    new_password = "admin123"
    hashed_password = get_password_hash(new_password)

    # Update the first user (admin)
    result = session.execute(
        text("UPDATE users SET hashed_password = :password WHERE email = 'admin@mackenzie-dev.com'"),
        {"password": hashed_password}
    )

    session.commit()

    if result.rowcount > 0:
        print(f"[SUCCESS] Admin password reset successfully!")
        print(f"  Email: admin@mackenzie-dev.com")
        print(f"  Password: {new_password}")
    else:
        print("[ERROR] No user found with email admin@mackenzie-dev.com")

        # Try to find any users
        users = session.execute(text("SELECT id, email FROM users")).fetchall()
        if users:
            print("\nFound users:")
            for user in users:
                print(f"  - {user[1]} (ID: {user[0]})")
        else:
            print("\nNo users found in database")

except Exception as e:
    print(f"Error: {e}")
    session.rollback()
    sys.exit(1)
finally:
    session.close()
