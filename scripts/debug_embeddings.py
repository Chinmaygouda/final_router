import os
import time
from langchain_huggingface import HuggingFaceEmbeddings

print("[*] Diagnostic Start")
model_name = "BAAI/bge-base-en-v1.5"

# Force offline if requested
if os.environ.get("TRANSFORMERS_OFFLINE") == "1":
    print("[!] TRANSFORMERS_OFFLINE is set to 1")

try:
    print(f"[*] Attempting to initialize HuggingFaceEmbeddings with: {model_name}")
    start = time.time()
    
    # We use a timeout or just print steps
    print("[*] Calling constructor...")
    embeddings = HuggingFaceEmbeddings(
        model_name=model_name,
        model_kwargs={"device": "cpu"},
        encode_kwargs={"normalize_embeddings": True},
    )
    
    end = time.time()
    print(f"[OK] Model loaded in {end - start:.2f} seconds.")
    
    print("[*] Testing a small embedding...")
    vec = embeddings.embed_query("Hello world")
    print(f"[OK] Embedding generated. Vector size: {len(vec)}")

except Exception as e:
    print(f"[ERROR] Failed: {e}")
    import traceback
    traceback.print_exc()
