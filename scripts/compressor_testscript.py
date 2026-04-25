import sys
import os

# Add root to python path so we can import app modules
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from app.routing.prompt_compressor import get_prompt_compressor

def test_compressor():
    print("=== Testing Prompt Compressor ===")
    
    compressor = get_prompt_compressor()
    
    test_prompt = """
    Could you please write a python script that will connect to a postgresql database and then fetch all of the users from the users table? 
    I would really appreciate it if you could also add some inline comments explaining what each line of the code is doing.
    Thank you so much!
    """
    
    print(f"\nOriginal Prompt (length: {len(test_prompt)}):")
    print(test_prompt.strip())
    
    compressed_prompt, metrics = compressor.compress(test_prompt)
    
    print(f"\nCompressed Prompt (length: {len(compressed_prompt)}):")
    print(compressed_prompt.strip())
    
    compression_ratio = 100 - (len(compressed_prompt) / len(test_prompt) * 100)
    print(f"\nSpace saved: {compression_ratio:.1f}%")

if __name__ == "__main__":
    test_compressor()
