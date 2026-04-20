import os
import json
from google import genai
from sqlalchemy import text
from app.database_init import SessionLocal
from app.embedding_engine import generate_vector
from app.models import UserConversation, SystemLog

# Import router and dispatcher for intelligent routing
import sys
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
from router import get_best_model
from dispatcher import Dispatcher

client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))
dispatcher = Dispatcher()

class VaultService:
    """
    Unified service combining:
    1. Semantic caching (PostgreSQL + pgvector)
    2. Intelligent routing (dispatcher + router)
    3. Session memory (Redis + PostgreSQL)
    """

    # ==================== PHASE 1: SEMANTIC CACHING ====================
    @staticmethod
    def get_embedding(text: str):
        """Generates 768-dim vector locally using HuggingFace."""
        return generate_vector(text)

    @staticmethod
    def semantic_search(user_id: str, vector: list):
        """
        Searches vault for semantically similar previous responses.
        Returns: (response_text, tokens_used, cost) or None
        """
        db = SessionLocal() 
        try:
            threshold = 0.7  # L2 distance threshold (lowered for better cache hits)
            
            match = db.query(UserConversation).filter(
                UserConversation.user_id == user_id,
                UserConversation.embedding != None, 
                UserConversation.embedding.l2_distance(vector) < threshold
            ).order_by(
                UserConversation.embedding.l2_distance(vector)
            ).first()

            if match:
                print(f"🎯 VAULT HIT: Found similar prompt in ID {match.id}")
                VaultService.log_system_event(user_id, "VAULT_CACHE_HIT")
                return (match.response, match.tokens_consumed, match.actual_cost)
                
            return None
        except Exception as e:
            print(f"❌ Search Error: {e}")
            return None
        finally:
            db.close()

    # ==================== PHASE 2: INTELLIGENT ROUTING ====================
    @staticmethod
    def get_best_provider_and_model(prompt: str, user_allowed_tier: int = 1):
        """
        Uses router to intelligently select best provider and model.
        Returns: (model_id, provider, score, category, tier)
        """
        try:
            result = get_best_model(prompt, user_allowed_tier)
            return result
        except Exception as e:
            print(f"⚠️ Router failed: {e}. Falling back to Gemini...")
            return ("gemini-2.5-flash", "Google", 5.0, "UTILITY", 2)

    # ==================== PHASE 3: EXECUTION WITH DISPATCHER ====================
    @staticmethod
    def execute_with_provider(provider: str, model_id: str, prompt: str):
        """
        Routes request through appropriate provider using dispatcher.
        Returns: {text, tokens}
        """
        try:
            print(f"🚀 Executing with {provider} - {model_id}")
            response = dispatcher.execute(provider, model_id, prompt)
            return response
        except Exception as e:
            print(f"❌ Dispatcher error: {e}")
            return {"text": f"Execution Error: {str(e)}", "tokens": 0}

    # ==================== PHASE 4: STORAGE & ARCHIVING ====================
    @staticmethod
    def save_to_vault(user_id: str, prompt: str, response: str, tokens: int, 
                     vector: list, cost: float, model_used: str, provider: str):
        """
        Saves interaction to PostgreSQL vault for future semantic matching.
        Stores both in DB and Redis.
        """
        db = SessionLocal()
        try:
            # 1. Save to PostgreSQL
            new_entry = UserConversation(
                user_id=user_id,
                prompt=prompt,
                response=response,
                model_used=model_used,
                tokens_consumed=tokens,
                actual_cost=cost,
                embedding=vector
            )
            db.add(new_entry)
            db.commit()
            print(f"✅ Vault Updated: Saved ${cost:.4f} interaction from {provider}/{model_used}")
            
            # 2. Cache in Redis - DISABLED (Redis off per user request)
            # if REDIS_AVAILABLE:
            #     VaultService._cache_in_redis(user_id, prompt, response)
            
        except Exception as e:
            print(f"❌ Database Save Error: {e}")
            db.rollback()
        finally:
            db.close()

    @staticmethod
    def _cache_in_redis(user_id: str, prompt: str, response: str):
        """
        Redis caching DISABLED for now.
        Will be enabled later with proper Redis setup.
        """
        # if not REDIS_AVAILABLE or not r:
        #     return
        # 
        # try:
        #     message = json.dumps({
        #         "role": "assistant",
        #         "prompt": prompt[:100],
        #         "response": response[:100]
        #     })
        #     r.rpush(f"chat:{user_id}", message)
        #     r.ltrim(f"chat:{user_id}", -10, -1)
        # except Exception as e:
        #     print(f"⚠️ Redis caching warning: {e}")
        pass

    # ==================== MEMORY MANAGEMENT ====================
    @staticmethod
    def get_session_context(user_id: str):
        """
        Retrieves recent conversation context from PostgreSQL.
        (Redis caching disabled for now)
        """
        # Using PostgreSQL only since Redis is disabled
        db = SessionLocal()
        try:
            recent = db.query(UserConversation).filter(
                UserConversation.user_id == user_id
            ).order_by(UserConversation.created_at.desc()).limit(5).all()
            return [{"prompt": c.prompt, "response": c.response} for c in recent]
        finally:
            db.close()

    @staticmethod
    def check_topic_change(user_id: str, new_prompt: str):
        """
        Topic change detection disabled for now (Redis disabled).
        Will be enabled when Redis is configured.
        """
        # Topic detection requires active Redis session
        # Skipping for now
        return False
        
        # Code below commented for future Redis setup:
        # if not REDIS_AVAILABLE or not r:
        #     return False
        # 
        # try:
        #     context = VaultService.get_session_context(user_id)
        #     if not context:
        #         return False
        #     
        #     check_prompt = f"Previous: {context[-1] if context else 'None'}\nNew: {new_prompt}\nTopic changed significantly? YES/NO"
        #     model = genai.GenerativeModel("gemini-2.5-flash")
        #     response = model.generate_content(check_prompt)
        #     
        #     if "YES" in response.text.upper():
        #         VaultService._archive_session(user_id, context)
        #         r.delete(f"chat:{user_id}")
        #         r.delete(f"summary:{user_id}")
        #         print(f"📦 ARCHIVED: Previous conversation for {user_id}")
        #         return True
        #     return False
        # except Exception as e:
        #     print(f"⚠️ Topic detection warning: {e}")
        #     return False

    @staticmethod
    def _archive_session(user_id: str, context: list):
        """Archives completed conversation to PostgreSQL."""
        from app.models import ConversationArchive
        
        db = SessionLocal()
        try:
            # Generate title for the archived conversation
            if context:
                title_prompt = f"Summarize this conversation in 5 words: {json.dumps(context[:3])}"
                title_res = client.models.generate_content(
                    model="gemini-2.5-flash",
                    contents=title_prompt
                )
                topic = title_res.text.strip().replace('"', '')[:50] or "General"
            else:
                topic = "General Discussion"
            
            archive = ConversationArchive(
                session_id=user_id,
                topic_summary=topic,
                full_transcript=json.dumps(context)
            )
            db.add(archive)
            db.commit()
        except Exception as e:
            print(f"⚠️ Archive warning: {e}")
        finally:
            db.close()

    # ==================== LOGGING & MONITORING ====================
    @staticmethod
    def log_system_event(user_id: str, event_name: str):
        """Records system events for monitoring and debugging."""
        db = SessionLocal()
        try:
            new_log = SystemLog(
                user_id=user_id,
                event=event_name
            )
            db.add(new_log)
            db.commit()
            print(f"📊 System Logged: {event_name} for {user_id}")
        except Exception as e:
            print(f"❌ Logging Error: {e}")
        finally:
            db.close()

    @staticmethod
    def _calculate_cost(provider: str, model_id: str, tokens: int):
        """
        Calculates cost based on provider and token usage.
        Uses database rates if available, otherwise uses defaults.
        """
        db = SessionLocal()
        try:
            from app.models import AIModel
            model = db.query(AIModel).filter(
                AIModel.provider == provider,
                AIModel.model_id == model_id
            ).first()
            
            if model:
                cost_per_1m = model.cost_per_1m_tokens
            else:
                # Fallback rates
                default_rates = {
                    "Google": 0.075,
                    "OpenAI": 0.15,
                    "Anthropic": 0.20,
                    "Cohere": 0.10,
                    "DeepSeek": 0.05,
                    "xAI": 0.10,
                    "Mistral": 0.12,
                    "HuggingFace": 0.00
                }
                cost_per_1m = default_rates.get(provider, 0.10)
            
            return (tokens / 1_000_000) * cost_per_1m
        finally:
            db.close()
