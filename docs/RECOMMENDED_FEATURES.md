# Recommended Features — AI Router (Not Yet Applied)

These features are recommended for the next development phase.
They are ordered by priority and impact.

---

## HIGH PRIORITY

### Feature 3: User Authentication (JWT / API Keys)
**What:** Users authenticate with a JWT token or API key like `sk-router-xyz123`
instead of passing a plain `user_id: "string"`.

**Why:** Currently anyone can claim to be any user_id. There is zero security.

**What to build:**
- New `api_keys` database table
- POST /auth/register and POST /auth/login endpoints
- FastAPI Depends(verify_api_key) middleware on all protected routes
- Each API key linked to a user, tier, and budget limit

**Effort:** 4-5 hours | **Impact:** Critical for production

---

### Feature 4: Per-User Budget Controls
**What:** Each user has a monthly spending cap (e.g., $5.00 USD).
When they hit it, requests return HTTP 402 instead of burning API credits.

**What to build:**
- New `user_budgets` table (user_id, monthly_limit_usd, current_month_spend, reset_date)
- Check budget before Phase 3 (execution)
- Update spend after each successful request

**Effort:** 2-3 hours | **Impact:** Prevents runaway costs in production

---

### Feature 5: Real-Time Analytics Dashboard
**What:** Web page or API endpoints showing:
- Requests/hour, cost/day, model usage %, cache hit rate, avg latency

**New endpoints to add:**
- GET /admin/analytics/overview — total cost, requests, cache hits today
- GET /admin/analytics/models — which model was used how many times
- GET /admin/analytics/users — top users by cost/requests
- GET /admin/analytics/cache — cache hit rate over time
- GET /admin/analytics/latency — P50/P95/P99 latency by model

**Effort:** 5-6 hours | **Impact:** Essential for understanding production usage

---

## MEDIUM PRIORITY

### Feature 8: Model Pinning and User Preferences
**What:** Users can say "always use Claude for my requests" or "never use Google".

**New fields in QueryRequest:**
- `preferred_model` — e.g., "claude-3-5-sonnet"
- `preferred_provider` — e.g., "Anthropic"
- `excluded_providers` — e.g., ["Google", "OpenAI"]

**Effort:** 1-2 hours | **Impact:** High for enterprise / white-label use

---

### Feature 9: Prompt Templates Library
**What:** Users can save and reuse prompt templates like Custom GPTs in ChatGPT.

**New endpoints:**
- POST /templates/save — { name, template, variables }
- GET /templates/list/{user_id}
- POST /ask/template — { template_id, variables }

**Effort:** 2-3 hours | **Impact:** Medium — good for power users

---

### Feature 10: Model Comparison Mode (Arena)
**What:** Send the same prompt to 2-3 models in parallel and return all responses.
This is the "arena" feature of Chatbot Arena.

**New endpoint:**
- POST /ask/compare — { user_id, prompt, models: [model1, model2, model3] }

**Effort:** 3-4 hours | **Impact:** Unique differentiator vs OpenRouter

---

### Feature 11: Webhook / Async Mode
**What:** For long-running requests (30+ seconds), return a job_id immediately.
Process in background. Call a webhook URL when done.

**New fields:**
- `webhook_url` in QueryRequest — if set, respond immediately with job_id
- Background task in FastAPI processes the request
- POST to webhook_url when complete

**Effort:** 3-4 hours | **Impact:** Medium — good for agent pipelines

---

## LOWER PRIORITY / FUTURE

### JWT Auth on /ask/stream (Streaming + Auth)
**What:** The /ask/stream endpoint currently has no authentication.
After Feature 3 (JWT) is implemented, it needs to be wired into the streaming endpoint as well.
**Effort:** 30 minutes after Feature 3 is done

---

### Redis L2 Cache (Speed Improvement)
**What:** Add Redis as a fast L2 cache between the user and PostgreSQL.
Currently disabled (PostgreSQL is the only cache layer).
Reduces latency from ~50ms to ~2ms for cache hits.
**Effort:** 2-3 hours | **Requires:** Redis server setup

---

### Streaming Memory Save (Feature 1 + 12 Integration)
**What:** The /ask/stream endpoint currently does NOT save the streamed response
to the vault or extract memories (since the response is streamed, not collected).
Add a background task to save after stream completes.
**Effort:** 1-2 hours

---

### Fine-Tuned ModernBERT Router
**What:** Replace the current DeBERTa classifier with a fine-tuned ModernBERT model
that has an 8192-token context window (vs. 512 tokens in DeBERTa).
This would fix the "intent at end of long prompt" problem natively in the NLP model.
**Effort:** Requires Colab training (COLAB_DEBERTA_TRAINING.md already exists)
**Requires:** GPU for training, then export to CPU for inference

---

### Rate Limiting per Tier
**What:** Currently all users get the same 30 req/min limit regardless of tier.
Tier 1 (Premium) users should get 100 req/min.
Tier 3 (Budget) users should get 10 req/min.
**Effort:** 30 minutes

---

## EMBEDDING MODEL UPGRADE PATH

When deploying to GPU server, upgrade the embedding model from:
- Current: `jinaai/jina-embeddings-v2-base-en` (768 dims, CPU)
- Target:  `Alibaba-NLP/gte-Qwen2-7B-instruct` (3584 dims, GPU)

NOTE: This requires:
1. Altering the PostgreSQL `embedding` column from Vector(768) to Vector(3584)
2. Regenerating all stored embeddings (old vectors will not be compatible)
3. Wiping the semantic cache (all old cache entries become invalid)
