"""Score assessment answers into SAE level and EPIAS stage."""
import time
from assessment.questions import SAE_QUESTIONS, EPIAS_QUESTIONS


STAGE_TO_NUM = {"E": 1, "P": 2, "I": 3, "A": 4, "S": 5}
NUM_TO_STAGE = {1: "E", 2: "P", 3: "I", 4: "A", 5: "S"}
STAGE_NAMES = {
    "E": "Explorer", "P": "Practitioner", "I": "Integrator",
    "A": "Architect", "S": "Steward",
}
SAE_NAMES = {
    0: "Manual", 1: "AI-Assisted", 2: "Partially Automated",
    3: "Guided Automation", 4: "Mostly Automated", 5: "Full Automation",
}
SAE_EMOJIS = {
    0: "\U0001f697\U0001f4a8", 1: "\U0001f697\u2795", 2: "\U0001f697\U0001f9e0",
    3: "\U0001f697\U0001f634", 4: "\U0001f695\U0001f916", 5: "\U0001f697\u2728",
}

# Tree form taxonomy: maps (root_depth, sae_level) to a tree species.
# root_depth is numeric EPIAS (1-5), sae_level is 0-5.
# The species communicates the shape: root extent vs canopy spread.
TREE_FORMS = {
    # L0 canopy (no AI) — all roots, no above-ground AI growth
    (1, 0): {"species": "Hawthorn",        "icon": "small_tree","desc": "Small, hardy, just getting established — common and resilient."},
    (2, 0): {"species": "Crabapple",       "icon": "small_tree","desc": "Compact and reliable in its niche — moderate roots, consistent output."},
    (3, 0): {"species": "Olive",           "icon": "olive",     "desc": "Deep-rooted and ancient — stays compact but built to last centuries."},
    (4, 0): {"species": "Yew",             "icon": "yew",       "desc": "Extensive root network others shelter under — quiet, long-lived, load-bearing."},
    (5, 0): {"species": "Bristlecone Pine","icon": "bristlecone","desc": "The oldest trees on earth — deepest roots, holds the mountainside together. The Redwood can't exist without it."},

    # L1 canopy (AI-Assisted) — narrow, close to trunk
    (1, 1): {"species": "Redbud",       "icon": "small_tree","desc": "Small ornamental, everywhere — low canopy, still finding its shape."},
    (2, 1): {"species": "Dogwood",      "icon": "small_tree","desc": "Understory tree — not the tallest, but well-anchored and purposeful."},
    (3, 1): {"species": "Holly",        "icon": "holly",     "desc": "Compact, structured, well-documented — others know exactly what to expect."},
    (4, 1): {"species": "Birch",        "icon": "birch",     "desc": "Elegant, moderate height — distinctive presence, deep enough roots for its size."},
    (5, 1): {"species": "Elm",          "icon": "elm",       "desc": "Stately presence with deep craft roots — AI is a supplement, not the structure."},

    # L2 canopy (Partially Automated) — moderate spread
    (1, 2): {"species": "Aspen",        "icon": "aspen",     "desc": "Grows fast and spreads wide — but the root system is still catching up."},
    (2, 2): {"species": "Cherry",       "icon": "cherry",    "desc": "Attractive canopy on developing roots — balance is emerging."},
    (3, 2): {"species": "Maple",        "icon": "maple",     "desc": "Strong canopy, reliable shade — the backbone of most design teams."},
    (4, 2): {"species": "Beech",        "icon": "beech",     "desc": "Wide canopy on a deep root network — others shelter under it."},
    (5, 2): {"species": "Chestnut",     "icon": "chestnut",  "desc": "Massive trunk, deep roots — the canopy could grow wider and it would hold."},

    # L3 canopy (Guided Automation) — wide spread
    (1, 3): {"species": "Bamboo",       "icon": "bamboo",    "desc": "Grows tall fast on shallow roots — impressive reach, but bends in a storm."},
    (2, 3): {"species": "Poplar",       "icon": "poplar",    "desc": "Tall and quick-growing — roots developing but haven't caught up yet."},
    (3, 3): {"species": "Ash",          "icon": "ash",       "desc": "Balanced height and root depth — a solid working tree."},
    (4, 3): {"species": "Oak",          "icon": "oak",       "desc": "Wide, deep-rooted, long-lived — anchors the forest."},
    (5, 3): {"species": "White Oak",    "icon": "oak",       "desc": "The most grounded oak — root system exceeds what the canopy needs."},

    # L4 canopy (Mostly Automated) — very wide spread
    (1, 4): {"species": "Palm",         "icon": "palm",      "desc": "Tall trunk, tiny root ball — looks dramatic but a hurricane reveals the gap."},
    (2, 4): {"species": "Eucalyptus",   "icon": "eucalyptus","desc": "Fast-growing canopy outpacing its roots — productive but brittle under pressure."},
    (3, 4): {"species": "Walnut",       "icon": "walnut",    "desc": "Large canopy catching up to solid roots — getting close to balance."},
    (4, 4): {"species": "Douglas Fir",  "icon": "fir",       "desc": "Tall, straight, deeply anchored — built for scale."},
    (5, 4): {"species": "Sequoia",      "icon": "sequoia",   "desc": "Enormous and deeply rooted — craft mastery sustains autonomous systems."},

    # L5 canopy (Full Automation) — widest spread
    (1, 5): {"species": "Banyan",       "icon": "banyan",    "desc": "Spreads endlessly outward but shallow — broad reach, no deep structure."},
    (2, 5): {"species": "Fig",          "icon": "fig",       "desc": "Wide canopy on developing roots — impressive spread but needs grounding."},
    (3, 5): {"species": "Baobab",       "icon": "baobab",    "desc": "Massive canopy on a thick trunk — the roots are catching up."},
    (4, 5): {"species": "Giant Sequoia","icon": "sequoia",   "desc": "Among the largest living things — deep roots match enormous presence."},
    (5, 5): {"species": "Redwood",      "icon": "redwood",   "desc": "The tallest and widest — requires the deepest roots. The rarest form."},
}


def score_assessment(answers: dict) -> dict:
    """Score user answers into SAE level and EPIAS stage.

    Args:
        answers: {
            "sae_tools": 2, "sae_qa": 1, ...  (SAE question id -> selected level int)
            "epias_l1_consistency": "P", ...     (EPIAS question id -> selected stage letter)
        }

    Returns:
        Dict with sae_level, epias_stage, and supporting data.
    """
    # 1. SAE Level: median of selected levels
    sae_values = []
    for q in SAE_QUESTIONS:
        val = answers.get(q["id"])
        if val is not None:
            sae_values.append(int(val))

    if not sae_values:
        sae_level = 1  # Default
    else:
        sorted_vals = sorted(sae_values)
        sae_level = sorted_vals[len(sorted_vals) // 2]

    # Clamp to valid range
    sae_level = max(0, min(5, sae_level))

    # 2. EPIAS Stage: median of selected stages within the identified SAE level
    epias_values = []
    level_questions = EPIAS_QUESTIONS.get(sae_level, [])
    for q in level_questions:
        val = answers.get(q["id"])
        if val is not None and val in STAGE_TO_NUM:
            epias_values.append(STAGE_TO_NUM[val])

    if not epias_values:
        epias_numeric = 1  # Default to Explorer
    else:
        sorted_vals = sorted(epias_values)
        epias_numeric = sorted_vals[len(sorted_vals) // 2]

    epias_stage = NUM_TO_STAGE[epias_numeric]

    return {
        "sae_level": sae_level,
        "sae_name": SAE_NAMES[sae_level],
        "sae_emoji": SAE_EMOJIS[sae_level],
        "epias_stage": epias_stage,
        "epias_name": STAGE_NAMES[epias_stage],
        "sae_distribution": {q["id"]: answers.get(q["id"]) for q in SAE_QUESTIONS},
        "epias_distribution": {q["id"]: answers.get(q["id"]) for q in level_questions},
    }


def score_assessment_v2(answers: dict, role: str = 'design') -> dict:
    """Score v2 tree assessment: dual codes (root depth + canopy shape).

    Args:
        answers: {
            "root_design_craft": "P", ...    (root question id -> stage letter)
            "sae_tools": 2, ...              (SAE question id -> level int)
            "epias_l2_spec_clarity": "I", ...  (canopy EPIAS id -> stage letter)
        }
        role: 'design' or 'uxr'

    Returns:
        Dict with root_stage, sae_level, canopy_stage, tree_form, balance, etc.
    """
    from assessment.questions import get_root_questions, get_epias_questions

    # 1. Root depth: median of root question answers
    root_questions = get_root_questions(role)
    root_values = []
    for q in root_questions:
        val = answers.get(q["id"])
        if val is not None and val in STAGE_TO_NUM:
            root_values.append(STAGE_TO_NUM[val])

    if not root_values:
        root_numeric = 1
    else:
        sorted_vals = sorted(root_values)
        root_numeric = sorted_vals[len(sorted_vals) // 2]
    root_stage = NUM_TO_STAGE[root_numeric]

    # 2. SAE Level: median of SAE answers (same as v1)
    sae_questions = SAE_QUESTIONS
    sae_values = []
    for q in sae_questions:
        val = answers.get(q["id"])
        if val is not None:
            sae_values.append(int(val))

    if not sae_values:
        sae_level = 0
    else:
        sorted_vals = sorted(sae_values)
        sae_level = sorted_vals[len(sorted_vals) // 2]
    sae_level = max(0, min(5, sae_level))

    # 3. Canopy EPIAS: median of canopy answers (only if SAE > 0)
    if sae_level == 0:
        canopy_stage = None
        canopy_numeric = 0
    else:
        canopy_questions = get_epias_questions(sae_level, role)
        canopy_values = []
        for q in canopy_questions:
            val = answers.get(q["id"])
            if val is not None and val in STAGE_TO_NUM:
                canopy_values.append(STAGE_TO_NUM[val])

        if not canopy_values:
            canopy_numeric = 1
        else:
            sorted_vals = sorted(canopy_values)
            canopy_numeric = sorted_vals[len(sorted_vals) // 2]
        canopy_stage = NUM_TO_STAGE[canopy_numeric]

    # 4. Tree form lookup
    tree_key = (root_numeric, sae_level)
    tree_form = TREE_FORMS.get(tree_key, TREE_FORMS.get((1, 0)))

    # 5. Balance analysis
    # Root depth (1-5) vs canopy demand from both SAE level (spread) and EPIAS (height).
    # SAE level creates structural demand even at low EPIAS — a wide canopy needs support.
    # EPIAS height adds vertical load. Both contribute independently to demand.
    if sae_level == 0:
        balance = "grounded"
        balance_desc = "All roots, no AI canopy \u2014 your foundation is your whole tree."
    else:
        canopy_demand = sae_level * 2 + canopy_numeric * 2  # 4-20 range
        root_capacity = root_numeric * 5                     # 5-25 range
        ratio = canopy_demand / root_capacity if root_capacity > 0 else 99

        if ratio <= 0.6:
            balance = "deeply rooted"
            balance_desc = "Your craft foundation exceeds your canopy \u2014 a strong position with room to grow."
        elif ratio <= 1.1:
            balance = "balanced"
            balance_desc = "Your root depth matches your canopy spread \u2014 a sustainable shape."
        elif ratio <= 1.8:
            balance = "reaching"
            balance_desc = "Your canopy is outpacing your roots \u2014 consider deepening your craft foundation."
        else:
            balance = "top-heavy"
            balance_desc = "Your canopy significantly exceeds your roots \u2014 this shape is fragile in a storm."

    # 6. Compose result
    root_code = f"L0-{root_stage}"
    canopy_code = f"L{sae_level}-{canopy_stage}" if canopy_stage else None

    return {
        # Root
        "root_stage": root_stage,
        "root_name": STAGE_NAMES[root_stage],
        "root_numeric": root_numeric,
        "root_code": root_code,
        "root_distribution": {q["id"]: answers.get(q["id"]) for q in root_questions},
        # Canopy
        "sae_level": sae_level,
        "sae_name": SAE_NAMES[sae_level],
        "canopy_stage": canopy_stage,
        "canopy_name": STAGE_NAMES[canopy_stage] if canopy_stage else None,
        "canopy_numeric": canopy_numeric,
        "canopy_code": canopy_code,
        "sae_distribution": {q["id"]: answers.get(q["id"]) for q in sae_questions},
        # Tree
        "tree_species": tree_form["species"],
        "tree_icon": tree_form["icon"],
        "tree_description": tree_form["desc"],
        "balance": balance,
        "balance_description": balance_desc,
        # Viz params (for SVG rendering)
        "viz": {
            "root_depth": root_numeric,      # 1-5
            "root_spread": root_numeric,      # mirrors depth
            "canopy_width": sae_level,        # 0-5
            "canopy_height": canopy_numeric,  # 0-5
            "seed": int(time.time() * 1000) % 2147483647,  # unique per person
        },
    }
