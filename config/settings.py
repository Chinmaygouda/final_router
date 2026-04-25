"""
Configuration settings for the router system.
"""

# Routing confidence threshold
# If confidence >= CONFIDENCE_THRESHOLD → auto-select best model
# If confidence < CONFIDENCE_THRESHOLD → call bandit for exploration
CONFIDENCE_THRESHOLD = 0.001  # Auto-select top model unless scores are literally identical

# Scaling factor for confidence formula: confidence = min(score_diff / SCALE, 1.0)
CONFIDENCE_SCALE_FACTOR = 2.0

# Number of top models to keep as candidates
TOP_K = 5

# Tier rules based on complexity level
# Determines which tiers are allowed for each complexity level
TIER_RULES = {
    "EASY": [2, 3],      # Simple tasks (1.0-5.5): Use Tier 2, 3
    "MEDIUM": [1, 2],    # Medium tasks (5.5-7.5): Use Tier 1B, Tier 2
    "HARD": [1]          # Hard tasks (7.5-10.0): Use Tier 1A, 1B only
}

# Complexity boundaries with tier mapping
COMPLEXITY_BOUNDARIES = {
    "EASY": (1.0, 5.5),
    "MEDIUM": (5.5, 7.5),
    "HARD": (7.5, 10.0)
}

# Sub-tier complexity mapping
TIER_COMPLEXITY_MAP = {
    "TIER_1_A": {"min": 8.0, "max": 9.8, "sub_tier": "A"},
    "TIER_1_B": {"min": 7.5, "max": 9.5, "sub_tier": "B"},
    "TIER_2":   {"min": 5.5, "max": 7.5, "sub_tier": None},
    "TIER_3":   {"min": 1.0, "max": 5.5, "sub_tier": None}
}

# Scoring weights (used in scoring.py)
SCORING_TIER_WEIGHTS = {1: {"A": 2.0, "B": 1.8, None: 1.8}, 2: 1.2, 3: 0.6}
SCORING_COST_WEIGHT       = 0.3   # Penalty per unit of cost_per_1m_tokens
SCORING_COMPLEXITY_WEIGHT = 0.1   # Penalty per unit of complexity distance

# ─────────────────────────────────────────────────────────────
# SINGLE SOURCE OF TRUTH: Non-text model keyword blocklist
# Used in: router.py filter_models(), router.py get_best_model(),
#          main.py cascading fallback builder
# ─────────────────────────────────────────────────────────────
NON_TEXT_KEYWORDS = [
    # Embedding models
    "embedding", "embed",
    # Image generation / vision (not for text chat)
    "image-preview", "image-gen", "imagen", "dall-e", "stable-diffusion",
    "-image", "preview-image",
    # Video generation
    "video", "sora", "veo",
    # Audio / TTS / STT
    "tts", "whisper", "speech", "audio", "voice",
    "native-audio", "tts-preview", "preview-tts",
    # Music generation
    "lyria", "music", "clip",
    # Robotics / specialized hardware
    "robotics", "robot",
    # Live / streaming (not for generateContent)
    "live-preview", "live",
    # Safety / moderation classifiers
    "moderation", "safety", "guard",
    # Code execution / tools only
    "code-execution",
]

# Valid model name prefixes (blocks garbage like "nano-banana-pro-preview")
VALID_MODEL_PREFIXES = [
    "gemini-", "gemma-", "palm-", "bard-",          # Google
    "claude-",                                         # Anthropic
    "gpt-", "o1-", "o3-", "o4-", "text-", "dall-e",  # OpenAI
    "llama-", "llama2-", "llama3-", "meta-llama",     # Meta
    "mistral-", "mixtral-", "codestral-",              # Mistral
    "command-", "embed-",                              # Cohere
    "deepseek-", "qwen-", "phi-", "falcon-",           # Others
    "titan-", "nova-", "jurassic-", "j2-",
]

# Safe fallback models (last resort, guaranteed text-capable)
SAFE_FALLBACK_MODELS = [
    {"model_id": "gemini-3-flash", "provider": "Google"},
    {"model_id": "gemini-2.0-flash", "provider": "Google"},
]
