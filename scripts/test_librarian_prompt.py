import os
from dotenv import load_dotenv
from google import genai

load_dotenv()
client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))

ALLOWED_CATEGORIES = ["CODE", "AGENTS", "ANALYSIS", "EXTRACTION", "CREATIVE", "UTILITY", "CHAT"]

LIBRARIAN_PROMPT = f"""
You are an AI Architect. Categorize these models.
If a model is good at multiple things, list them separated by a SEMICOLON (;).
USE ONLY THESE CATEGORIES: {", ".join(ALLOWED_CATEGORIES)}.

Return ONLY comma-separated lines:
model_id, provider, category_list, tier, complexity_min, complexity_max, cost_per_1m
Example: gemini-2.0-pro, Google, CODE; ANALYSIS, HIGH, 8.5, 10.0, 1.25
"""

models_string = "gemini-1.5-flash\ngemini-1.5-pro\ngemini-1.0-pro"

try:
    response = client.models.generate_content(
        model='gemini-1.5-flash', 
        contents=f"{LIBRARIAN_PROMPT}\n\nModels:\n{models_string}"
    )
    print("--- RAW AI RESPONSE ---")
    print(response.text)
    print("-----------------------")
except Exception as e:
    print(f"Error: {e}")
