"""Generate synthetic v2 tree assessment seed data.

Produces a JSON file with ~500 records covering all 130 tree forms.
Distribution is realistic: heavy in L2-L3/P-I, sparse at extremes.

Run: python assessment/scripts/generate_tree_seed_data.py
Output: assessment/tree_seed_data.json
"""

import json
import random
from pathlib import Path

random.seed(42)

NUM_TO_STAGE = {1: "E", 2: "P", 3: "I", 4: "A", 5: "S"}
STAGE_NAMES = {"E": "Explorer", "P": "Practitioner", "I": "Integrator",
               "A": "Architect", "S": "Steward"}
SAE_NAMES = {0: "Manual", 1: "AI-Assisted", 2: "Partially Automated",
             3: "Guided Automation", 4: "Mostly Automated", 5: "Full Automation"}

ROLES = ["design", "uxr"]
AGE_RANGES = ["18-24", "25-34", "35-44", "45-54", "55+"]

# ── Weight matrices for realistic distribution ──
# root_depth weights (1-5): moderate roots most common
ROOT_WEIGHTS = {1: 0.10, 2: 0.25, 3: 0.35, 4: 0.20, 5: 0.10}

# canopy_width/SAE weights (0-5): L0 uncommon, L2-L3 peak
SAE_WEIGHTS = {0: 0.08, 1: 0.15, 2: 0.28, 3: 0.25, 4: 0.16, 5: 0.08}

# canopy_height weights (1-5): P-I most common (for non-L0 trees)
CH_WEIGHTS = {1: 0.12, 2: 0.28, 3: 0.32, 4: 0.18, 5: 0.10}


def weighted_choice(weights_dict):
    keys = list(weights_dict.keys())
    weights = [weights_dict[k] for k in keys]
    return random.choices(keys, weights=weights, k=1)[0]


def compute_balance(rd, cw, ch):
    if cw == 0:
        return "grounded"
    demand = cw * 2 + ch * 2
    capacity = rd * 5
    ratio = demand / capacity if capacity > 0 else 99
    if ratio <= 0.6:
        return "deeply rooted"
    elif ratio <= 1.1:
        return "balanced"
    elif ratio <= 1.8:
        return "reaching"
    else:
        return "top-heavy"


# ── Step 1: Guarantee at least 1 record per form ──
records = []

# L0 forms: rd 1-5, cw=0, ch=0
for rd in range(1, 6):
    records.append({
        "root_depth": rd,
        "canopy_width": 0,
        "canopy_height": 0,
    })

# Non-L0 forms: rd 1-5, cw 1-5, ch 1-5
for rd in range(1, 6):
    for cw in range(1, 6):
        for ch in range(1, 6):
            records.append({
                "root_depth": rd,
                "canopy_width": cw,
                "canopy_height": ch,
            })

print(f"Base coverage: {len(records)} records (1 per form)")

# ── Step 2: Fill to ~500 with weighted distribution ──
TARGET = 500
remaining = TARGET - len(records)

for _ in range(remaining):
    rd = weighted_choice(ROOT_WEIGHTS)
    cw = weighted_choice(SAE_WEIGHTS)
    if cw == 0:
        ch = 0
    else:
        ch = weighted_choice(CH_WEIGHTS)
    records.append({
        "root_depth": rd,
        "canopy_width": cw,
        "canopy_height": ch,
    })

# Shuffle so the guaranteed-coverage records aren't all at the front
random.shuffle(records)

# ── Step 3: Enrich with metadata ──
enriched = []
for r in records:
    rd, cw, ch = r["root_depth"], r["canopy_width"], r["canopy_height"]
    root_stage = NUM_TO_STAGE[rd]
    canopy_stage = NUM_TO_STAGE[ch] if ch > 0 else None
    balance = compute_balance(rd, cw, ch)

    enriched.append({
        "root_depth": rd,
        "canopy_width": cw,
        "canopy_height": ch,
        "root_stage": root_stage,
        "canopy_stage": canopy_stage,
        "balance": balance,
        "role": random.choice(ROLES),
        "age_range": random.choice(AGE_RANGES),
    })

# ── Verify coverage ──
form_keys = set()
for r in enriched:
    form_keys.add(f"r{r['root_depth']}_c{r['canopy_width']}_h{r['canopy_height']}")

print(f"Total records: {len(enriched)}")
print(f"Unique forms covered: {len(form_keys)} / 130")

# Distribution summary
from collections import Counter
balance_dist = Counter(r["balance"] for r in enriched)
print(f"Balance distribution: {dict(balance_dist)}")

sae_dist = Counter(r["canopy_width"] for r in enriched)
print(f"SAE distribution: {dict(sorted(sae_dist.items()))}")

root_dist = Counter(r["root_depth"] for r in enriched)
print(f"Root distribution: {dict(sorted(root_dist.items()))}")

# ── Save ──
out_path = Path(__file__).parent.parent / "tree_seed_data.json"
with open(out_path, "w", encoding="utf-8") as f:
    json.dump(enriched, f, indent=2)

print(f"\nSaved to {out_path}")
