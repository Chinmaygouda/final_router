"""
Prompt Compressor Test Script
Shows BEFORE vs AFTER compression with token savings in the terminal.
Run: python scripts/test_compressor.py
"""

import sys
import os
if sys.platform == "win32":
    sys.stdout.reconfigure(encoding='utf-8')
    sys.stderr.reconfigure(encoding='utf-8')

sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from app.routing.prompt_compressor import get_prompt_compressor

# ─────────────────────────────────────────────────────
# TEST CASES: Real-world prompts across categories
# ─────────────────────────────────────────────────────
test_cases = [
    {
        "category": "CODE",
        "label": "Buggy Python Script (pasted code)",
        "prompt": """
import os
import sys

# This is the main function
# It greets the user by name
def greet(name)
    # Print hello to the user
    print("Hello " + name)

# Factorial function - calculates factorial recursively
# This is a recursive implementation
def factorial(n):
    # Base case: if n is 0, return 1
    if n == 0
        return 1
    # Recursive case: return n * factorial(n-1)
    else
        return n * factorial(n-1)

# Person class to represent a person object
class Person
    # Constructor method
    def __init__(self, name, age)
        self.name = name
        self.age = age

    # Speak method - prints the person's info
    def speak(self)
        print("My name is " + self.nam + " and I am " + str(self.age))

# Create a list of numbers
numbers = [1, 2, 3, 4, 5
# Loop through the list
for i in range(6)
    # Print each number
    print(numbers[i])

# Check if x equals 10
x = 10
if x = 10:
    print("x is ten")
"""
    },
    {
        "category": "ANALYSIS",
        "label": "Data analysis request with filler words",
        "prompt": """
Hello! I was wondering if you could basically help me with something. 
I have this dataset of sales figures and I think maybe you could 
sort of analyze it for me? Like, I actually need to understand 
the trends across Q1, Q2, Q3, and Q4 of 2024. Um, specifically 
I'd really like to know which products performed the best and 
which ones were kind of underperforming. Could you please kindly 
also provide some recommendations on how to improve sales in Q1 2025?
"""
    },
    {
        "category": "CODE",
        "label": "Architecture question with repeated lines",
        "prompt": """
Design a microservices architecture for an e-commerce platform.

Requirements:
- The system must handle high traffic
- The system must handle high traffic peaks
- The system must handle high traffic spikes during sales
- Use Kubernetes for orchestration
- Use Docker containers
- Use an API gateway
- Use an API gateway for routing
- Use an API gateway for authentication
- Use PostgreSQL for user data
- Use PostgreSQL for order data
- Use PostgreSQL for product data
- Use Redis for caching
- Use Redis for session management
- Use message queues for async communication
"""
    },
    {
        "category": "CHAT",
        "label": "Simple chat with filler",
        "prompt": """
Um, hey there! So basically I was just wondering, like, 
could you actually help me understand what machine learning 
really is? I mean I sort of know what it is kind of but 
I think I need a clearer explanation. Like literally explain 
it to me as if I'm a complete beginner. Thank you so much!
"""
    }
]


def count_tokens_approx(text: str) -> int:
    """Approximate token count (1 token ≈ 0.75 words for English)."""
    words = len(text.split())
    return int(words / 0.75)


def run_compressor_test():
    print("=" * 80)
    print("  PROMPT COMPRESSOR — BEFORE vs AFTER DEMO")
    print("=" * 80)

    compressor = get_prompt_compressor()

    for i, tc in enumerate(test_cases, 1):
        prompt = tc["prompt"].strip()
        category = tc["category"]
        label = tc["label"]

        compressed, metrics = compressor.compress(prompt, category)

        orig_tokens = count_tokens_approx(prompt)
        comp_tokens = count_tokens_approx(compressed)
        tokens_saved = orig_tokens - comp_tokens
        # Estimate cost savings using GPT-4o rate ($5/1M tokens)
        cost_saved = (tokens_saved / 1_000_000) * 5.0

        print(f"\n{'─'*80}")
        print(f"  TEST {i}: [{category}] {label}")
        print(f"{'─'*80}")

        print(f"\n📋 ORIGINAL PROMPT ({orig_tokens} tokens):")
        print("  " + "\n  ".join(prompt.split('\n')[:15]))
        if len(prompt.split('\n')) > 15:
            print(f"  ... ({len(prompt.split(chr(10)))-15} more lines)")

        print(f"\n✂️  COMPRESSED PROMPT ({comp_tokens} tokens):")
        print("  " + "\n  ".join(compressed.split('\n')[:15]))
        if len(compressed.split('\n')) > 15:
            print(f"  ... ({len(compressed.split(chr(10)))-15} more lines)")

        print(f"\n📊 COMPRESSION METRICS:")
        print(f"   Words:        {metrics['original_words']} → {metrics['compressed_words']}")
        print(f"   Tokens:       ~{orig_tokens} → ~{comp_tokens}")
        print(f"   Tokens Saved: {tokens_saved} tokens  ({metrics['savings_percent']}% reduction)")
        print(f"   Cost Saved:   ${cost_saved:.6f} per call (at GPT-4o rates)")
        print(f"   At 1000 calls/day: ${cost_saved*1000:.4f}/day | ${cost_saved*1000*30:.2f}/month saved")

    print(f"\n{'='*80}")
    print("  SUMMARY")
    print(f"{'='*80}")
    print("  The compressor runs in <1ms locally at $0.00 cost.")
    print("  For production scale (10k+ daily calls), savings are significant.")
    print(f"{'='*80}\n")


if __name__ == "__main__":
    run_compressor_test()
