# Applied Features — AI Router v1.1

## Features Implemented in This Session

### Feature 1: Streaming Responses (`/ask/stream`)
New endpoint: `POST /ask/stream`
Returns tokens word-by-word via Server-Sent Events (SSE) instead of waiting 30+ seconds.

**New files:** `core/dispatcher.py` — added `execute_stream()` async generator for Google, Anthropic, OpenAI, Cohere
**Modified:** `app/main.py` — added `/ask/stream` endpoint with `StreamingResponse`

How to use:
```
POST /ask/stream
{ "user_id": "alice", "prompt": "Write a Python sort algorithm" }
```

---

### Feature 2: Conversation History / Multi-Turn Memory
New fields in QueryRequest:
- `session_id` — links messages in a conversation
- `max_history_turns` — how many past turns to include (default 5)

Previous turns are fetched from PostgreSQL and prepended to the prompt before routing.

**Modified:** `app/main.py`, `app/vault_service.py`, `app/models.py`
**Database:** `user_conversations.session_id` column added

How to use:
```
{ "user_id": "alice", "prompt": "make it faster", "session_id": "chat-001" }
```

---

### Feature 6: Multi-Modal Input (Image + Text)
New fields in QueryRequest:
- `image_base64` — Base64-encoded image (ore photo, screenshot, code screenshot)
- `image_url` — Or a public image URL

When an image is provided, it is forwarded to vision-capable models (Gemini Vision, GPT-4V, Claude 3.x).

**Modified:** `app/main.py`, `app/vault_service.py`, `core/dispatcher.py`
**Database:** `user_conversations.has_image` column added

How to use:
```
{ "user_id": "miner", "prompt": "Classify this ore type", "image_base64": "<base64string>" }
```

---

### Feature 7: Guardrails (Content Safety Layer)
New file: `app/guardrails.py`

Runs before Phase 1 on every request. Checks for:
- Prompt injection (ignore instructions, jailbreak, developer mode, DAN mode)
- PII redaction (email, Indian/international phone, credit cards, Aadhaar, PAN, SSN)
- Blocked harmful keywords (bomb-making, malware, etc.)
- Extreme length warnings (over 100,000 characters)

Blocked requests return HTTP 400. PII is auto-redacted silently.

**Modified:** `app/main.py` — GuardrailsChecker wired before Phase 1 in both /ask and /ask/stream

---

### Feature 12: Persistent User Memory
New file: `app/memory_service.py`
New database table: `user_memory`

After every AI response (Phase 5), key facts about the user are automatically extracted
and stored. On the next request, the top memories are prepended to the prompt.

New admin endpoints:
- GET /memory/{user_id} — view all memories
- DELETE /memory/{user_id} — clear all memories
- DELETE /memory/{user_id}/{memory_id} — delete a specific memory

**Modified:** `app/main.py`, `app/vault_service.py`, `app/models.py`

---

### Feature 13: Operator-Level System Prompt
Configuration: `.env` file

Set OPERATOR_SYSTEM_PROMPT in your .env to globally customize all responses.
It is prepended to every category system prompt before being sent to any AI model.

**Modified:** `core/dispatcher.py` — _build_system_prompt() reads OPERATOR_SYSTEM_PROMPT
**Modified:** `.env` — OPERATOR_SYSTEM_PROMPT= variable added

How to use:
```
OPERATOR_SYSTEM_PROMPT=You are an assistant specialized in mining and ore detection.
```

---

### Performance & Stability Enhancements
To ensure production reliability, two critical stability fixes were applied:

1. **Lazy Model Loading:** The 440MB BGE embedding model is now lazy-loaded on the first `/ask` request. This prevents the server from freezing for 30-60 seconds on every restart, allowing `/health` to respond instantly.
2. **Background Librarian:** The auto-discovery librarian (which makes synchronous network calls) now runs in a background thread via `asyncio.to_thread()`. This prevents the FastAPI event loop from being blocked during startup.

---


| File                    | Purpose                                              |
|-------------------------|------------------------------------------------------|
| app/guardrails.py       | Content safety: injection + PII + keyword blocking   |
| app/memory_service.py   | User memory extraction, storage, and retrieval       |

## Summary of Modified Files

| File                  | Changes                                                        |
|-----------------------|----------------------------------------------------------------|
| core/dispatcher.py    | Streaming, multi-modal vision, operator prompt                 |
| app/main.py           | All 6 features wired + /ask/stream + memory endpoints          |
| app/vault_service.py  | session_id + image params through execution and storage        |
| app/models.py         | session_id, has_image on UserConversation; UserMemory table    |
| .env                  | OPERATOR_SYSTEM_PROMPT variable                                |

## New API Endpoints

| Endpoint                     | Method | Feature         |
|------------------------------|--------|-----------------|
| /ask/stream                  | POST   | Streaming SSE   |
| /memory/{user_id}            | GET    | View memories   |
| /memory/{user_id}            | DELETE | Clear memories  |
| /memory/{user_id}/{id}       | DELETE | Delete one      |
