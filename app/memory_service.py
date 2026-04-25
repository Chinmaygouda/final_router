"""
Memory Service — Persistent User Memory (Feature 12)
=====================================================
Automatically extracts key facts from every AI response and stores
them per-user in PostgreSQL. On the next request, the top memories
are prepended to the prompt so the AI "remembers" the user.

Examples of extracted memories:
  - "User is building an ore detection ML pipeline"
  - "User prefers Python for all coding tasks"
  - "User is running on a CPU-based laptop"

100% local. No internet needed. Self-improving with usage.
"""

import re
from datetime import datetime
from typing import List, Optional
from sqlalchemy.orm import Session

from app.models import UserMemory


# ─────────────────────────────────────────────────────────────
# Heuristic memory extraction patterns
# ─────────────────────────────────────────────────────────────
PREFERENCE_SIGNALS = [
    # Preferences: "I prefer X", "user prefers X"
    r"(?:I |user )prefer(?:s)? (.{5,80}?)(?:\.|,|$)",
    # Work context: "I am building / working on / developing"
    r"(?:I am|I'm|user is) (?:a |an )?(.{5,80}?)(?:\.|,|$)",
    # Tool/language: "I use Python for...", "I'm using React"
    r"(?:I use|I'm using|using) (.{3,60}?) (?:for|as|to|and|,|$)",
    # Hardware: "I have a MacBook", "running on a CPU laptop"
    r"(?:I have|I've got|running on) (?:a |an )(.{3,60}?) (?:laptop|server|machine|GPU|CPU|PC|Mac)",
    # Project: "my project is X"
    r"(?:my |our )project is (.{5,80}?)(?:\.|,|$)",
    # Work style: "I work in Python", "I work with TensorFlow"
    r"(?:I work|working) (?:in|with|on) (.{3,60}?)(?:\.|,|$)",
    # Name: "My name is X"
    r"[Mm]y name is ([A-Za-z][a-zA-Z ]{1,30}?)(?:\.|,|!| and|$)",
    # Love/passion: "I love building AI", "I enjoy coding"
    r"(?:I love|I enjoy|I like|I hate|I dislike|I only) (.{5,80}?)(?:\.|,|$)",
    # Language/tool preference: "I only code in Python", "I prefer TypeScript"
    r"(?:only (?:code|write|program|work)) (?:in|with) (.{3,40}?)(?:\.|,|$)",
    # Identity: "I am a backend developer", "I am a data scientist"
    r"[Ii] am (?:a |an )([a-z][a-zA-Z ]{3,60}?)(?:\.|,| who| and|$)",
]


def extract_memories(prompt: str, response: str, max_facts: int = 5) -> List[str]:
    """
    Extract key facts about the user from a prompt+response pair.
    Returns a list of short memory strings.
    """
    memories = []
    combined = f"{prompt} {response}"

    for pattern in PREFERENCE_SIGNALS:
        matches = re.findall(pattern, combined, re.IGNORECASE)
        for match in matches:
            # Flatten tuple matches (if pattern has groups)
            if isinstance(match, tuple):
                text = " ".join(m for m in match if m).strip()
            else:
                text = match.strip()

            # Clean up and validate
            if 5 < len(text) < 100 and text not in memories:
                memories.append(text.capitalize())

            if len(memories) >= max_facts:
                break
        if len(memories) >= max_facts:
            break

    return memories


class MemoryService:
    """
    Manages persistent user memory in PostgreSQL.
    """

    @staticmethod
    def get_memories(user_id: str, db: Session, top_n: int = 5) -> List[str]:
        """
        Fetch the top N most recently used memories for a user.
        Returns list of memory strings to prepend to the prompt.
        """
        try:
            memories = (
                db.query(UserMemory)
                .filter(UserMemory.user_id == user_id)
                .order_by(UserMemory.importance.desc(), UserMemory.last_used.desc())
                .limit(top_n)
                .all()
            )
            return [m.memory_text for m in memories]
        except Exception as e:
            print(f"[MEMORY] Error fetching memories: {e}")
            return []

    @staticmethod
    def save_memories(
        user_id: str,
        db: Session,
        prompt: str,
        response: str,
        conversation_id: Optional[int] = None
    ) -> int:
        """
        Extract and save new memories from a conversation.
        Returns number of new memories saved.
        """
        try:
            new_facts = extract_memories(prompt, response)
            if not new_facts:
                return 0

            # Fetch existing memory texts to avoid duplicates
            existing = db.query(UserMemory.memory_text).filter(
                UserMemory.user_id == user_id
            ).all()
            existing_texts = {e[0].lower() for e in existing}

            saved = 0
            for fact in new_facts:
                if fact.lower() not in existing_texts:
                    db.add(UserMemory(
                        user_id=user_id,
                        memory_text=fact,
                        source_conversation_id=conversation_id,
                        importance=0.6,
                    ))
                    existing_texts.add(fact.lower())
                    saved += 1

            db.commit()
            if saved:
                print(f"[MEMORY] 🧠 Saved {saved} new memories for user '{user_id}'")
            return saved
        except Exception as e:
            print(f"[MEMORY] Error saving memories: {e}")
            db.rollback()
            return 0

    @staticmethod
    def build_memory_context(memories: List[str]) -> str:
        """
        Format memories into a system-level context string to
        prepend to the user's prompt.
        """
        if not memories:
            return ""
        lines = "\n".join(f"- {m}" for m in memories)
        return (
            f"[CONTEXT: Known facts about this user]\n{lines}\n"
            f"[Use the above context to personalize your response.]\n\n"
        )

    @staticmethod
    def delete_memory(user_id: str, memory_id: int, db: Session) -> bool:
        """Allow users to delete a specific memory."""
        try:
            mem = db.query(UserMemory).filter(
                UserMemory.id == memory_id,
                UserMemory.user_id == user_id
            ).first()
            if mem:
                db.delete(mem)
                db.commit()
                return True
            return False
        except Exception:
            db.rollback()
            return False

    @staticmethod
    def clear_memories(user_id: str, db: Session) -> int:
        """Clear all memories for a user."""
        try:
            count = db.query(UserMemory).filter(
                UserMemory.user_id == user_id
            ).delete()
            db.commit()
            return count
        except Exception:
            db.rollback()
            return 0
