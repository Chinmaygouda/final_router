import sys
import os

if sys.platform == "win32":
    sys.stdout.reconfigure(encoding='utf-8')
    sys.stderr.reconfigure(encoding='utf-8')

sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from app.routing.router import get_best_model
from app.routing.deberta_classifier import get_semantic_classifier

def test_routing():
    print("=== Testing Routing Logic ===")
    
    test_prompts = [
        ("Write a Python script to sort an array.", 2), # Code, Tier 2
        ("How are you feeling today?", 3),             # Chat, Tier 3
        ("Analyze this dataset and give me the standard deviation.", 1) # Analysis, Tier 1
    ]
    
    for prompt, tier in test_prompts:
        print(f"\n--- Test Case ---")
        print(f"Prompt: {prompt}")
        print(f"User Tier: {tier}")
        
        # Test DeBERTa Classification
        print("\n1. DeBERTa Classification:")
        classifier = get_semantic_classifier()
        category, confidence, complexity_label = classifier.classify_with_complexity(prompt)
        print(f"   Category: {category}")
        print(f"   Confidence: {confidence}")
        print(f"   Label: {complexity_label}")
        
        # Test Full Routing
        print("\n2. Router Selection (Best Model + Fallbacks):")
        try:
            model_id, provider, final_score, final_category, final_tier, fallbacks = get_best_model(prompt, tier)
            print(f"   Primary Model: {provider} / {model_id}")
            print(f"   Final Category: {final_category}")
            print(f"   Number of Fallbacks: {len(fallbacks)}")
            print("   Top 3 Fallbacks:")
            for i, f in enumerate(fallbacks[:3]):
                print(f"      {i+1}. {f['provider']} / {f['model_id']}")
        except Exception as e:
            print(f"   Routing Error: {e}")

if __name__ == "__main__":
    test_routing()
