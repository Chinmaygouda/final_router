import os
from langchain_huggingface import HuggingFaceEmbeddings

# This loads the model locally. The first time it runs, it will download (~400MB).
# After that, it works 100% offline and for free.
model_name = "sentence-transformers/all-mpnet-base-v2"
local_embeddings = HuggingFaceEmbeddings(
    model_name=model_name,
    model_kwargs={'device': 'cpu'} 
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