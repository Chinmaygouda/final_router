#FROZEN CODE - DO NOT MODIFY

import redis
import json
import os
import google.generativeai as genai
from database import SessionLocal, r, REDIS_AVAILABLE
from app.models import ConversationArchive

# Setup Gemini Client
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))

class MemoryManager:
    @staticmethod
    def get_context(session_id: str):
        if not REDIS_AVAILABLE or not r: 
            return [] # Safety check
        messages = r.lrange(f"chat:{session_id}", 0, -1)
        return [json.loads(m) for m in messages]

    @staticmethod
    def check_topic_change(session_id: str, new_prompt: str):
        context = MemoryManager.get_context(session_id)
        if not context: 
            return False
        
        # 1. Detection Phase (Gemini Flash)
        check_prompt = f"Existing Topic: {context[-1]['text']}\nNew Message: {new_prompt}\nHas the topic changed significantly? Return ONLY 'YES' or 'NO'."
        response = client.models.generate_content(model="gemini-2.5-flash", contents=check_prompt)
        
        if "YES" in response.text.upper():
            # 2. Dynamic Titling Phase (Summarize the old context before wiping)
            # We only look at the last few messages to get the core subject
            title_prompt = f"Summarize the subject of this conversation in 5 words or less: {json.dumps(context[-3:])}"
            title_res = client.models.generate_content(model="gemini-2.5-flash", contents=title_prompt)
            dynamic_topic = title_res.text.strip().replace('"', '') or "General Discussion"

            # 3. Archiving Phase (Using correct history_json column)
            db = SessionLocal()
            archive = ConversationArchive(
                session_id=session_id,
                topic_summary=dynamic_topic,         
                full_transcript=json.dumps(context) 
            )
            db.add(archive)
            db.commit()
            db.close()
            
            # 4. Wipe Redis
            if REDIS_AVAILABLE and r:
                r.delete(f"chat:{session_id}")
                r.delete(f"summary:{session_id}")
                r.delete(f"count:{session_id}")
            
            print(f"📦 ARCHIVED: Previous conversation saved as '{dynamic_topic}'")
            return True
            
        return False

    @staticmethod
    def manage_summary(session_id: str, context: list):
        # Blueprint: Turn Count % 5 == 0?
        if not REDIS_AVAILABLE or not r:
            return ""
            
        count = r.incr(f"count:{session_id}")
        if count % 5 == 0:
            sum_prompt = f"Summarize this conversation concisely: {json.dumps(context)}"
            summary = client.models.generate_content(model="gemini-2.5-flash", contents=sum_prompt)
            r.set(f"summary:{session_id}", summary.text)
            return summary.text
        return r.get(f"summary:{session_id}") or ""

    @staticmethod
    def save_message(session_id: str, role: str, text: str):
        if not REDIS_AVAILABLE or not r: 
            return # Safety check
        message = json.dumps({"role": role, "text": text})
        r.rpush(f"chat:{session_id}", message)
        # Blueprint: LTRIM: Keep only last 10
        r.ltrim(f"chat:{session_id}", -10, -1)