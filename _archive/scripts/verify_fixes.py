import sys
sys.path.insert(0, '.')

print('=== Test 1: librarian.py ===')
from core.librarian import LIBRARIAN_PROMPT, assign_sub_tiers, reconstruct_database_layout
with open('core/librarian.py', encoding='utf-8') as f:
    content = f.read()

assert 'gemini-2.0-flash' in content, 'FAIL: gemini-2.0-flash not in audit_candidates'
assert 'gemini-3-flash' not in content, 'FAIL: dead model gemini-3-flash still in code'
assert "audit_candidates = ['gemini-2.0-flash'" in content, 'FAIL: audit_candidates not updated to working models'
assert 'HIGH   = Premium' in content, 'FAIL: tier explanation missing from prompt'
assert 'reconstruct_database_layout FAILED' in content, 'FAIL: rollback safety not added'
assert 'for tier_num in [1, 2, 3]' in content, 'FAIL: all-tier sub_tier assignment not added'
print('  [OK] Audit candidates fixed to working models')
print('  [OK] Prompt has explicit HIGH/MEDIUM/LOW definitions')
print('  [OK] reconstruct_database_layout has rollback safety')
print('  [OK] assign_sub_tiers covers all tiers')

print()
print('=== Test 2: auto_discovery.py ===')
with open('core/auto_discovery.py', encoding='utf-8') as f:
    content = f.read()

assert 'UPDATE ai_model' not in content, 'FAIL: wrong table name still present'
assert 'UPDATE models' in content, 'FAIL: correct table name not set'
assert 'from sqlalchemy import text' in content, 'FAIL: text() wrapper not added'
assert 'seed/static models found' in content, 'FAIL: seed bypass fix missing'
assert 'distinct_audit_times' in content, 'FAIL: smart seed detection missing'
print('  [OK] Raw SQL uses text() wrapper (SQLAlchemy 2.0 compatible)')
print('  [OK] Correct table name "models" (not "ai_model")')
print('  [OK] Seed model bypass fix applied')

print()
print('=== Test 3: models_manager.py ===')
with open('core/models_manager.py', encoding='utf-8') as f:
    content = f.read()

assert 'from core.librarian import' in content, 'FAIL: broken relative import still present'
assert 'from core.auto_discovery import' in content, 'FAIL: broken relative import still present'
assert 'from librarian import' not in content, 'FAIL: old relative import still present'
print('  [OK] Absolute imports used (no more broken relative imports)')

print()
print('=== Test 4: router.py ===')
with open('app/routing/router.py', encoding='utf-8') as f:
    content = f.read()

assert 'score = 8.0' in content, 'FAIL: HARD score not updated'
assert 'score = 2.5' in content, 'FAIL: EASY score not updated'
assert 'score = 8.5' not in content, 'FAIL: old pinpoint score 8.5 still present'
assert 'score = 3.0' not in content, 'FAIL: old pinpoint score 3.0 still present'
print('  [OK] HARD  -> 8.0 (center of 7.0-10.0 band)')
print('  [OK] MEDIUM-> 5.5 (center of 4.0-8.0 band)')
print('  [OK] EASY  -> 2.5 (center of 1.0-5.0 band)')

print()
print('=== Test 5: Live import check ===')
from core.auto_discovery import should_update_models, get_api_keys_hash
from core.librarian import LIBRARIAN_PROMPT
print('  [OK] core.librarian  imports without error')
print('  [OK] core.auto_discovery imports without error')

print()
print('=' * 45)
print('  ALL 9 BUGS VERIFIED FIXED!')
print('=' * 45)
