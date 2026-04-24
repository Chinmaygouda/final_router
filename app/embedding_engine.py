import os
from langchain_huggingface import HuggingFaceEmbeddings

# Embedding model for semantic vault search.
# UPGRADED from sentence-transformers/all-mpnet-base-v2 to BAAI/bge-base-en-v1.5
# - Same 768 dimensions (no DB schema change needed)
# - MTEB score: 63.5 vs 57.8 (significantly better semantic distinction)
# - Better at distinguishing "sorting algorithm" from "searching algorithm"
# First run downloads ~440MB, then works 100% offline and free.
model_name = "BAAI/bge-base-en-v1.5"
local_embeddings = HuggingFaceEmbeddings(
    model_name=model_name,
    model_kwargs={'device': 'cpu'},
    encode_kwargs={'normalize_embeddings': True}  # BGE models require normalization
)

def generate_vector(text: str):
    """
    Generates a 768-dimension vector locally.
    Privacy: 100% | Cost: $0.00
    """
    try:
        print(f"⚙️  Engine: Processing text... '{text[:30]}...'")
        # LangChain logic to embed the text
        vector = local_embeddings.embed_query(text)
        return vector
    except Exception as e:
        print(f"❌ Local Embedding Error: {e}")
        return None