# AI Router Feature Documentation

*Last Updated & Features Implemented: April 24, 2026*

This document provides a detailed explanation of all active features in the AI Router Pipeline V2.0, along with a list of recommended features for future iterations.

## 1. Local DeBERTa-v3 Intent Classification
**Implemented:** April 2026
**Description:** Instead of making expensive LLM calls to classify user intent, the router uses a local, fine-tuned `DeBERTa-v3-base` model. It accurately categorizes prompts into domains such as `CODE`, `AGENTS`, `ANALYSIS`, `EXTRACTION`, `CREATIVE`, `CHAT`, and `UTILITY`.
**Benefit:** 0ms API latency, zero cost, absolute privacy for the routing layer.

## 2. Prompt Compression
**Implemented:** April 2026
**Description:** A local pipeline that removes stop words, excessive whitespace, and non-semantic noise from the user's prompt before it reaches the router or the AI provider. It preserves the conversation context and memory context explicitly.
**Benefit:** Reduces token usage by up to 30-50%, drastically cutting inference costs.

## 3. Semantic Vault Caching
**Implemented:** April 2026
**Description:** Utilizes PostgreSQL with the `pgvector` extension. Every request and response is embedded. Before calling an LLM, the system checks the vault for an existing response with high cosine similarity (L2 distance) and exact keyword overlap.
**Benefit:** Eliminates redundant API calls, provides instant (cache hit) responses, and prevents hallucination looping by ensuring caching rules are strict.

## 4. Multi-Turn Conversation History
**Implemented:** April 2026
**Description:** Conversations are tracked using `session_id`. The router fetches up to `N` (configurable) past turns for that session, appending them to the prompt context.
**Benefit:** Users can ask follow-up questions without losing context.

## 5. Multi-Modal Vision Integration
**Implemented:** April 2026
**Description:** Seamlessly supports base64 image strings or public image URLs. The `Dispatcher` handles mapping these to the appropriate multi-modal provider APIs (Google Gemini, Claude 3.5, GPT-4o).
**Benefit:** Users can send images for OCR or visual analysis effortlessly.

## 6. Guardrails & PII Redaction
**Implemented:** April 24, 2026
**Description:** Evaluates prompts *before* routing. It uses regex patterns to redact PII (Emails, Phones, SSN, Aadhaar, PAN) and blocks common prompt injection patterns (`ignore previous instructions`, `DAN mode`).
**Benefit:** Enforces strong security compliance and protects sensitive user data without needing an LLM.

## 7. Persistent User Memory
**Implemented:** April 2026
**Description:** Using heuristic and regex patterns, the system automatically extracts facts, preferences, and identity statements from the user's input. These are saved in PostgreSQL and injected as context into future prompts.
**Benefit:** The AI "remembers" the user across different sessions and devices.

## 8. Cascading Fallback & Circuit Breaking
**Implemented:** April 24, 2026
**Description:** If a model fails or rate-limits, the system falls back to other models in the same category. If those fail, it queries the DB for cross-category text models, and finally defaults to guaranteed hardcoded models.
**Benefit:** Near 100% uptime and resilience against provider outages.

## 9. Operator System Prompt
**Implemented:** April 2026
**Description:** Developers can set an `OPERATOR_SYSTEM_PROMPT` in the `.env` file. This is prepended to the category-specific system prompt, strictly specializing the behavior of all downstream LLMs.
**Benefit:** Easily pivot the router into a domain-specific expert (e.g., medical bot, coding assistant) without changing the codebase.

## 10. Thompson Sampling Bandit
**Implemented:** April 2026
**Description:** When multiple models tie in score, the router uses Thompson Sampling to select a model based on historical success/failure rates, continually optimizing selection based on real-world feedback.
**Benefit:** The system genuinely learns over time which models perform best for specific tasks.

---

## 🚀 Recommended Features (Future Roadmap)

1. **Authentication Middleware (JWT/OAuth2):**
   * Currently, the system relies on user-provided `user_id` strings. Integrating a real auth system will secure the endpoints.
2. **Cost Budget Caps:**
   * Enforce hard limits on `cost_per_1m_tokens` consumed per `user_id` to prevent abuse.
3. **Admin UI Dashboard:**
   * A web interface (React/Vite or FastAPI templates) to view routing metrics, edit memory, and manage model tiers without touching the database.
4. **LLM-Based Guardrails (Secondary Tier):**
   * Regex-based guardrails are fast but rigid. Implement a lightweight local LLM (e.g., Llama-3-8B) as an optional deep-inspection layer for high-risk prompts.
5. **Redis Fallback Cache:**
   * Currently, Redis is disabled in favor of PostgreSQL. Re-enabling Redis for pure exact-match string caching will reduce DB load for exact duplicate queries.
