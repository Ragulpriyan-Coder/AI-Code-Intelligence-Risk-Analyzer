"""
Script to create a superuser or promote an existing user to admin.
Usage: python create_superuser.py
"""
import sys
import os

# Add the app directory to the path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app.db.session import SessionLocal, engine, Base
from app.db.models import User
from app.auth.utils import hash_password, validate_email, validate_password_strength

def create_superuser():
    """Create a new superuser or promote existing user."""

    # Ensure tables exist
    Base.metadata.create_all(bind=engine)

    db = SessionLocal()

    try:
        print("\n=== Create Superuser ===\n")

        # Get email
        email = input("Email: ").strip().lower()

        # Check if user exists
        existing_user = db.query(User).filter(User.email == email).first()

        if existing_user:
            print(f"\nUser '{existing_user.username}' already exists.")
            promote = input("Promote to admin? (y/n): ").strip().lower()

            if promote == 'y':
                existing_user.is_admin = True
                db.commit()
                print(f"\n✓ User '{existing_user.username}' is now an admin!")
            else:
                print("Cancelled.")
            return

        # Validate email
        is_valid, error = validate_email(email)
        if not is_valid:
            print(f"Error: {error}")
            return

        # Get username
        username = input("Username: ").strip().lower()

        # Check username exists
        if db.query(User).filter(User.username == username).first():
            print("Error: Username already exists")
            return

        # Get password
        password = input("Password: ").strip()

        is_valid, error = validate_password_strength(password)
        if not is_valid:
            print(f"Error: {error}")
            return

        # Create superuser
        superuser = User(
            email=email,
            username=username,
            hashed_password=hash_password(password),
            is_active=True,
            is_admin=True,
        )

        db.add(superuser)
        db.commit()
        db.refresh(superuser)

        print(f"\n✓ Superuser created successfully!")
        print(f"  ID: {superuser.id}")
        print(f"  Email: {superuser.email}")
        print(f"  Username: {superuser.username}")
        print(f"  Admin: Yes")

    except KeyboardInterrupt:
        print("\nCancelled.")
    except Exception as e:
        print(f"Error: {e}")
        db.rollback()
    finally:
        db.close()


if __name__ == "__main__":
    create_superuser()
