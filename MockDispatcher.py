#FROZEN CODE - DO NOT MODIFY

import random

class MockDispatcher:
    """Simulates an AI provider for testing memory and routing."""
    
    def execute(self, provider: str, model: str, payload: str):
        # 1. Simulate token usage
        tokens = random.randint(150, 450)
        
        # 2. Extract some info from the payload to prove memory works
        # This helps you see if the 'SUMMARY' or 'HISTORY' is actually being sent
        has_summary = "SUMMARY: " in payload and "None" not in payload
        has_history = "RECENT_HISTORY: [" in payload and "[]" not in payload
        
        mock_response = (
            f"[MOCK RESPONSE from {model}]\n"
            f"I see you're using {provider}. "
            f"Memory Check: Summary Present? {has_summary} | History Present? {has_history}.\n"
            f"Your input was: {payload[-50:]}..." # Show the end of the payload
        )
        
        return {
            "text": mock_response,
            "tokens": tokens
        }