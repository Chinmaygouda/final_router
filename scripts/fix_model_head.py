"""
fix_model_head.py
-----------------
Regenerates the model_head.pkl file for the DeBERTa SetFit classifier
using the current version of scikit-learn (1.8.0).

The old model_head.pkl was trained with sklearn 1.6.1 which causes:
  InconsistentVersionWarning → NoneType error → classifier = None → score always 2.5

Run this once:
  python scripts/fix_model_head.py
"""

import os
import sys
import pickle
import numpy as np

# ── Compatibility patches (same as deberta_classifier.py) ──────────────────
import transformers.training_args
if not hasattr(transformers.training_args, 'default_logdir'):
    transformers.training_args.default_logdir = lambda *args, **kwargs: "./runs"

import huggingface_hub
if not hasattr(huggingface_hub, 'DatasetFilter'):
    class DatasetFilter:
        pass
    huggingface_hub.DatasetFilter = DatasetFilter
# ───────────────────────────────────────────────────────────────────────────

MODEL_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), "models", "deberta-router")
HEAD_PATH  = os.path.join(MODEL_PATH, "model_head.pkl")
HEAD_BACKUP= os.path.join(MODEL_PATH, "model_head_backup_sklearn161.pkl")

def main():
    print("=" * 60)
    print("DeBERTa Model Head Regeneration Script")
    print("=" * 60)

    # Step 1: Verify paths exist
    if not os.path.exists(MODEL_PATH):
        print(f"[ERROR] Model folder not found: {MODEL_PATH}")
        sys.exit(1)
    if not os.path.exists(HEAD_PATH):
        print(f"[ERROR] model_head.pkl not found at: {HEAD_PATH}")
        sys.exit(1)

    # Step 2: Load the old head with warnings suppressed
    print(f"\n[STEP 1] Loading old model_head.pkl (sklearn 1.6.1 format)...")
    import warnings
    with warnings.catch_warnings():
        warnings.simplefilter("ignore")
        with open(HEAD_PATH, "rb") as f:
            old_head = pickle.load(f)
    print(f"  Type: {type(old_head)}")
    print(f"  Head object: {old_head}")

    # Step 3: Extract the LogisticRegression internals
    print(f"\n[STEP 2] Extracting LogisticRegression weights...")
    from sklearn.linear_model import LogisticRegression

    # The SetFit head is a sklearn LogisticRegression
    # We need to recreate it with current sklearn and copy the weights over
    new_head = LogisticRegression(max_iter=1000)

    # Copy all fitted attributes from the old model
    attrs_to_copy = [
        'coef_', 'intercept_', 'classes_', 'n_features_in_',
        'n_iter_', 'solver', 'multi_class', 'C', 'max_iter'
    ]
    copied = []
    for attr in attrs_to_copy:
        if hasattr(old_head, attr):
            setattr(new_head, attr, getattr(old_head, attr))
            copied.append(attr)
    print(f"  Copied attributes: {copied}")

    if 'coef_' not in copied:
        print("[ERROR] Could not extract model weights. The head may be a different type.")
        print(f"  Available attributes: {[a for a in dir(old_head) if not a.startswith('__')]}")
        sys.exit(1)

    # Step 4: Backup the old head
    print(f"\n[STEP 3] Backing up old head to: {HEAD_BACKUP}")
    import shutil
    shutil.copy2(HEAD_PATH, HEAD_BACKUP)
    print("  ✅ Backup created.")

    # Step 5: Save the new head
    print(f"\n[STEP 4] Saving new model_head.pkl with sklearn {__import__('sklearn').__version__}...")
    with open(HEAD_PATH, "wb") as f:
        pickle.dump(new_head, f)
    print("  ✅ New model_head.pkl saved.")

    # Step 6: Verify it loads correctly
    print(f"\n[STEP 5] Verifying the fix works...")
    try:
        from setfit import SetFitModel
        model = SetFitModel.from_pretrained(MODEL_PATH)
        test_prompt = ["Design a distributed microservices architecture with Kubernetes"]
        result = model.predict(test_prompt)
        print(f"  ✅ Model loads successfully!")
        print(f"  Test prediction: '{test_prompt[0][:50]}...' → {result}")
        print(f"\n🎉 SUCCESS! DeBERTa is fixed. Restart your uvicorn server.")
    except Exception as e:
        print(f"  ❌ Verification failed: {e}")
        print(f"  Restoring backup...")
        shutil.copy2(HEAD_BACKUP, HEAD_PATH)
        print(f"  Backup restored. Error details: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
