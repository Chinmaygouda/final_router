from sqlalchemy import Column, Integer, String, Float, DateTime, Text, Boolean, UniqueConstraint
from sqlalchemy.orm import declarative_base
from sqlalchemy.dialects.postgresql import UUID # For unique user IDs
from pgvector.sqlalchemy import Vector # Install: pip install pgvector
import datetime

Base = declarative_base() # <--- Create the Base object here

# ==================== TABLE 1: Semantic Vault (NEW) ====================
class UserConversation(Base):
    __tablename__ = "user_conversations"

    id = Column(Integer, primary_key=True)
    user_id = Column(String, index=True) # Unique ID so User A can't see User B
    prompt = Column(Text)
    response = Column(Text)
    model_used = Column(String)
    tokens_consumed = Column(Integer)
    actual_cost = Column(Float) # Calculated as tokens * rate
    # 768 is the default for Gemini text-embedding-004
    embedding = Column(Vector(768)) 
    created_at = Column(DateTime, default=datetime.datetime.utcnow)

# ==================== TABLE 2: System Logs (NEW) ====================
class SystemLog(Base):
    __tablename__ = "system_logs"

    id = Column(Integer, primary_key=True)
    user_id = Column(String)
    event = Column(String) # e.g., 'VAULT_HIT', 'VAULT_MISS', 'PROVIDER_ROUTE'
    timestamp = Column(DateTime, default=datetime.datetime.utcnow)

# ==================== TABLE 3: AI Models for Routing (OLD - RESTORED) ====================
class AIModel(Base):
    __tablename__ = "models"

    id = Column(Integer, primary_key=True, index=True)
    model_id = Column(String, index=True, nullable=False) 
    provider = Column(String, nullable=False)
    category = Column(String, nullable=False)
    tier = Column(Integer, nullable=False)           # 1 (Premium), 2 (Standard), 3 (Budget)
    sub_tier = Column(String, nullable=True)         # "A" (Top 3) or "B" (Standard)
    complexity_min = Column(Float, nullable=False)
    complexity_max = Column(Float, nullable=False)
    cost_per_1m_tokens = Column(Float, default=0.0)  # Price in USD per 1M tokens
    is_active = Column(Boolean, default=True)
    last_audited = Column(DateTime, default=datetime.datetime.utcnow)

    # Ensures a model isn't added to the EXACT same category twice
    __table_args__ = (
        UniqueConstraint('model_id', 'category', name='uix_model_category'),
    )

# ==================== TABLE 4: Conversation Archive (OLD - RESTORED) ====================
class ConversationArchive(Base):
    __tablename__ = "conversation_archives"

    id = Column(Integer, primary_key=True, index=True)
    session_id = Column(String, index=True)
    topic_summary = Column(String)
    full_transcript = Column(String) # JSON string of the chat history
    archived_at = Column(DateTime, default=datetime.datetime.utcnow)