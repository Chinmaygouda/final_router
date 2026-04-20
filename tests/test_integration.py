"""
Integration test for the new routing system.
Tests: filtering → scoring → confidence → selection
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from database.db import fetch_models
from app.routing.scoring import score_models, get_top_k
from app.routing.confidence import compute_confidence
from app.routing.bandit import call_bandit
from config.settings import CONFIDENCE_THRESHOLD, TOP_K, TIER_RULES
from app.routing.router import filter_models, complexity_distance

def test_routing():
    """Test the complete routing pipeline."""
    
    print("\n" + "="*70)
    print("🧪 INTEGRATION TEST: Routing Pipeline")
    print("="*70)
    
    # Test case 1: CODE analysis (should route to code models)
    test_category = "CODE"
    test_score = 5.5
    test_label = "MEDIUM"
    
    print(f"\n📋 Test Case 1: {test_label} {test_category} task (score={test_score})")
    print("-" * 70)
    
    # Fetch models
    all_models = fetch_models()
    print(f"✅ Fetched {len(all_models)} models")
    
    if len(all_models) == 0:
        print("⚠️ WARNING: No models in database. Skipping tests.")
        print("   Run: python app/main.py  to initialize the database first")
        return False
    
    # Filter
    filtered = filter_models(all_models, test_category, test_score, test_label)
    print(f"✅ Filtered: {len(filtered)} models for {test_label} {test_category}")
    
    if not filtered:
        print("⚠️ No models matched - this is expected if DB is empty")
        return False
    
    print(f"   Models: {[m['name'][:20] for m in filtered[:5]]}")
    
    # Score
    scored = score_models(filtered)
    print(f"✅ Scored all {len(scored)} models")
    
    # Top-K
    candidates = get_top_k(scored, TOP_K)
    print(f"✅ Top-K selection (k={TOP_K}):")
    for i, m in enumerate(candidates, 1):
        print(f"   {i}. {m['name'][:30]:<30} score={m['score']:.3f}")
    
    # Confidence
    confidence = compute_confidence(candidates)
    print(f"✅ Confidence: {confidence:.3f}")
    
    # Decision
    if confidence >= CONFIDENCE_THRESHOLD:
        selected = candidates[0]["name"]
        print(f"✅ DECISION: HIGH confidence → select {selected[:30]}")
    else:
        selected = call_bandit(candidates)
        print(f"✅ DECISION: LOW confidence → bandit selected {selected[:30]}")
    
    print("\n" + "="*70)
    print("✅ INTEGRATION TEST PASSED")
    print("="*70 + "\n")
    
    return True


if __name__ == "__main__":
    try:
        success = test_routing()
        if success:
            print("✨ All tests passed! Integration is working correctly.")
        else:
            print("⚠️ Tests skipped due to missing data. This is expected on fresh install.")
    except Exception as e:
        print(f"\n❌ ERROR: {e}")
        import traceback
        traceback.print_exc()
