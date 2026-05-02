"""
Automated Test Matrix Benchmark
-------------------------------
Runs 6 configurations of (System Prompt Mode x Double Lock) 
across 3 Complexity Tiers (EASY, MEDIUM, HARD).
Total combinations: 54
"""

import asyncio
import time
import json
import os
import sys

# Add root directory to sys.path so we can import app modules
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from app.routing.router import get_best_model
from app.vault_service import VaultService
from core.dispatcher import GLOBAL_CONFIG

PROMPTS = {
    "EASY": [
        "hi how are you",
        "what time is it",
        "tell me a joke"
    ],
    "MEDIUM": [
        "Write a python script to parse a CSV file and convert it to JSON.",
        "Explain the difference between REST and GraphQL APIs.",
        "How does Python's asyncio event loop work?"
    ],
    "HARD": [
        "Design and implement a distributed rate limiter system in Python that supports multiple algorithms (Token Bucket, Sliding Window), works across multiple server instances using Redis, and handles race conditions.",
        "Build a complete multi-agent pipeline using LangChain where an Architect agent plans a codebase and a Coder agent implements it, including memory and tool usage.",
        "Design a full-stack microservices architecture for a real-time stock trading app with high availability and low latency, including the message queue, database schema, and Kubernetes deployment strategy."
    ]
}

CONFIGS = [
    {"sys_mode": "1.1", "lock": True,  "desc": "[1.1, 2.1] Single Prompt + Lock ON"},
    {"sys_mode": "1.1", "lock": False, "desc": "[1.1, 2.2] Single Prompt + Lock OFF"},
    {"sys_mode": "1.2", "lock": True,  "desc": "[1.2, 2.1] Detailed Prompt + Lock ON"},
    {"sys_mode": "1.2", "lock": False, "desc": "[1.2, 2.2] Detailed Prompt + Lock OFF"},
    {"sys_mode": "1.3", "lock": True,  "desc": "[1.3, 2.1] Category-Aware + Lock ON"},
    {"sys_mode": "1.3", "lock": False, "desc": "[1.3, 2.2] Category-Aware + Lock OFF"},
]

async def run_benchmark():
    print("=" * 80)
    print("AUTOMATED TEST MATRIX INITIATED")
    print("=" * 80)
    print("Testing 6 Configurations across 3 Complexity Tiers (9 prompts total).")
    print("This will make 54 API calls and may take 5-10 minutes. Please wait...\n")

    results = []

    for cfg in CONFIGS:
        # Update dynamic config in dispatcher.py
        GLOBAL_CONFIG.system_prompt_mode = cfg["sys_mode"]
        GLOBAL_CONFIG.double_lock_enabled = cfg["lock"]
        print(f"\nRunning Configuration: {cfg['desc']}")
        print("-" * 60)

        for tier, prompts in PROMPTS.items():
            for i, prompt in enumerate(prompts):
                # 1. Routing Phase
                model_id, provider, score, category, user_tier, fallbacks = get_best_model(prompt, user_allowed_tier=1)
                
                # 2. Execution Phase
                start_time = time.time()
                try:
                    response_data = VaultService.execute_with_provider(
                        provider, model_id, prompt, category=category, complexity_score=score
                    )
                    latency = time.time() - start_time
                    tokens = response_data.get("tokens", 0)
                    text = response_data.get("text", "")
                    word_count = len(text.split())
                    success = response_data.get("success", False)
                except Exception as e:
                    latency = time.time() - start_time
                    tokens = 0
                    word_count = 0
                    success = False
                    text = str(e)

                # Record Result
                record = {
                    "config": cfg["desc"],
                    "expected_tier": tier,
                    "deberta_score": score,
                    "tokens": tokens,
                    "words": word_count,
                    "latency": round(latency, 2),
                    "success": success,
                    "prompt_preview": prompt[:30] + "..."
                }
                results.append(record)
                status = "SUCCESS" if success else "FAILED"
                print(f"  {status} {tier:<6} | Score: {score:<3} | Tokens: {tokens:<5} | Words: {word_count:<4} | Latency: {latency:.1f}s | {prompt[:30]}...")

    # Write results to Markdown Artifact
    artifact_path = os.path.join(os.path.dirname(__file__), "..", "test_matrix_results.md")
    with open(artifact_path, "w", encoding="utf-8") as f:
        f.write("# 🧪 Automated Test Matrix Results\n\n")
        f.write("This table proves the token and quality differences across all configurations.\n\n")
        f.write("| Configuration | Tier | DeBERTa Score | Tokens Consumed | Words Generated | Latency (s) | Prompt Preview |\n")
        f.write("|---------------|------|---------------|-----------------|-----------------|-------------|----------------|\n")
        for r in results:
            f.write(f"| {r['config']} | {r['expected_tier']} | {r['deberta_score']} | **{r['tokens']}** | {r['words']} | {r['latency']}s | `{r['prompt_preview']}` |\n")
    print(f"\nBenchmark Complete! Results saved to {artifact_path}")

if __name__ == "__main__":
    asyncio.run(run_benchmark())
