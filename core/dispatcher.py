"""
Dispatcher — Multi-Provider Execution Engine
============================================
Feature Additions:
  - Feature 1:  Streaming via execute_stream() async generator
  - Feature 6:  Multi-Modal (image_b64 / image_url) for vision models
  - Feature 13: Operator-Level System Prompt (injected before category prompt)
"""

import os
from typing import AsyncGenerator, Optional
from dotenv import load_dotenv
from openai import OpenAI
from google import genai
from google.genai import types as genai_types

load_dotenv()

# ── FEATURE 13: Operator-Level System Prompt ─────────────────────────────────
# Set OPERATOR_SYSTEM_PROMPT in your .env to customize all responses globally.
# Example: "You are an assistant specialized in mining and ore detection."
OPERATOR_SYSTEM_PROMPT = os.getenv("OPERATOR_SYSTEM_PROMPT", "")

# ── CATEGORY-AWARE SYSTEM PROMPTS ────────────────────────────────────────────
HEAVY_SYSTEM_PROMPTS = {
    "CODE": "Engineer: runnable code; no placeholders; inline comments; architecture; markdown.",
    "AGENTS": "Architect: full impl; loop/tools/orch; ASCII if useful; markdown.",
    "ANALYSIS": "Analyst: findings; code/queries; actionable conclusions; structured.",
    "EXTRACTION": "Extractor: full scripts; error handling; sample + schema.",
    "CREATIVE": "Writer: original, vivid, complete content.",
    "UTILITY": "Assistant: clear, accurate answers; examples if useful.",
    "CHAT": "Assistant: concise; clear; ask if unclear."
}

MEDIUM_SYSTEM_PROMPTS = {
    "CODE": "Engineer: code + brief explanation; markdown.",
    "AGENTS": "Architect: agent code; markdown.",
    "ANALYSIS": "Analyst: structured analysis; findings.",
    "EXTRACTION": "Extractor: scripts/code.",
    "CREATIVE": "Writer: original, vivid content.",
    "UTILITY": "Assistant: clear answers.",
    "CHAT": "Assistant: concise."
}

LIGHT_SYSTEM_PROMPTS = {
    "CODE": "Engineer: code only; no explanation.",
    "AGENTS": "Architect: code only; no explanation.",
    "ANALYSIS": "Analyst: findings only; concise.",
    "EXTRACTION": "Extractor: script only.",
    "CREATIVE": "Writer: creative, concise.",
    "UTILITY": "Assistant: direct; no filler.",
    "CHAT": "Assistant: short; no filler."
}

DEFAULT_SYSTEM_PROMPT = MEDIUM_SYSTEM_PROMPTS["UTILITY"]


def _get_max_tokens(complexity_score: float) -> int:
    """
    Implements the 'Double Lock' token ceiling.
    Prevents runaway hallucination loops by setting strict max_tokens.
    """
    if complexity_score < 4.0:
        return 500
    elif complexity_score <= 7.0:
        return 2000
    else:
        return 8192

def _build_system_prompt(category: str, complexity_score: float) -> str:
    """
    Returns a dynamic system prompt based on category and complexity tier.
    Operator-level prompt from .env is prepended if set.
    """
    if complexity_score < 4.0:
        prompts_dict = LIGHT_SYSTEM_PROMPTS
    elif complexity_score > 7.0:
        prompts_dict = HEAVY_SYSTEM_PROMPTS
    else:
        prompts_dict = MEDIUM_SYSTEM_PROMPTS
        
    base = prompts_dict.get(category.upper(), DEFAULT_SYSTEM_PROMPT)

    if OPERATOR_SYSTEM_PROMPT:
        return f"{OPERATOR_SYSTEM_PROMPT}\n\n{base}"
    return base


# ── VISION-CAPABLE MODELS (Feature 6) ────────────────────────────────────────
VISION_MODELS = {
    "Google":    ["gemini-2.0-flash", "gemini-1.5-pro", "gemini-2.5-flash", "gemini-flash-latest"],
    "Anthropic": ["claude-3-opus-20240229", "claude-3-sonnet-20240229", "claude-3-5-sonnet-20241022"],
    "OpenAI":    ["gpt-4o", "gpt-4-turbo", "gpt-4-vision-preview"],
}


def _detect_mime_type(image_b64: str = None, image_url: str = None) -> str:
    """
    Auto-detect image MIME type from base64 header bytes or URL extension.
    Prevents Google Gemini from rejecting PNG/WebP images sent as 'image/jpeg'.
    """
    if image_b64:
        import base64
        try:
            header = base64.b64decode(image_b64[:16])
            if header[:8] == b'\x89PNG\r\n\x1a\n':
                return "image/png"
            if header[:4] == b'RIFF' and header[8:12] == b'WEBP':
                return "image/webp"
            if header[:6] in (b'GIF87a', b'GIF89a'):
                return "image/gif"
            if header[:2] == b'\xff\xd8':
                return "image/jpeg"
        except Exception:
            pass
    if image_url:
        url_lower = image_url.lower().split('?')[0]  # strip query params
        if url_lower.endswith('.png'):
            return "image/png"
        if url_lower.endswith('.webp'):
            return "image/webp"
        if url_lower.endswith('.gif'):
            return "image/gif"
    return "image/jpeg"  # safe default


class Dispatcher:
    def __init__(self):
        self.client_anthropic = None
        self.client_cohere = None
        self.client_google = None

        try:
            self.client_google = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))
        except Exception:
            pass

        self.hub = {}

    def _get_hub_client(self, provider, api_keys=None):
        """Lazily initialize and return OpenAI-compatible client."""
        custom_key = None
        if api_keys:
            key_map = {
                "OpenAI": "openai",
                "NVIDIA": "nvidia",
                "xAI": "xai",
                "OpenRouter": "openrouter",
                "Together": "together",
                "DeepSeek": "deepseek",
                "Mistral": "mistral",
                "HuggingFace": "huggingface"
            }
            mapped_key = key_map.get(provider)
            if mapped_key and api_keys.get(mapped_key):
                custom_key = api_keys.get(mapped_key)

        hub_config = {
            "OpenAI":      (os.getenv("OPENAI_API_KEY"),      None),
            "NVIDIA":      (os.getenv("NVIDIA_API_KEY"),      "https://integrate.api.nvidia.com/v1"),
            "xAI":         (os.getenv("XAI_API_KEY"),          "https://api.x.ai/v1"),
            "OpenRouter":  (os.getenv("OPENROUTER_API_KEY"),   "https://openrouter.ai/api/v1"),
            "Together":    (os.getenv("TOGETHER_API_KEY"),     "https://api.together.xyz/v1"),
            "DeepSeek":    (os.getenv("DEEPSEEK_API_KEY"),     "https://api.deepseek.com"),
            "Mistral":     (os.getenv("MISTRAL_API_KEY"),      "https://api.mistral.ai/v1"),
            "HuggingFace": (os.getenv("HUGGINGFACE_API_KEY"),  "https://api-inference.huggingface.co/v1"),
        }

        # If custom key, create and return one-off client
        if custom_key and provider in hub_config:
            _, base_url = hub_config[provider]
            return OpenAI(api_key=custom_key, base_url=base_url, timeout=15.0) if base_url else OpenAI(api_key=custom_key, timeout=15.0)

        if provider not in self.hub:
            if provider in hub_config:
                api_key, base_url = hub_config[provider]
                if api_key:
                    try:
                        self.hub[provider] = (
                            OpenAI(api_key=api_key, base_url=base_url, timeout=15.0)
                            if base_url else OpenAI(api_key=api_key, timeout=15.0)
                        )
                    except Exception:
                        return None
        return self.hub.get(provider)

    def _build_vision_content(self, prompt: str, image_b64: Optional[str], image_url: Optional[str]):
        """Build multi-modal content array for providers that support vision."""
        content = [{"type": "text", "text": prompt}]
        if image_b64:
            content.append({
                "type": "image_url",
                "image_url": {"url": f"data:image/jpeg;base64,{image_b64}"}
            })
        elif image_url:
            content.append({
                "type": "image_url",
                "image_url": {"url": image_url}
            })
        return content

    # ──────────────────────────────────────────────────────────────────────
    # STANDARD EXECUTE (blocking)
    # ──────────────────────────────────────────────────────────────────────
    def execute(
        self,
        provider: str,
        model_id: str,
        prompt: str,
        category: str = "UTILITY",
        complexity_score: float = 5.0,
        image_b64: Optional[str] = None,
        image_url: Optional[str] = None,
        system_prompt_override: Optional[str] = None,
        api_keys: Optional[dict] = None
    ) -> dict:
        """
        Standardized blocking execution.
        Returns {'text': str, 'tokens': int, 'success': bool}

        Features:
          - category: selects system prompt
          - image_b64 / image_url: enables vision/multi-modal (Feature 6)
          - OPERATOR_SYSTEM_PROMPT is automatically prepended (Feature 13)
        """
        system_prompt = _build_system_prompt(category, complexity_score)
        if system_prompt_override:
            system_prompt = f"{system_prompt_override}\n\n{system_prompt}"
            
        has_image = bool(image_b64 or image_url)

        try:
            # ── OpenAI-Compatible Hub ──────────────────────────────────
            if provider in ["OpenAI", "NVIDIA", "xAI", "OpenRouter", "Together", "DeepSeek", "Mistral", "HuggingFace"]:
                client = self._get_hub_client(provider, api_keys)
                if not client:
                    return {"text": f"Error: Provider API key not configured.", "tokens": 0, "success": False}

                # Feature 6: Use vision content if image provided
                user_content = (
                    self._build_vision_content(prompt, image_b64, image_url)
                    if has_image else prompt
                )
                response = client.chat.completions.create(
                    model=model_id,
                    messages=[
                        {"role": "system", "content": system_prompt},
                        {"role": "user",   "content": user_content}
                    ],
                    max_tokens=_get_max_tokens(complexity_score)
                )
                return {
                    "text":    response.choices[0].message.content,
                    "tokens":  response.usage.total_tokens if response.usage else 0,
                    "success": True,
                }

            # ── Anthropic ─────────────────────────────────────────────
            elif provider == "Anthropic":
                try:
                    from anthropic import Anthropic
                    custom_anthropic = api_keys.get("anthropic") if api_keys else None
                    if custom_anthropic:
                        client = Anthropic(api_key=custom_anthropic)
                    else:
                        if not self.client_anthropic:
                            self.client_anthropic = Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))
                        client = self.client_anthropic

                    # Feature 6: vision content for Anthropic
                    if has_image:
                        img_src = (
                            {"type": "base64", "media_type": "image/jpeg", "data": image_b64}
                            if image_b64
                            else {"type": "url", "url": image_url}
                        )
                        user_content = [
                            {"type": "image", "source": img_src},
                            {"type": "text",  "text": prompt},
                        ]
                    else:
                        user_content = prompt

                    response = client.messages.create(
                        model=model_id,
                        max_tokens=_get_max_tokens(complexity_score),
                        system=system_prompt,
                        messages=[{"role": "user", "content": user_content}]
                    )
                    tokens = response.usage.input_tokens + response.usage.output_tokens
                    return {"text": response.content[0].text, "tokens": tokens, "success": True}
                except ImportError:
                    return {"text": "Error: Anthropic SDK not installed. Run: pip install anthropic", "tokens": 0, "success": False}

            # ── Google Gemini ─────────────────────────────────────────
            elif provider == "Google":
                custom_google = api_keys.get("gemini") if api_keys else None
                if custom_google:
                    client = genai.Client(api_key=custom_google)
                else:
                    if not self.client_google:
                        self.client_google = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))
                    client = self.client_google
                    
                if not client:
                    return {"text": "Error: Google API key not configured.", "tokens": 0, "success": False}

                # Feature 6: Add image parts for Gemini vision
                if has_image:
                    import base64
                    mime = _detect_mime_type(image_b64=image_b64, image_url=image_url)
                    if image_b64:
                        img_bytes = base64.b64decode(image_b64)
                        contents = [
                            genai_types.Part.from_bytes(data=img_bytes, mime_type=mime),
                            prompt,
                        ]
                    else:
                        contents = [genai_types.Part.from_uri(file_uri=image_url, mime_type=mime), prompt]
                else:
                    contents = prompt

                response = client.models.generate_content(
                    model=model_id,
                    contents=contents,
                    config=genai_types.GenerateContentConfig(
                        system_instruction=system_prompt,
                        max_output_tokens=_get_max_tokens(complexity_score),
                    )
                )
                return {
                    "text":    response.text,
                    "tokens":  response.usage_metadata.total_token_count if response.usage_metadata else 0,
                    "success": True,
                }

            # ── Cohere ────────────────────────────────────────────────
            elif provider == "Cohere":
                try:
                    import cohere
                    if not self.client_cohere:
                        co_key = os.getenv("COHERE_API_KEY")
                        self.client_cohere = cohere.Client(co_key) if co_key else None
                    if self.client_cohere:
                        response = self.client_cohere.chat(
                            model=model_id,
                            preamble=system_prompt,
                            message=prompt,
                            max_tokens=_get_max_tokens(complexity_score)
                        )
                        return {
                            "text":    response.text,
                            "tokens":  response.meta.tokens.total_tokens if response.meta else 0,
                            "success": True,
                        }
                    return {"text": "Error: Cohere API key not configured.", "tokens": 0, "success": False}
                except ImportError:
                    return {"text": "Error: Cohere SDK not installed. Run: pip install cohere", "tokens": 0, "success": False}

            return {"text": f"Error: Provider '{provider}' not configured.", "tokens": 0, "success": False}

        except Exception as e:
            return {"text": f"Execution Error [{provider}]: {str(e)}", "tokens": 0, "success": False}

    # ──────────────────────────────────────────────────────────────────────
    # STREAMING EXECUTE (Feature 1) — async generator
    # ──────────────────────────────────────────────────────────────────────
    async def execute_stream(
        self,
        provider: str,
        model_id: str,
        prompt: str,
        category: str = "UTILITY",
        complexity_score: float = 5.0,
        image_b64: Optional[str] = None,
        image_url: Optional[str] = None,
        system_prompt_override: Optional[str] = None,
        api_keys: Optional[dict] = None
    ) -> AsyncGenerator[str, None]:
        """
        Standardized streaming execution.
        """
        system_prompt = _build_system_prompt(category, complexity_score)
        if system_prompt_override:
            system_prompt = f"{system_prompt_override}\n\n{system_prompt}"
            
        has_image = bool(image_b64 or image_url)

        try:
            # ── OpenAI-Compatible Streaming ────────────────────────────
            if provider in ["OpenAI", "NVIDIA", "xAI", "OpenRouter", "Together", "DeepSeek", "Mistral", "HuggingFace"]:
                client = self._get_hub_client(provider, api_keys)
                if not client:
                    yield "Error: Provider API key not configured."
                    return

                user_content = (
                    self._build_vision_content(prompt, image_b64, image_url)
                    if has_image else prompt
                )
                stream = client.chat.completions.create(
                    model=model_id,
                    messages=[
                        {"role": "system", "content": system_prompt},
                        {"role": "user",   "content": user_content},
                    ],
                    stream=True,
                    max_tokens=_get_max_tokens(complexity_score)
                )
                for chunk in stream:
                    delta = chunk.choices[0].delta.content
                    if delta:
                        yield delta

            # ── Anthropic Streaming ────────────────────────────────────
            elif provider == "Anthropic":
                try:
                    from anthropic import Anthropic
                    custom_anthropic = api_keys.get("anthropic") if api_keys else None
                    if custom_anthropic:
                        client = Anthropic(api_key=custom_anthropic)
                    else:
                        if not self.client_anthropic:
                            self.client_anthropic = Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))
                        client = self.client_anthropic

                    with client.messages.stream(
                        model=model_id,
                        max_tokens=_get_max_tokens(complexity_score),
                        system=system_prompt,
                        messages=[{"role": "user", "content": prompt}]
                    ) as stream:
                        for text in stream.text_stream:
                            yield text
                except ImportError:
                    yield "[ERROR] Anthropic SDK not installed."

            # ── Google Gemini Streaming ────────────────────────────────
            elif provider == "Google":
                custom_google = api_keys.get("gemini") if api_keys else None
                if custom_google:
                    client = genai.Client(api_key=custom_google)
                else:
                    if not self.client_google:
                        self.client_google = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))
                    client = self.client_google

                contents = prompt
                if has_image:
                    import base64
                    mime = _detect_mime_type(image_b64=image_b64, image_url=image_url)
                    if image_b64:
                        img_bytes = base64.b64decode(image_b64)
                        contents = [
                            genai_types.Part.from_bytes(data=img_bytes, mime_type=mime),
                            prompt,
                        ]

                # Gemma models do not support system_instruction in GenerateContentConfig
                is_gemma = "gemma" in model_id.lower()
                config_system_prompt = None if is_gemma else system_prompt
                
                if is_gemma and system_prompt:
                    if isinstance(contents, list):
                        contents.insert(0, f"System Instructions: {system_prompt}\n\n")
                    else:
                        contents = f"System Instructions: {system_prompt}\n\n{contents}"

                for chunk in client.models.generate_content_stream(
                    model=model_id,
                    contents=contents,
                    config=genai_types.GenerateContentConfig(
                        system_instruction=config_system_prompt,
                        max_output_tokens=_get_max_tokens(complexity_score),
                    )
                ):
                    if chunk.text:
                        yield chunk.text

            # ── Cohere Streaming ───────────────────────────────────────
            elif provider == "Cohere":
                try:
                    import cohere
                    if not self.client_cohere:
                        co_key = os.getenv("COHERE_API_KEY")
                        self.client_cohere = cohere.Client(co_key) if co_key else None
                    if self.client_cohere:
                        for event in self.client_cohere.chat_stream(
                            model=model_id,
                            preamble=system_prompt,
                            message=prompt,
                            max_tokens=_get_max_tokens(complexity_score)
                        ):
                            if hasattr(event, "text") and event.text:
                                yield event.text
                except ImportError:
                    yield "[ERROR] Cohere SDK not installed."

            else:
                yield f"[ERROR] Provider '{provider}' not configured."

        except Exception as e:
            yield f"[ERROR] Streaming failed [{provider}]: {str(e)}"


# ── Global singleton ───────────────────────────────────────────────────────
_dispatcher = None

def get_dispatcher() -> Dispatcher:
    global _dispatcher
    if _dispatcher is None:
        _dispatcher = Dispatcher()
    return _dispatcher


dispatcher = Dispatcher()
