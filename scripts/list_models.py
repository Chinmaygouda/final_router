import os
from dotenv import load_dotenv
from google import genai

load_dotenv()
client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))

try:
    for m in client.models.list():
        if m.name.startswith("models/gemini"):
            print(m.name)
except Exception as e:
    print(f"Error: {e}")
