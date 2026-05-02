"""
rebuild_model_head.py
---------------------
Rebuilds the corrupted model_head.pkl by:
1. Loading the existing sentence-transformer body (model.safetensors) 
2. Generating embeddings for a labeled training set
3. Training a fresh LogisticRegression with current sklearn
4. Saving as model_head.pkl

Run once:
  python scripts/rebuild_model_head.py
"""

import os, sys, pickle, warnings
import numpy as np

# ── Compatibility patches ────────────────────────────────────────────────────
import transformers.training_args
if not hasattr(transformers.training_args, 'default_logdir'):
    transformers.training_args.default_logdir = lambda *a, **k: "./runs"
import huggingface_hub
if not hasattr(huggingface_hub, 'DatasetFilter'):
    class DatasetFilter: pass
    huggingface_hub.DatasetFilter = DatasetFilter
# ─────────────────────────────────────────────────────────────────────────────

MODEL_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), "models", "deberta-router")
HEAD_PATH  = os.path.join(MODEL_PATH, "model_head.pkl")
BACKUP     = os.path.join(MODEL_PATH, "model_head_corrupted_backup.pkl")

# ── Labeled training data ────────────────────────────────────────────────────
# Each entry: (prompt_text, label)
TRAINING_DATA = [
    # UTILITY
    ("hi how are you", "UTILITY"),
    ("hello", "UTILITY"),
    ("nice to meet you", "UTILITY"),
    ("what time is it", "UTILITY"),
    ("thanks", "UTILITY"),
    ("what is the capital of France", "UTILITY"),
    ("tell me a joke", "UTILITY"),
    ("what is 2 plus 2", "UTILITY"),
    ("who are you", "UTILITY"),
    ("what can you do", "UTILITY"),

    # CHAT
    ("how was your day", "CHAT"),
    ("let's chat", "CHAT"),
    ("what do you think about movies", "CHAT"),
    ("do you like music", "CHAT"),
    ("what's your favorite color", "CHAT"),
    ("talk to me", "CHAT"),

    # CODE
    ("write a python function to reverse a string", "CODE"),
    ("implement binary search in python", "CODE"),
    ("create a REST API with FastAPI", "CODE"),
    ("write a class for a binary tree", "CODE"),
    ("build a web scraper using BeautifulSoup", "CODE"),
    ("implement quicksort algorithm", "CODE"),
    ("write a decorator function in python", "CODE"),
    ("create a linked list implementation", "CODE"),
    ("write unit tests for my python module", "CODE"),
    ("implement a rate limiter in python", "CODE"),
    ("build a flask web application", "CODE"),
    ("write a dockerfile for a python app", "CODE"),

    # ANALYSIS
    ("analyze the performance of this algorithm", "ANALYSIS"),
    ("explain the time complexity of merge sort", "ANALYSIS"),
    ("compare REST vs GraphQL APIs", "ANALYSIS"),
    ("what are the pros and cons of microservices", "ANALYSIS"),
    ("analyze this dataset and find patterns", "ANALYSIS"),
    ("explain the difference between supervised and unsupervised learning", "ANALYSIS"),
    ("what are the tradeoffs between SQL and NoSQL databases", "ANALYSIS"),
    ("evaluate the security risks of this architecture", "ANALYSIS"),

    # EXTRACTION
    ("extract all email addresses from this text", "EXTRACTION"),
    ("parse this JSON and extract the user fields", "EXTRACTION"),
    ("scrape product prices from this webpage", "EXTRACTION"),
    ("extract key information from this PDF", "EXTRACTION"),
    ("pull out all dates mentioned in this document", "EXTRACTION"),
    ("write a regex to extract phone numbers", "EXTRACTION"),

    # AGENTS
    ("design an autonomous agent that can browse the web", "AGENTS"),
    ("build an AI agent pipeline with tool use", "AGENTS"),
    ("create a multi-agent system for research", "AGENTS"),
    ("design an agentic workflow for data processing", "AGENTS"),
    ("implement a ReAct agent with memory", "AGENTS"),

    # CREATIVE
    ("write a short story about a robot", "CREATIVE"),
    ("compose a poem about the ocean", "CREATIVE"),
    ("write a product description for a smartwatch", "CREATIVE"),
    ("create a marketing tagline for a coffee brand", "CREATIVE"),
    ("write a blog post about artificial intelligence", "CREATIVE"),
]

LABELS = ["UTILITY", "CHAT", "CODE", "ANALYSIS", "EXTRACTION", "AGENTS", "CREATIVE"]


def main():
    print("=" * 60)
    print("DeBERTa Model Head Rebuild Script")
    print("=" * 60)

    # Step 1: Verify model body exists
    if not os.path.exists(MODEL_PATH):
        print(f"[ERROR] Model folder not found: {MODEL_PATH}")
        sys.exit(1)
    print(f"[OK] Model folder found: {MODEL_PATH}")

    # Step 2: Backup corrupted head
    if os.path.exists(HEAD_PATH):
        import shutil
        shutil.copy2(HEAD_PATH, BACKUP)
        print(f"[OK] Corrupted head backed up to: {os.path.basename(BACKUP)}")

    # Step 3: Load the sentence transformer body
    print("\n[STEP 1] Loading sentence transformer body...")
    print("  (This may take 30-60 seconds on first load...)")
    from sentence_transformers import SentenceTransformer
    body = SentenceTransformer(MODEL_PATH)
    print("  [OK] Body loaded!")

    # Step 4: Generate embeddings for training data
    print("\n[STEP 2] Generating embeddings for training examples...")
    prompts = [item[0] for item in TRAINING_DATA]
    labels  = [item[1] for item in TRAINING_DATA]
    
    with warnings.catch_warnings():
        warnings.simplefilter("ignore")
        embeddings = body.encode(prompts, show_progress_bar=True, batch_size=16)
    print(f"  [OK] Generated {len(embeddings)} embeddings of dim {embeddings.shape[1]}")

    # Step 5: Train a fresh LogisticRegression head
    print("\n[STEP 3] Training new LogisticRegression head...")
    from sklearn.linear_model import LogisticRegression
    from sklearn.preprocessing import LabelEncoder

    le = LabelEncoder()
    y = le.fit_transform(labels)

    clf = LogisticRegression(
        max_iter=1000,
        C=1.0,
        solver="lbfgs",
        multi_class="multinomial",
        random_state=42
    )
    clf.fit(embeddings, y)
    clf.classes_ = le.classes_   # Store string class names

    # Quick accuracy check on training data (just to verify it works)
    preds = clf.predict(embeddings)
    from sklearn.metrics import accuracy_score
    acc = accuracy_score(y, preds)
    print(f"  [OK] Training accuracy: {acc*100:.1f}%")

    # Step 6: Wrap into SetFit-compatible format and save
    print("\n[STEP 4] Saving new model_head.pkl...")
    with open(HEAD_PATH, "wb") as f:
        pickle.dump(clf, f)
    print(f"  [OK] Saved to: {HEAD_PATH}")

    # Step 7: Verify full SetFit pipeline works
    print("\n[STEP 5] Verifying full pipeline...")
    try:
        from setfit import SetFitModel
        with warnings.catch_warnings():
            warnings.simplefilter("ignore")
            model = SetFitModel.from_pretrained(MODEL_PATH)

        test_cases = [
            "hi how are you",
            "write a python function to sort a list",
            "design a distributed microservices architecture with kubernetes",
            "analyze the performance tradeoffs of this algorithm",
        ]
        results = model.predict(test_cases)
        print("\n  Test Results:")
        for prompt, result in zip(test_cases, results):
            print(f"    '{prompt[:50]}' → {result}")
        print("\n🎉 SUCCESS! DeBERTa is fixed.")
        print("   Restart your uvicorn server to apply the fix.")
    except Exception as e:
        print(f"\n  [WARN] SetFit verification step failed: {e}")
        print("  But the model_head.pkl was saved. Try restarting the server anyway.")


if __name__ == "__main__":
    main()
