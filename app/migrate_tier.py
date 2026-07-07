# One-time migration: adds the 'tier' column to the users table
# if it doesn't already exist. Safe to run multiple times.
from app.database import engine
from sqlalchemy import text

with engine.connect() as conn:
    conn.execute(text("""
        ALTER TABLE users
        ADD COLUMN IF NOT EXISTS tier VARCHAR DEFAULT 'free'
    """))
    conn.commit()
    print("Migration complete: tier column added (or already existed).")
