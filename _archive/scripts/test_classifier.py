"""
Direct DeBERTa Classifier Test Script
Tests the routing model DIRECTLY (no API server needed).
Run: python scripts/test_classifier.py
"""

import os
import sys

# Fix Windows console encoding for emoji
if sys.platform == "win32":
    sys.stdout.reconfigure(encoding='utf-8')
    sys.stderr.reconfigure(encoding='utf-8')

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from app.routing.deberta_classifier import get_semantic_classifier

# ===================== TEST PROMPTS =====================
# Organized from EASY → MEDIUM → HARD across all categories

test_prompts = [
    # -------- EASY PROMPTS --------
    {"prompt": "Hello, how are you today?",                          "expected_category": "CHAT",       "expected_difficulty": "EASY"},
    {"prompt": "What is 25 + 37?",                                   "expected_category": "UTILITY",    "expected_difficulty": "EASY"},
    {"prompt": "Convert 5 miles to kilometers",                      "expected_category": "UTILITY",    "expected_difficulty": "EASY"},
    {"prompt": "Write a hello world program in Python",              "expected_category": "CODE",       "expected_difficulty": "EASY"},
    {"prompt": "Tell me a joke about cats",                          "expected_category": "CREATIVE",   "expected_difficulty": "EASY"},

    # -------- MEDIUM PROMPTS --------
    {"prompt": "Explain how binary search works step by step",       "expected_category": "CODE",       "expected_difficulty": "MEDIUM"},
    {"prompt": "Analyze the sentiment of this product review: 'The battery life is terrible but the camera is amazing'",
                                                                     "expected_category": "ANALYSIS",   "expected_difficulty": "MEDIUM"},
    {"prompt": "Write a Python function to find all prime numbers up to N using the Sieve of Eratosthenes",
                                                                     "expected_category": "CODE",       "expected_difficulty": "MEDIUM"},
    {"prompt": "Extract all email addresses and phone numbers from this text and return them as JSON",
                                                                     "expected_category": "EXTRACTION", "expected_difficulty": "MEDIUM"},
    {"prompt": "Write a short poem about the ocean at sunset",       "expected_category": "CREATIVE",   "expected_difficulty": "MEDIUM"},

    # -------- HARD PROMPTS --------
    {"prompt": "Debug this async Python code that has a race condition in the database connection pool causing intermittent deadlocks under high concurrency",
                                                                     "expected_category": "CODE",       "expected_difficulty": "HARD"},
    {"prompt": "Design a distributed microservices architecture for a real-time stock trading platform with Kubernetes orchestration, API gateway, and event-driven messaging",
                                                                     "expected_category": "CODE",       "expected_difficulty": "HARD"},
    {"prompt": "Build an AI agent that can first search the web for recent papers on transformer optimization, then summarize the top 5 findings, and finally generate a comparison table",
                                                                     "expected_category": "AGENTS",     "expected_difficulty": "HARD"},
    {"prompt": "Fix this error in my regex-based parser that fails on nested JSON with escaped unicode characters inside arrays of objects",
                                                                     "expected_category": "CODE",       "expected_difficulty": "HARD"},
    {"prompt": "Analyze the algorithmic complexity of this recursive dynamic programming solution and optimize it from O(2^n) to O(n*m) using memoization and bottom-up tabulation",
                                                                     "expected_category": "CODE",       "expected_difficulty": "HARD"},
]


def run_tests():
    print("=" * 90)
    print("  DeBERTa-v3 CLASSIFIER DIRECT TEST")
    print("=" * 90)

    classifier = get_semantic_classifier()

    if not classifier.classifier:
        print("\n❌ FATAL: DeBERTa model failed to load! SetFit may not be installed.")
        print("   Run: pip install setfit torch")
        return

    print(f"\n✅ Model loaded successfully!\n")
    print(f"{'#':<4} {'EXPECTED':<30} {'GOT':<30} {'MATCH':<8} {'PROMPT (truncated)'}")
    print("-" * 130)

    correct_category = 0
    correct_difficulty = 0
    total = len(test_prompts)

    for i, test in enumerate(test_prompts, 1):
        prompt = test["prompt"]
        exp_cat = test["expected_category"]
        exp_diff = test["expected_difficulty"]

        # Run classification
        category, confidence, complexity_label = classifier.classify_with_complexity(prompt)

        # Check matches
        cat_match = "✅" if category.upper() == exp_cat.upper() else "❌"
        diff_match = "✅" if complexity_label.upper() == exp_diff.upper() else "❌"

        if category.upper() == exp_cat.upper():
            correct_category += 1
        if complexity_label.upper() == exp_diff.upper():
            correct_difficulty += 1

        expected_str = f"{exp_cat}/{exp_diff}"
        got_str = f"{category}/{complexity_label} ({confidence:.2f})"

        print(f"{i:<4} {expected_str:<30} {got_str:<30} {cat_match}{diff_match}     {prompt[:50]}...")

    # Final Report
    print("\n" + "=" * 90)
    print("  RESULTS SUMMARY")
    print("=" * 90)
    print(f"  Category Accuracy:   {correct_category}/{total} ({correct_category/total*100:.1f}%)")
    print(f"  Difficulty Accuracy: {correct_difficulty}/{total} ({correct_difficulty/total*100:.1f}%)")
    print(f"  Overall Match:       {(correct_category + correct_difficulty)}/{total * 2} ({(correct_category + correct_difficulty)/(total * 2)*100:.1f}%)")
    print("=" * 90)

    if correct_category / total >= 0.8:
        print("  🎉 CATEGORY CLASSIFICATION: PASSING (80%+ accuracy)")
    else:
        print("  ⚠️  CATEGORY CLASSIFICATION: NEEDS IMPROVEMENT")

    if correct_difficulty / total >= 0.7:
        print("  🎉 DIFFICULTY ASSESSMENT: PASSING (70%+ accuracy)")
    else:
        print("  ⚠️  DIFFICULTY ASSESSMENT: NEEDS IMPROVEMENT")


if __name__ == "__main__":
    run_tests()
