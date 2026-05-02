# 🧠 AI Token Knowledge Base

### 1. How does an AI know when to stop?
Inside every AI model's brain, there is a special mathematical token called the **`<|STOP|>`** token (or End-of-Turn token).

1. **The Loop:** The AI generates tokens one by one.
2. **The Prediction:** For every new word, the AI also calculates the probability that the conversation should end.
3. **The Conclusion:** When the AI determines that the most "correct" next token is the `<|STOP|>` token, it predicts it.
4. **The Exit:** The API server detects this token, stops the generation, and sends you the full text.

### 2. What influences the response length?
The AI's "Stop" decision is influenced by:
- **User Prompt:** Simple questions reach the stop token faster.
- **System Prompt:** Instructions like "Be concise" increase the probability of a stop token appearing earlier.
- **Training Data:** Models like Gemini Flash are trained to be helpful and verbose, so they often delay the stop token to provide more detail.

### 3. The "Max Tokens" Ceiling (The Safety Wall)
The `max_tokens` parameter in the API call is a **hard physical limit**.
- If the AI predicts the `<|STOP|>` token **before** reaching this limit, you get a clean, finished response.
- If the AI reaches the `max_tokens` limit **before** predicting the `<|STOP|>` token, the API server kills the response mid-sentence.

### 4. Comparison: ChatGPT vs. Our Router
- **Native ChatGPT:** Uses a very high, fixed `max_tokens` (e.g., 4096).
- **Our Router:** We use a **Dynamic Ceiling**. We set a small limit for EASY tasks (to prevent yapping) and a high limit for HARD tasks (to allow for detail).
