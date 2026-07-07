import sys
from app.database import SessionLocal
from app import models


def promote_to_admin(email: str):
    db = SessionLocal()
    try:
        user = db.query(models.User).filter(models.User.email == email).first()
        if not user:
            print(f"No user found with email '{email}'. Register that account first.")
            return
        if user.role == "admin":
            print(f"{email} is already an admin -- nothing to do.")
            return
        user.role = "admin"
        db.commit()
        print(f"Promoted {email} to admin.")
    finally:
        db.close()


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python -m app.promote_admin <email>")
        sys.exit(1)
    promote_to_admin(sys.argv[1])
