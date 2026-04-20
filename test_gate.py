import requests
import json
import time

# The address where your FastAPI is running
URL = "http://127.0.0.1:8000/ask"
USER_ID = "test_user_001"

def send_chat(message):
    """Send a chat message to the unified gateway."""
    payload = {
        "user_id": USER_ID,
        "prompt": message,
        "user_tier": 1  # Premium tier
    }
    try:
        response = requests.post(URL, json=payload)
        res_data = response.json()
        print(f"\n{'='*60}")
        print(f"📝 USER: {message}")
        print(f"---")
        print(f"🤖 AI RESPONSE: {res_data.get('data', {}).get('ai_response', 'No response')[:200]}...")
        print(f"📊 SOURCE: {res_data.get('source')}")
        print(f"💰 METRICS: {res_data.get('data', {}).get('metrics')}")
        print(f"{'='*60}")
        return res_data
    except Exception as e:
        print(f"❌ Error: {e}")
        return None

# --- THE TEST SEQUENCE ---
print("🚀 UNIFIED SYSTEM TEST: Caching First + Intelligent Routing")
print("=" * 60)

print("\n[TEST 1] 📚 Initial Query (Should cache result)")
send_chat("What are the benefits of machine learning?")

print("\n[TEST 2] ⏱️ Waiting 2 seconds...")
time.sleep(2)

print("\n[TEST 3] 💾 Semantic Cache Hit (Similar question)")
send_chat("What are the advantages of machine learning?")

print("\n[TEST 4] 🔀 Topic Change (Different question)")
send_chat("How do I cook pasta?")

print("\n[TEST 5] 🧠 Complex Query (Should route to higher tier)")
send_chat("Implement a recursive algorithm to solve the N-Queens problem with backtracking")

print("\n✅ TEST COMPLETE")