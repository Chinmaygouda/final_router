"""
Scoring & ranking module for model selection.
Scores models based on tier, cost, and complexity distance.
"""


def score_models(models):
    """
    Score models based on:
    - Better tier (lower number = better, but weight it less for cost sensitivity)
    - Lower cost
    - Complexity fit (penalty if outside range)
    """
    for m in models:
        # Tier score: Tier 1 = 1.5, Tier 2 = 1.0, Tier 3 = 0.5
        tier_score = (4 - m["tier"]) * 0.5
        
        # Complexity penalty if model is outside the range
        complexity_penalty = 0.1 * m.get("complexity_distance", 0.0)
        
        # Final score: higher is better
        m["score"] = tier_score - 0.3 * m["cost"] - complexity_penalty

    return models


def get_top_k(models, k):
    """Return top K models sorted by score (highest first)."""
    return sorted(models, key=lambda x: x["score"], reverse=True)[:k]
