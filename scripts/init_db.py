#!/usr/bin/env python3
from app.models import create_tables, engine
from sqlalchemy import text

def init_database():
    print("Creating database tables...")
    create_tables()
    print("✓ Database initialized successfully")
    
    with engine.connect() as conn:
        result = conn.execute(text("SELECT 1"))
        print("✓ Database connection verified")

if __name__ == "__main__":
    init_database()
