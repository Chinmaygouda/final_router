import sys
import os

if sys.platform == "win32":
    sys.stdout.reconfigure(encoding='utf-8')
    sys.stderr.reconfigure(encoding='utf-8')

sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from app.memory_service import MemoryService, extract_memories
from app.database_init import SessionLocal

def test_memory_extraction():
    print("=== Testing Persistent User Memory Extraction ===")
    
    test_user_id = "test_memory_user_999"
    
    test_responses = [
        "User stated: 'My name is Alice and I love playing tennis.'",
        "It seems the user prefers dark mode in their applications.",
        "The user is a frontend developer who hates using Java.",
        "User mentioned: 'I am allergic to peanuts.'"
    ]
    
    db = SessionLocal()
    
    try:
        # Clear existing memory for this user just for the test
        from app.models import UserMemory
        db.query(UserMemory).filter(UserMemory.user_id == test_user_id).delete()
        db.commit()
        
        print("\nExtracting facts from simulated AI responses...")
        for i, response in enumerate(test_responses):
            print(f"\nResponse {i+1}: {response}")
            # The top-level function extracts raw facts
            facts = extract_memories("Tell me about yourself.", response)
            print(f"Extracted facts: {facts}")
            # The service saves them to DB
            MemoryService.save_memories(test_user_id, db, "Tell me about yourself.", response)
            
        print("\n--- Extracted Memories in DB ---")
        memories = MemoryService.get_memories(test_user_id, db)
        
        if not memories:
            print("No memories extracted.")
        else:
            for i, m in enumerate(memories):
                print(f"- Fact {i+1}: {m}")
                
        print("\n--- Built Memory Context ---")
        context = MemoryService.build_memory_context(memories)
        print(context)

    finally:
        db.close()

if __name__ == "__main__":
    test_memory_extraction()
