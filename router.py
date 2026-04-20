
#FROZEN CODE - DO NOT MODIFY


from google import genai
import os
from database import SessionLocal
from app.models import AIModel
from sqlalchemy import and_, desc

client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))

# MODIFICATION: Added your specific checks (CoT, Logic, Length) to the prompt
ROUTER_PROMPT = """
Analyze the user's prompt and determine:
1. Complexity score (1.0 to 10.0).
2. Intent Category. Choose the MOST specific one from: [CODE, AGENTS, ANALYSIS, EXTRACTION, CREATIVE, UTILITY, CHAT].
   - Priority: If it involves code, choose CODE. If it involves data/logic, choose ANALYSIS.
3. Needs_CoT (True/False): Does this require complex reasoning or Chain of Thought?
4. Logical_Necessity (True/False): Is a high-tier model absolutely required to prevent failure?
5. Is_Long_Output (True/False): Does the user need a massive output?

Return ONLY comma-separated values matching this format:
score, category, needs_cot, logical_necessity, is_long_output
Example: 8.5, CODE, True, False, True
"""

def get_best_model(user_prompt, user_allowed_tier):
    # --- STEP 1: MACRO-ROUTING (The Gatekeeper) ---
    analysis = client.models.generate_content(
        model='gemini-2.5-flash',
        contents=f"{ROUTER_PROMPT}\n\nUser Prompt: {user_prompt}"
    )
    
    try:
        parts = [p.strip() for p in analysis.text.strip().split(',')]
        score = float(parts[0])
        category = parts[1].upper()
        needs_cot = parts[2].lower() == 'true'
        logical_necessity = parts[3].lower() == 'true'
        is_long = parts[4].lower() == 'true'
    except Exception as e:
        # Fallback if parsing fails
        score, category, needs_cot, logical_necessity, is_long = 5.0, "UTILITY", False, False, False

    # --- STEP 2: LAZY ROUTING FILTER (Bias for cheaper tiers) ---
    effective_tier = user_allowed_tier
    
    if user_allowed_tier == 1:
        # Only stay in Tier 1 if there's Logical Necessity or high complexity
        if not logical_necessity and score < 8.0:
            effective_tier = 2 
            
    if score < 4.0 and not is_long:
        effective_tier = 3 # Extreme lazy routing for simple tasks

    # --- STEP 3: MICRO-ROUTING (Model Selection) ---
    db = SessionLocal()
    selected_model = None
    tiers_to_check = [t for t in [1, 2, 3] if t >= effective_tier]

    for tier_to_try in tiers_to_check:
        base_filters = [
             AIModel.tier == tier_to_try, 
             AIModel.is_active == True,  # This will now block the "---" spacer rows
             ~AIModel.model_id.startswith("---") # Change this line to catch all spacer variants
        ]
        
        # --- THE SAFETY BUFFER (Intra-Tier 1 Logic) ---
        if tier_to_try == 1:
            # Unlock Tier 1-A ONLY if the prompt passed the Chain of Thought test or is extremely complex
            if not needs_cot and score < 9.5:
                base_filters.append(AIModel.sub_tier == 'B') # Force Tier 1-B (Cheaper Architects)

        # PHASE A: Exact Category & Complexity Match
        selected_model = db.query(AIModel).filter(
            and_(*base_filters, AIModel.category == category, AIModel.complexity_min <= score)
        ).order_by(desc(AIModel.complexity_min)).first()

        # PHASE B: Cross-Category Fallback
        if not selected_model:
            selected_model = db.query(AIModel).filter(
                and_(*base_filters, AIModel.complexity_min <= score)
            ).order_by(desc(AIModel.complexity_min)).first()

        # PHASE C: Last Resort (Simplest model in this tier)
        if not selected_model:
            selected_model = db.query(AIModel).filter(and_(*base_filters)).order_by(AIModel.complexity_min.asc()).first()
            
        if selected_model:
            break

    db.close()

    if not selected_model:
        return "gemini-2.5-flash", "Google", score, category, 2
        
    return (selected_model.model_id, selected_model.provider, score, category, selected_model.tier)