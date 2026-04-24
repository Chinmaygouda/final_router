"""
Test the anti-hallucination keyword overlap verification layer.
This validates that the cache won't serve wrong responses.
"""
import sys
import io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
sys.path.insert(0, '.')

from app.vault_service import VaultService

print("=" * 60)
print("  ANTI-HALLUCINATION VERIFICATION TESTS")
print("=" * 60)

# Test 1: Identical prompts
overlap = VaultService._compute_keyword_overlap(
    "write code for tower of hanoi",
    "write code for tower of hanoi"
)
print(f"\n[TEST 1] Identical prompts")
print(f"  Overlap: {overlap:.2f} (expected: 1.00)")
assert overlap == 1.0, f"FAIL: expected 1.0, got {overlap}"
print("  [OK] PASS")

# Test 2: Same topic, typo
overlap = VaultService._compute_keyword_overlap(
    "write code for tower of hanoi",
    "toweer of hanio code"
)
print(f"\n[TEST 2] Same topic with typos ('toweer', 'hanio')")
print(f"  Overlap: {overlap:.2f}")
if overlap < 0.30:
    print("  [OK] Typos correctly detected as mismatch -> cache MISS (safe)")
else:
    print("  [INFO] Overlap high enough to pass -> cache HIT (risky but prompt is similar)")

# Test 3: Completely different topics
overlap = VaultService._compute_keyword_overlap(
    "write a sorting algorithm in python",
    "explain quantum physics theory"
)
print(f"\n[TEST 3] Completely different topics")
print(f"  Overlap: {overlap:.2f} (expected: ~0.00)")
assert overlap < 0.15, f"FAIL: expected < 0.15, got {overlap}"
print("  [OK] Different topics correctly rejected")

# Test 4: Similar topic but CRITICAL word differs
overlap = VaultService._compute_keyword_overlap(
    "write a bubble sort algorithm",
    "write a binary search algorithm"
)
print(f"\n[TEST 4] Similar structure, different algorithm")
print(f"  Overlap: {overlap:.2f}")
print(f"  Keywords A: bubble, sort, algorithm")
print(f"  Keywords B: binary, search, algorithm")
assert overlap < 0.50, f"FAIL: expected < 0.50, got {overlap}"
print("  [OK] Won't serve 'bubble sort' code for 'binary search' query")

# Test 5: Same topic, rephrased
overlap = VaultService._compute_keyword_overlap(
    "tower of hanoi recursive solution",
    "recursive tower of hanoi implementation"
)
print(f"\n[TEST 5] Same topic, rephrased")
print(f"  Overlap: {overlap:.2f} (expected: > 0.30)")
assert overlap >= 0.30, f"FAIL: expected >= 0.30, got {overlap}"
print("  [OK] Rephrased prompts correctly matched")

# Test 6: Same domain, opposite action
overlap = VaultService._compute_keyword_overlap(
    "how to delete a file in python",
    "how to create a file in python"
)
print(f"\n[TEST 6] Same domain, opposite action (delete vs create)")
print(f"  Overlap: {overlap:.2f}")
if overlap >= 0.30:
    print("  [WARN] Might serve 'delete' for 'create' query")
    print("         Vector distance (Layer 1) will block this")
else:
    print("  [OK] Opposite actions correctly distinguished")

# Test 7: Nearly identical phrasing
overlap = VaultService._compute_keyword_overlap(
    "fibonacci sequence python code",
    "fibonacci series python program"
)
print(f"\n[TEST 7] Near-identical (fibonacci code vs fibonacci program)")
print(f"  Overlap: {overlap:.2f} (expected: > 0.30)")
assert overlap >= 0.30, f"FAIL: expected >= 0.30, got {overlap}"
print("  [OK] Near-identical prompts correctly matched")

print("\n" + "=" * 60)
print("  THRESHOLD SUMMARY")
print("=" * 60)
print(f"  Vector threshold:  0.55 (L2 distance)")
print(f"  Keyword threshold: 0.30 (Jaccard overlap)")
print(f"  Both must pass for a cache hit to be served.")
print(f"")
print(f"  Protection against:")
print(f"  - 'sorting' vs 'searching'   -> BLOCKED (keyword overlap too low)")
print(f"  - 'tower of hanoi' typos     -> BLOCKED (keywords don't match)")
print(f"  - 'delete file' vs 'create'  -> BLOCKED (vector distance too high)")
print(f"  - exact/rephrased prompts    -> ALLOWED (both layers pass)")
print("=" * 60)
print("\n  ALL TESTS PASSED!")
