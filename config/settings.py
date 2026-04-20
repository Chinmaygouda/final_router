"""
Configuration settings for the router system.
"""

# Routing confidence threshold
# If confidence >= CONFIDENCE_THRESHOLD → auto-select best model
# If confidence < CONFIDENCE_THRESHOLD → call bandit for exploration
CONFIDENCE_THRESHOLD = 0.5

# Number of top models to keep as candidates
TOP_K = 2

# Tier rules based on complexity level
# Determines which tiers are allowed for each complexity level
TIER_RULES = {
    "EASY": [2, 3],      # For simple tasks, use cheaper tiers
    "MEDIUM": [1, 2],    # For medium tasks, allow mid-range models
    "HARD": [1]          # For hard tasks, use premium models only
}

# Complexity boundaries
COMPLEXITY_BOUNDARIES = {
    "EASY": (1.0, 4.0),
    "MEDIUM": (4.0, 7.0),
    "HARD": (7.0, 10.0)
}
