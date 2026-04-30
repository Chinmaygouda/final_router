import os
from langchain_huggingface import HuggingFaceEmbeddings

# Embedding model for semantic vault search.
# UPGRADED to BAAI/bge-base-en-v1.5
# - 768 dimensions (no DB schema change needed)
# - MTEB score: 63.5 (better than previous model)
# - Works 100% offline after first download (~440MB)
#
# FIX: Lazy loading — model is initialized on FIRST call to generate_vector(),
# NOT at import time. This prevents the server event loop from freezing for
# 30-60 seconds on every restart, making /health and all other fast endpoints
# respond instantly.

import threading

model_name = "BAAI/bge-base-en-v1.5"
_embeddings = None  # Lazy singleton
_embeddings_lock = threading.Lock()


def _get_embeddings():
    """Return the embedding model, loading it on first call only (Thread Safe)."""
    global _embeddings
    if _embeddings is None:
        with _embeddings_lock:
            # Double-check pattern to prevent race conditions
            if _embeddings is None:
                print(f"⚙️  Loading embedding model: {model_name} (first request only)...")
                _embeddings = HuggingFaceEmbeddings(
                    model_name=model_name,
                    model_kwargs={"device": "cpu"},
                    encode_kwargs={"normalize_embeddings": True},  # BGE requires normalization
                )
                print(f"✅ Embedding model ready.")
    return _embeddings


def generate_vector(text: str):
    """
    Generates a 768-dimension embedding vector locally.
    Privacy: 100% | Cost: $0.00
    Model is lazy-loaded on the first call.
    """
    try:
        print(f"⚙️  Engine: Embedding '{text[:40]}...'")
        vector = _get_embeddings().embed_query(text)
        return vector
    except Exception as e:
        print(f"❌ Local Embedding Error: {e}")
        return None