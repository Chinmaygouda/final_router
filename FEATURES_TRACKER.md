# 🚀 Feature Tracker

This document logs all token optimization features implemented in the AI Router Pipeline v2.0 to ensure custom logic is preserved during future refactoring.

### Feature 1: Dynamic Complexity-Based System Prompts
- **Date:** 2026-05-02
- **Files Modified:** 
  - `core/dispatcher.py`
  - `app/vault_service.py`
  - `app/main.py`
- **Description:** Implemented dynamic system prompts that adjust verbosity based on the router's `complexity_score`. `LIGHT` prompts are used for easy queries (< 4.0), `HEAVY` prompts for complex queries (> 7.0), and `MEDIUM` for everything else. This provides the AI with a strict persona based on the task type (e.g., chat vs code) to prevent hallucinations and excessive generation.
- **Status:** ✅ Implemented

### Feature 2: Dynamic Max Output Tokens Limit ("Double Lock")
- **Date:** 2026-05-02
- **Files Modified:** 
  - `core/dispatcher.py`
  - `app/vault_service.py`
  - `app/main.py`
- **Description:** Implemented a `_get_max_tokens(complexity_score)` function to dynamically set the `max_tokens` API limit based on the DeBERTa complexity score. EASY tasks are capped at 500, MEDIUM at 2,000, and HARD at 8,192. This provides a hard ceiling on AI verbosity, protecting against runaway output generation.
- **Status:** ✅ Implemented
