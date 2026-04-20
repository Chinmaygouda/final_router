import os
from dotenv import load_dotenv
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
from app.models import Base  # Use absolute import for reliability

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")

# 1. Setup the Engine and Session Factory
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def initialize_v2_db():
    """Initializes pgvector and creates all tables including new models."""
    with engine.connect() as conn:
        print("🛠️ Enabling Vector Extension...")
        conn.execute(text("CREATE EXTENSION IF NOT EXISTS vector;"))
        conn.commit()

    print("🏗️ Creating V2 Tables (UserConversation, SystemLog, AIModel, ConversationArchive)...")
    Base.metadata.create_all(bind=engine)
    print("✅ V2 Database is ready with all models!")

if __name__ == "__main__":
    initialize_v2_db()