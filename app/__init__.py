"""App package."""
import os
from pathlib import Path
from dotenv import load_dotenv

# CRITICAL: Load .env BEFORE any other imports
# This ensures TRANSFORMERS_OFFLINE and HF_HUB_OFFLINE are set before HuggingFace libraries load
# Find .env file (should be in project root, parent of app/)
env_path = Path(__file__).parent.parent / ".env"
if env_path.exists():
    load_dotenv(env_path)
else:
    # Fallback: try current working directory
    load_dotenv()
