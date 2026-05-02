# 🧪 Automated Test Matrix Results

This table proves the token and quality differences across all configurations.

| Configuration | Tier | DeBERTa Score | Tokens Consumed | Words Generated | Latency (s) | Prompt Preview |
|---------------|------|---------------|-----------------|-----------------|-------------|----------------|
| [1.1, 2.1] Single Prompt + Lock ON | EASY | 2.5 | **0** | 18 | 1.04s | `hi how are you...` |
| [1.1, 2.1] Single Prompt + Lock ON | EASY | 2.5 | **0** | 18 | 1.32s | `what time is it...` |
| [1.1, 2.1] Single Prompt + Lock ON | EASY | 2.5 | **0** | 18 | 0.8s | `tell me a joke...` |
| [1.1, 2.1] Single Prompt + Lock ON | MEDIUM | 5.5 | **0** | 136 | 0.72s | `Write a python script to parse...` |
| [1.1, 2.1] Single Prompt + Lock ON | MEDIUM | 2.5 | **521** | 11 | 3.94s | `Explain the difference between...` |
| [1.1, 2.1] Single Prompt + Lock ON | MEDIUM | 5.5 | **0** | 118 | 0.83s | `How does Python's asyncio even...` |
| [1.1, 2.1] Single Prompt + Lock ON | HARD | 8.0 | **0** | 136 | 0.66s | `Design and implement a distrib...` |
| [1.1, 2.1] Single Prompt + Lock ON | HARD | 5.5 | **0** | 6 | 0.02s | `Build a complete multi-agent p...` |
| [1.1, 2.1] Single Prompt + Lock ON | HARD | 8.0 | **0** | 136 | 0.85s | `Design a full-stack microservi...` |
| [1.1, 2.2] Single Prompt + Lock OFF | EASY | 2.5 | **0** | 18 | 0.91s | `hi how are you...` |
| [1.1, 2.2] Single Prompt + Lock OFF | EASY | 2.5 | **0** | 18 | 0.74s | `what time is it...` |
| [1.1, 2.2] Single Prompt + Lock OFF | EASY | 2.5 | **0** | 18 | 0.73s | `tell me a joke...` |
| [1.1, 2.2] Single Prompt + Lock OFF | MEDIUM | 5.5 | **0** | 33 | 0.93s | `Write a python script to parse...` |
| [1.1, 2.2] Single Prompt + Lock OFF | MEDIUM | 2.5 | **1095** | 296 | 7.2s | `Explain the difference between...` |
| [1.1, 2.2] Single Prompt + Lock OFF | MEDIUM | 5.5 | **0** | 118 | 1.54s | `How does Python's asyncio even...` |
| [1.1, 2.2] Single Prompt + Lock OFF | HARD | 8.0 | **0** | 136 | 1.0s | `Design and implement a distrib...` |
| [1.1, 2.2] Single Prompt + Lock OFF | HARD | 5.5 | **0** | 6 | 0.0s | `Build a complete multi-agent p...` |
| [1.1, 2.2] Single Prompt + Lock OFF | HARD | 8.0 | **0** | 118 | 0.82s | `Design a full-stack microservi...` |
| [1.2, 2.1] Detailed Prompt + Lock ON | EASY | 2.5 | **0** | 18 | 0.77s | `hi how are you...` |
| [1.2, 2.1] Detailed Prompt + Lock ON | EASY | 2.5 | **0** | 18 | 1.03s | `what time is it...` |
| [1.2, 2.1] Detailed Prompt + Lock ON | EASY | 2.5 | **0** | 18 | 0.97s | `tell me a joke...` |
| [1.2, 2.1] Detailed Prompt + Lock ON | MEDIUM | 5.5 | **0** | 136 | 0.99s | `Write a python script to parse...` |
| [1.2, 2.1] Detailed Prompt + Lock ON | MEDIUM | 2.5 | **557** | 16 | 4.1s | `Explain the difference between...` |
| [1.2, 2.1] Detailed Prompt + Lock ON | MEDIUM | 5.5 | **0** | 84 | 0.81s | `How does Python's asyncio even...` |
| [1.2, 2.1] Detailed Prompt + Lock ON | HARD | 8.0 | **0** | 118 | 0.96s | `Design and implement a distrib...` |
| [1.2, 2.1] Detailed Prompt + Lock ON | HARD | 5.5 | **0** | 6 | 0.0s | `Build a complete multi-agent p...` |
| [1.2, 2.1] Detailed Prompt + Lock ON | HARD | 8.0 | **0** | 136 | 0.62s | `Design a full-stack microservi...` |
| [1.2, 2.2] Detailed Prompt + Lock OFF | EASY | 2.5 | **0** | 18 | 1.75s | `hi how are you...` |
| [1.2, 2.2] Detailed Prompt + Lock OFF | EASY | 2.5 | **0** | 18 | 2.15s | `what time is it...` |
| [1.2, 2.2] Detailed Prompt + Lock OFF | EASY | 2.5 | **0** | 18 | 1.37s | `tell me a joke...` |
| [1.2, 2.2] Detailed Prompt + Lock OFF | MEDIUM | 5.5 | **0** | 136 | 0.72s | `Write a python script to parse...` |
| [1.2, 2.2] Detailed Prompt + Lock OFF | MEDIUM | 2.5 | **0** | 84 | 1.06s | `Explain the difference between...` |
| [1.2, 2.2] Detailed Prompt + Lock OFF | MEDIUM | 5.5 | **0** | 28 | 13.83s | `How does Python's asyncio even...` |
| [1.2, 2.2] Detailed Prompt + Lock OFF | HARD | 8.0 | **0** | 136 | 0.71s | `Design and implement a distrib...` |
| [1.2, 2.2] Detailed Prompt + Lock OFF | HARD | 5.5 | **0** | 6 | 0.0s | `Build a complete multi-agent p...` |
| [1.2, 2.2] Detailed Prompt + Lock OFF | HARD | 8.0 | **0** | 136 | 0.61s | `Design a full-stack microservi...` |
| [1.3, 2.1] Category-Aware + Lock ON | EASY | 2.5 | **0** | 18 | 1.05s | `hi how are you...` |
| [1.3, 2.1] Category-Aware + Lock ON | EASY | 2.5 | **0** | 18 | 1.3s | `what time is it...` |
| [1.3, 2.1] Category-Aware + Lock ON | EASY | 2.5 | **0** | 18 | 1.38s | `tell me a joke...` |
| [1.3, 2.1] Category-Aware + Lock ON | MEDIUM | 5.5 | **0** | 136 | 0.61s | `Write a python script to parse...` |
| [1.3, 2.1] Category-Aware + Lock ON | MEDIUM | 2.5 | **0** | 84 | 1.32s | `Explain the difference between...` |
| [1.3, 2.1] Category-Aware + Lock ON | MEDIUM | 5.5 | **0** | 28 | 9.42s | `How does Python's asyncio even...` |
| [1.3, 2.1] Category-Aware + Lock ON | HARD | 8.0 | **0** | 136 | 1.6s | `Design and implement a distrib...` |
| [1.3, 2.1] Category-Aware + Lock ON | HARD | 5.5 | **0** | 6 | 0.0s | `Build a complete multi-agent p...` |
| [1.3, 2.1] Category-Aware + Lock ON | HARD | 8.0 | **0** | 136 | 1.13s | `Design a full-stack microservi...` |
| [1.3, 2.2] Category-Aware + Lock OFF | EASY | 2.5 | **0** | 18 | 1.72s | `hi how are you...` |
| [1.3, 2.2] Category-Aware + Lock OFF | EASY | 2.5 | **0** | 18 | 1.03s | `what time is it...` |
| [1.3, 2.2] Category-Aware + Lock OFF | EASY | 2.5 | **0** | 18 | 1.23s | `tell me a joke...` |
| [1.3, 2.2] Category-Aware + Lock OFF | MEDIUM | 5.5 | **0** | 136 | 0.63s | `Write a python script to parse...` |
| [1.3, 2.2] Category-Aware + Lock OFF | MEDIUM | 2.5 | **0** | 84 | 1.21s | `Explain the difference between...` |
| [1.3, 2.2] Category-Aware + Lock OFF | MEDIUM | 5.5 | **0** | 84 | 1.34s | `How does Python's asyncio even...` |
| [1.3, 2.2] Category-Aware + Lock OFF | HARD | 8.0 | **0** | 136 | 0.82s | `Design and implement a distrib...` |
| [1.3, 2.2] Category-Aware + Lock OFF | HARD | 5.5 | **0** | 6 | 0.0s | `Build a complete multi-agent p...` |
| [1.3, 2.2] Category-Aware + Lock OFF | HARD | 8.0 | **0** | 118 | 0.62s | `Design a full-stack microservi...` |
