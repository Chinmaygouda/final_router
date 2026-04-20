"""
UNIFIED DATABASE MODULE - Root level for backward compatibility
Handles PostgreSQL connections only (Redis disabled for now)
"""

import os
from dotenv import load_dotenv
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker

load_dotenv()

# ================== PostgreSQL Setup ==================
DATABASE_URL = os.getenv("DATABASE_URL")

if not DATABASE_URL:
    raise ValueError("DATABASE_URL not set in .env file")

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def initialize_db():
    """Initialize PostgreSQL with pgvector support and create all tables."""
    from app.models import Base
    with engine.connect() as conn:
        print("🛠️ Enabling Vector Extension...")
        conn.execute(text("CREATE EXTENSION IF NOT EXISTS vector;"))
        conn.commit()

    print("🏗️ Creating all tables...")
    Base.metadata.create_all(bind=engine)
    print("✅ Database ready!")

# ================== Redis Setup (DISABLED FOR NOW) ==================
REDIS_AVAILABLE = False
r = None

# Uncomment below to enable Redis later:
# import redis
# REDIS_HOST = os.getenv("REDIS_HOST", "localhost")
# REDIS_PORT = int(os.getenv("REDIS_PORT", 6379))
# REDIS_DB = int(os.getenv("REDIS_DB", 0))
# try:
#     r = redis.Redis(
#         host=REDIS_HOST, 
#         port=REDIS_PORT, 
#         db=REDIS_DB, 
#         decode_responses=True, 
#         socket_connect_timeout=2
#     )
#     r.ping()
#     REDIS_AVAILABLE = True
#     print("✅ Redis connected successfully")
# except redis.exceptions.ConnectionError as e:
#     print(f"⚠️ Redis connection failed: {e}")
#     r = None
#     REDIS_AVAILABLE = False

print("⏭️  Redis disabled (using PostgreSQL only)")

__all__ = ["SessionLocal", "engine", "r", "REDIS_AVAILABLE", "initialize_db"]
