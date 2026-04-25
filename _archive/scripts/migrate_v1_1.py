"""
Migration: Add new columns to user_conversations and create user_memory table.
Run once with: python scripts/migrate_v1_1.py
"""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from sqlalchemy import create_engine, text
from dotenv import load_dotenv

load_dotenv()
engine = create_engine(os.getenv("DATABASE_URL"))

MIGRATIONS = [
    # Feature 2: Multi-Turn Conversation History
    (
        "session_id column on user_conversations",
        "ALTER TABLE user_conversations ADD COLUMN IF NOT EXISTS session_id VARCHAR;"
    ),
    (
        "session_id index",
        "CREATE INDEX IF NOT EXISTS ix_user_conversations_session_id ON user_conversations(session_id);"
    ),
    # Feature 6: Multi-Modal flag
    (
        "has_image column on user_conversations",
        "ALTER TABLE user_conversations ADD COLUMN IF NOT EXISTS has_image BOOLEAN DEFAULT FALSE;"
    ),
    # Feature 12: User Memory table
    (
        "user_memory table",
        """
        CREATE TABLE IF NOT EXISTS user_memory (
            id SERIAL PRIMARY KEY,
            user_id VARCHAR NOT NULL,
            memory_text TEXT NOT NULL,
            source_conversation_id INTEGER,
            importance FLOAT DEFAULT 0.5,
            created_at TIMESTAMP DEFAULT NOW(),
            last_used  TIMESTAMP DEFAULT NOW()
        );
        """
    ),
    (
        "user_memory index on user_id",
        "CREATE INDEX IF NOT EXISTS ix_user_memory_user_id ON user_memory(user_id);"
    ),
]

print("=== Running v1.1 Database Migration ===\n")
with engine.connect() as conn:
    for label, sql in MIGRATIONS:
        try:
            conn.execute(text(sql.strip()))
            conn.commit()
            print(f"  [OK] {label}")
        except Exception as e:
            print(f"  [FAIL] {label}: {e}")
            conn.rollback()

print("\n=== Migration complete ===")
print("New columns: user_conversations.session_id, user_conversations.has_image")
print("New table:   user_memory")
