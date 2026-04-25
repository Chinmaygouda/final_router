import os
import time
from dotenv import load_dotenv
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
from app.models import Base

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")

# 1. Setup the Engine and Session Factory
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def initialize_v2_db():
    """
    Initializes pgvector and creates all tables.
    Retries up to 3 times with backoff in case NeonDB is waking from sleep.
    """
    MAX_RETRIES = 3
    for attempt in range(1, MAX_RETRIES + 1):
        try:
            with engine.connect() as conn:
                print("[DB] Enabling pgvector extension...")
                conn.execute(text("CREATE EXTENSION IF NOT EXISTS vector;"))
                conn.commit()

            print("[DB] Creating V2 Tables (UserConversation, UserMemory, AIModel, ModelPerformance)...")
            Base.metadata.create_all(bind=engine)
            print("[DB] V2 Database ready.")
            return  # Success - exit early

        except Exception as e:
            wait = attempt * 5  # 5s, 10s, 15s
            if attempt < MAX_RETRIES:
                print(f"[DB] Connection attempt {attempt}/{MAX_RETRIES} failed.")
                print(f"[DB] NeonDB may be waking up. Retrying in {wait}s... ({e})")
                time.sleep(wait)
            else:
                print(f"[DB] All {MAX_RETRIES} connection attempts failed.")
                print("[DB] ACTION REQUIRED: Visit https://console.neon.tech to wake your DB, then restart the server.")
                raise  # Re-raise so uvicorn shows the real error

if __name__ == "__main__":
    initialize_v2_db()