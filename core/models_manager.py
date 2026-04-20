#!/usr/bin/env python3
"""
Automated Models Table Updater
Automatically discovers, categorizes, and updates the models table without manual intervention.
Run with: python models_manager.py
"""

import sys
sys.path.insert(0, '.')

from app.database_init import SessionLocal
from app.models import AIModel
from librarian import audit_models
from auto_discovery import run_30_day_refresh
from sqlalchemy import desc
from datetime import datetime

db = SessionLocal()

def auto_update_models():
    """Automatically discover, categorize, and update all models in the database."""
    print("\n" + "="*80)
    print("🚀 AUTOMATED MODELS TABLE UPDATE")
    print("="*80)
    
    try:
        # Run the complete discovery and categorization workflow
        print("\n📚 Running Auto-Discovery & Categorization...")
        run_30_day_refresh()
        
        print("\n✅ MODELS UPDATE COMPLETE!")
        print_summary()
        
    except Exception as e:
        print(f"\n❌ ERROR during update: {e}")
        import traceback
        traceback.print_exc()

def print_summary():
    """Print summary statistics after update."""
    print("\n" + "="*80)
    print("📊 UPDATED MODELS SUMMARY")
    print("="*80)
    
    total = db.query(AIModel).filter(~AIModel.model_id.startswith("---")).count()
    active = db.query(AIModel).filter(AIModel.is_active == True, ~AIModel.model_id.startswith("---")).count()
    
    print(f"Total Models:          {total}")
    print(f"Active Models:         {active}")
    
    # Stats by tier
    print(f"\nBy Tier:")
    for tier in [1, 2, 3]:
        count = db.query(AIModel).filter(
            AIModel.tier == tier, 
            AIModel.is_active == True,
            ~AIModel.model_id.startswith("---")
        ).count()
        tier_name = ["", "Premium (Tier 1)", "Standard (Tier 2)", "Budget (Tier 3)"][tier]
        print(f"  {tier_name:<30} {count:>5}")
    
    # Stats by category
    print(f"\nBy Category:")
    from collections import defaultdict
    categories = defaultdict(int)
    for m in db.query(AIModel).filter(AIModel.is_active == True, ~AIModel.model_id.startswith("---")).all():
        categories[m.category] += 1
    
    for cat in sorted(categories.keys()):
        print(f"  {cat:<30} {categories[cat]:>5}")
    
    # Stats by provider
    print(f"\nBy Provider:")
    providers = defaultdict(int)
    for m in db.query(AIModel).filter(AIModel.is_active == True, ~AIModel.model_id.startswith("---")).all():
        providers[m.provider] += 1
    
    for prov in sorted(providers.keys()):
        print(f"  {prov:<30} {providers[prov]:>5}")
    
    print("="*80 + "\n")

if __name__ == "__main__":
    try:
        auto_update_models()
    except KeyboardInterrupt:
        print("\n⚠️  Update interrupted by user")
    except Exception as e:
        print(f"\n❌ CRITICAL ERROR: {e}")
        import traceback
        traceback.print_exc()
    finally:
        db.close()
        print("✅ Database connection closed")
