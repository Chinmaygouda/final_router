import tiktoken

def estimate_tokens(system_prompt: str, user_prompt: str, model: str = "gpt-4o"):
    """
    Estimates the input token count using tiktoken.
    This is highly accurate for OpenAI and a very close approximation for Anthropic/Gemini.
    """
    try:
        enc = tiktoken.encoding_for_model(model)
    except KeyError:
        print(f"Warning: model {model} not found. Using cl100k_base encoding.")
        enc = tiktoken.get_encoding("cl100k_base")

    sys_tokens = len(enc.encode(system_prompt))
    usr_tokens = len(enc.encode(user_prompt))
    total = len(enc.encode(system_prompt + "\n" + user_prompt))

    print("=== TIKTOKEN ESTIMATION ===")
    print(f"System Prompt : {sys_tokens} tokens")
    print(f"User Prompt   : {usr_tokens} tokens")
    print("-" * 30)
    print(f"Total Input   : {total} tokens\n")
    return total

if __name__ == "__main__":
    # --- Example 1: MEDIUM Prompt ---
    print("--- TESTING: MEDIUM PROMPT (Fibonacci) ---")
    m_sys = "You are an expert software engineer. Provide working code with brief explanations. Use proper markdown code blocks."
    m_usr = "Write a python function to calculate the Fibonacci sequence up to N."
    estimate_tokens(m_sys, m_usr)

    # --- Example 2: HEAVY Prompt ---
    print("--- TESTING: HEAVY PROMPT (Microservices) ---")
    h_sys = "You are an expert software engineer. When asked to code, design, or build something, you MUST provide: 1) Complete, working, runnable code with no placeholders. 2) Clear inline comments explaining key steps. 3) A brief explanation of the architecture after the code. Always use proper markdown code blocks (```python, ```bash etc.)."
    h_usr = "Design a full-stack microservices architecture for a real-time stock trading app with high availability and low latency."
    estimate_tokens(h_sys, h_usr)
