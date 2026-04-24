#FROZEN CODE - DO NOT MODIFY
# Exception: system prompt injection added to fix code-only-text bug

import os
from dotenv import load_dotenv
from openai import OpenAI
from google import genai
from google.genai import types as genai_types

load_dotenv()

# ── CATEGORY-AWARE SYSTEM PROMPTS ──────────────────────────────────────────
# These ensure models produce the right OUTPUT FORMAT for each task type.
# Without this, a 'CODE' request gets a text essay instead of code.
SYSTEM_PROMPTS = {
    "CODE": (
        "You are an expert software engineer. "
        "When asked to code, design, or build something, you MUST provide: "
        "1) Complete, working, runnable code with no placeholders. "
        "2) Clear inline comments explaining key steps. "
        "3) A brief explanation of the architecture after the code. "
        "Always use proper markdown code blocks (```python, ```bash etc.)."
    ),
    "AGENTS": (
        "You are an expert AI systems architect. "
        "When asked to design an agent or agentic pipeline, provide: "
        "1) A complete working implementation with all components. "
        "2) Agent loop, tool definitions, and orchestration logic in code. "
        "3) Architecture diagram in text/ASCII if helpful. "
        "Always use markdown code blocks for all code."
    ),
    "ANALYSIS": (
        "You are an expert data scientist and analyst. "
        "Provide thorough, structured analysis with: "
        "1) Key findings clearly stated. "
        "2) Supporting code or queries where applicable. "
        "3) Actionable conclusions. "
        "Use markdown headers and bullet points for clarity."
    ),
    "EXTRACTION": (
        "You are an expert at data extraction and processing. "
        "Provide complete extraction code/scripts with error handling. "
        "Always show sample output and explain the data schema."
    ),
    "CREATIVE": (
        "You are a creative writing expert. "
        "Provide high-quality, original creative content. "
        "Be imaginative, use vivid language, and fulfill the request fully."
    ),
    "UTILITY": (
        "You are a knowledgeable, helpful assistant. "
        "Provide clear, complete, and accurate answers. "
        "Include examples where helpful."
    ),
    "CHAT": (
        "You are a friendly, knowledgeable conversational assistant. "
        "Be concise but complete. Ask clarifying questions if the request is ambiguous."
    ),
}
DEFAULT_SYSTEM_PROMPT = SYSTEM_PROMPTS["UTILITY"]


class Dispatcher:
    def __init__(self):
        # 1. Native SDKs - lazy load to avoid import errors
        self.client_anthropic = None
        self.client_cohere = None
        self.client_google = None
        
        # Google API configured at startup (optional)
        try:
            self.client_google = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))
        except:
            pass

        # 2. OpenAI-Compatible Hub - lazy load clients
        self.hub = {}

    def _get_hub_client(self, provider):
        """Lazily initialize and return OpenAI-compatible client."""
        if provider not in self.hub:
            hub_config = {
                "OpenAI": (os.getenv("OPENAI_API_KEY"), None),
                "xAI": (os.getenv("XAI_API_KEY"), "https://api.x.ai/v1"),
                "OpenRouter": (os.getenv("OPENROUTER_API_KEY"), "https://openrouter.ai/api/v1"),
                "Together": (os.getenv("TOGETHER_API_KEY"), "https://api.together.xyz/v1"),
                "DeepSeek": (os.getenv("DEEPSEEK_API_KEY"), "https://api.deepseek.com"),
                "Mistral": (os.getenv("MISTRAL_API_KEY"), "https://api.mistral.ai/v1"),
                "HuggingFace": (os.getenv("HUGGINGFACE_API_KEY"), "https://api-inference.huggingface.co/v1")
            }
            
            if provider in hub_config:
                api_key, base_url = hub_config[provider]
                if api_key:
                    try:
                        if base_url:
                            self.hub[provider] = OpenAI(api_key=api_key, base_url=base_url)
                        else:
                            self.hub[provider] = OpenAI(api_key=api_key)
                    except Exception as e:
                        return None
        
        return self.hub.get(provider)

    def execute(self, provider, model_id, prompt, category="UTILITY"):
        """
        Standardized execution returning {'text': str, 'tokens': int, 'success': bool}
        
        category: task category (CODE, AGENTS, ANALYSIS, etc.) used to select
                  the appropriate system prompt so models produce the right output format.
        """
        system_prompt = SYSTEM_PROMPTS.get(category.upper(), DEFAULT_SYSTEM_PROMPT)

        try:
            # Route to OpenAI-Compatible Hub
            if provider in ["OpenAI", "xAI", "OpenRouter", "Together", "DeepSeek", "Mistral", "HuggingFace"]:
                client = self._get_hub_client(provider)
                if not client:
                    return {"text": f"Error: {provider} API key not configured.", "tokens": 0, "success": False}
                
                response = client.chat.completions.create(
                    model=model_id,
                    messages=[
                        {"role": "system", "content": system_prompt},
                        {"role": "user",   "content": prompt}
                    ]
                )
                return {
                    "text": response.choices[0].message.content,
                    "tokens": response.usage.total_tokens if response.usage else 0,
                    "success": True
                }

            # Route to Anthropic
            elif provider == "Anthropic":
                try:
                    from anthropic import Anthropic
                    if not self.client_anthropic:
                        self.client_anthropic = Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))
                    response = self.client_anthropic.messages.create(
                        model=model_id,
                        max_tokens=4096,
                        system=system_prompt,  # Anthropic uses top-level 'system' param
                        messages=[{"role": "user", "content": prompt}]
                    )
                    tokens = response.usage.input_tokens + response.usage.output_tokens
                    return {"text": response.content[0].text, "tokens": tokens, "success": True}
                except ImportError:
                    return {"text": "Error: Anthropic SDK not installed. Install with: pip install anthropic", "tokens": 0, "success": False}

            # Route to Google
            elif provider == "Google":
                if not self.client_google:
                    self.client_google = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))
                
                if self.client_google:
                    response = self.client_google.models.generate_content(
                        model=model_id,
                        contents=prompt,
                        config=genai_types.GenerateContentConfig(
                            system_instruction=system_prompt,
                            max_output_tokens=8192,
                        )
                    )
                    return {
                        "text": response.text,
                        "tokens": response.usage_metadata.total_token_count if response.usage_metadata else 0,
                        "success": True
                    }
                else:
                    return {"text": "Error: Google API key not configured.", "tokens": 0, "success": False}

            # Route to Cohere
            elif provider == "Cohere":
                try:
                    import cohere
                    if not self.client_cohere:
                        co_key = os.getenv("COHERE_API_KEY")
                        self.client_cohere = cohere.Client(co_key) if co_key else None
                    
                    if self.client_cohere:
                        # Cohere uses preamble as system prompt
                        response = self.client_cohere.chat(
                            model=model_id,
                            preamble=system_prompt,
                            message=prompt
                        )
                        return {
                            "text": response.text, 
                            "tokens": response.meta.tokens.total_tokens if response.meta else 0,
                            "success": True
                        }
                    else:
                        return {"text": "Error: Cohere API key not configured.", "tokens": 0, "success": False}
                except ImportError:
                    return {"text": "Error: Cohere SDK not installed. Install with: pip install cohere", "tokens": 0, "success": False}

            # If no provider matches
            return {"text": f"Error: Provider '{provider}' not configured.", "tokens": 0, "success": False}

        except Exception as e:
            # Always return a dict even on error to prevent main.py from crashing
            return {"text": f"Execution Error [{provider}]: {str(e)}", "tokens": 0, "success": False}

