"""
Bandit/Exploration fallback module.
When confidence is low, explore alternative models.
"""


def call_bandit(candidates):
    """
    Fallback when confidence is low.
    
    This is a placeholder - in production, this could:
    - Implement multi-armed bandit algorithm
    - Perform A/B testing
    - Explore less-used models
    - Route to a human decision maker
    
    For now: explore second-best model if available.
    """
    if not candidates:
        return None

    # Temporary: if only 1 model, return it
    if len(candidates) == 1:
        return candidates[0]["name"]
    
    # Explore second-best model (exploration over exploitation)
    print(f"[LOW] Bandit triggered - exploring {candidates[1]['name']} instead of {candidates[0]['name']}")
    return candidates[1]["name"]
