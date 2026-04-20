"""
Database wrapper for model fetching.
Uses SQLAlchemy ORM instead of raw psycopg2.
"""

import os
import importlib.util

# Handle database module import (naming conflict with database/ directory)
def _load_database_module():
    spec = importlib.util.spec_from_file_location("root_database", 
        os.path.join(os.path.dirname(os.path.dirname(__file__)), "database.py"))
    root_database = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(root_database)
    return root_database

root_database = _load_database_module()
SessionLocal = root_database.SessionLocal

from app.models import AIModel


def fetch_models():
    """
    Fetch all active models from database.
    
    Returns list of dicts with keys:
    - name: model_id
    - category: model category
    - tier: 1, 2, or 3
    - complexity_min: minimum complexity score
    - complexity_max: maximum complexity score
    - cost: cost_per_1m_tokens
    - active: is_active boolean
    """
    db = SessionLocal()
    
    try:
        models_query = db.query(AIModel).filter(
            AIModel.is_active == True
        ).all()
        
        models = []
        for m in models_query:
            models.append({
                "name": m.model_id,
                "category": m.category,
                "tier": m.tier,
                "complexity_min": m.complexity_min,
                "complexity_max": m.complexity_max,
                "cost": m.cost_per_1m_tokens,
                "active": m.is_active,
                "provider": m.provider,
                "sub_tier": m.sub_tier
            })
        
        return models
    
    finally:
        db.close()
