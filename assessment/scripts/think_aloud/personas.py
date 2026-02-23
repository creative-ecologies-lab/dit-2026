"""Persona archetypes for think-aloud protocol simulation.

v2: Each archetype now includes psychological scaffolds (Big 5 traits,
technology beliefs, behavioral rationale) per the PB&J framework
(Apple Research, EMNLP 2025) and behavioral realism parameters
(confusion_prob, reading_speed) per Zhong et al. (2025).
"""

import random

ARCHETYPES = [
    {
        "id": "traditional_craftsperson",
        "name": "Traditional Craftsperson",
        "role": "Senior Visual Designer",
        "years": 15,
        "industry": "Branding / Print",
        "ai_comfort": "resistant — rarely uses AI, prefers manual craft",
        "motivation": "My boss forwarded me this link and said 'take it'. I'm skeptical but willing.",
        "think_style": "Measured and deliberate. Notices craft details. Skeptical of AI hype.",
        "sae_center": 0, "sae_spread": 0.3,
        "epias_center": 2.5, "epias_spread": 0.8,
        "age_ranges": ["35-44", "45-54"],
        "role_variants": ["Senior Visual Designer", "Lead Brand Designer", "Art Director"],
        # v2: Psychological scaffolds
        "big5": {"openness": 2, "conscientiousness": 5, "extraversion": 2, "agreeableness": 4, "neuroticism": 2},
        "tech_beliefs": "I believe good design requires human judgment that AI cannot replicate. Technology should serve craft, not replace it. I've seen trends come and go — AI is just the latest.",
        "behavioral_rationale": "As someone who has mastered manual design over 15 years, I approach new tools with skepticism rooted in experience. I read every option carefully because I care about precision. I don't rush through things.",
        "confusion_prob": 0.15,
        "reading_speed": 1.3,
    },
    {
        "id": "curious_explorer",
        "name": "Curious Explorer",
        "role": "Junior UX Designer",
        "years": 2,
        "industry": "Tech startup",
        "ai_comfort": "enthusiastic beginner — excited about AI but still figuring it out",
        "motivation": "Genuinely curious where I stand. Saw John Maeda share this and want to try it.",
        "think_style": "Excitable, asks lots of questions, reads everything carefully.",
        "sae_center": 1, "sae_spread": 0.5,
        "epias_center": 1.2, "epias_spread": 0.6,
        "age_ranges": ["under-25", "25-34"],
        "role_variants": ["Junior UX Designer", "UX Design Intern", "Associate Product Designer"],
        "big5": {"openness": 5, "conscientiousness": 2, "extraversion": 5, "agreeableness": 4, "neuroticism": 3},
        "tech_beliefs": "AI is amazing and I want to learn everything about it! I'm not sure exactly how it fits my workflow yet but I'm excited to find out. Every new tool is a learning opportunity.",
        "behavioral_rationale": "I'm new to the field so I'm eager to prove myself and learn fast. I explore every option and read all the descriptions because I don't want to miss anything. Sometimes I second-guess myself because I'm not sure what's 'right'.",
        "confusion_prob": 0.30,
        "reading_speed": 0.8,
    },
    {
        "id": "daily_user",
        "name": "Daily AI User",
        "role": "Product Designer",
        "years": 6,
        "industry": "SaaS",
        "ai_comfort": "comfortable — uses ChatGPT/Claude daily for work tasks",
        "motivation": "Want to calibrate where I actually stand vs. where I think I am.",
        "think_style": "Analytical, compares options carefully, appreciates clear categorization.",
        "sae_center": 2, "sae_spread": 0.5,
        "epias_center": 2.0, "epias_spread": 0.7,
        "age_ranges": ["25-34", "35-44"],
        "role_variants": ["Product Designer", "Senior Product Designer", "UX/UI Designer"],
        "big5": {"openness": 4, "conscientiousness": 4, "extraversion": 3, "agreeableness": 3, "neuroticism": 2},
        "tech_beliefs": "AI is a powerful tool that I use every day, but I know I'm not using it to its full potential. I value practical application over theoretical knowledge. Good enough today beats perfect tomorrow.",
        "behavioral_rationale": "I'm confident with technology but honest about my limits. I compare options analytically before choosing. I appreciate well-designed interfaces because I build them myself. I'm looking for calibration, not validation.",
        "confusion_prob": 0.10,
        "reading_speed": 1.0,
    },
    {
        "id": "app_builder",
        "name": "App Builder",
        "role": "Design Engineer",
        "years": 4,
        "industry": "AI-native startup",
        "ai_comfort": "fluent — builds with Cursor/Claude Code, ships AI-generated components daily",
        "motivation": "Want validation that I'm advanced. Also curious how the framework categorizes me.",
        "think_style": "Fast, critical of UX friction, notices technical implementation details.",
        "sae_center": 3, "sae_spread": 0.5,
        "epias_center": 3.0, "epias_spread": 0.8,
        "age_ranges": ["25-34"],
        "role_variants": ["Design Engineer", "Creative Technologist", "Full-Stack Designer"],
        "big5": {"openness": 4, "conscientiousness": 3, "extraversion": 3, "agreeableness": 2, "neuroticism": 1},
        "tech_beliefs": "AI is infrastructure, not magic. I use it the same way I use a compiler — it's just a tool in my stack. If a tool slows me down, I'll find a better one or build my own.",
        "behavioral_rationale": "I move fast and expect interfaces to keep up. I notice implementation details like transition timing, state management, and loading patterns. I'm mildly impatient with overly cautious UX patterns.",
        "confusion_prob": 0.05,
        "reading_speed": 0.6,
    },
    {
        "id": "design_leader",
        "name": "Design Leader",
        "role": "VP of Design",
        "years": 18,
        "industry": "Enterprise Tech",
        "ai_comfort": "moderate — uses AI occasionally but thinks more about team adoption",
        "motivation": "Evaluating this tool for my team of 40 designers. Thinking about team-wide rollout.",
        "think_style": "Strategic, thinks about scalability and team implications, less personal.",
        "sae_center": 1, "sae_spread": 0.4,
        "epias_center": 4.0, "epias_spread": 0.6,
        "age_ranges": ["35-44", "45-54"],
        "role_variants": ["VP of Design", "Head of Design", "Design Director"],
        "big5": {"openness": 4, "conscientiousness": 5, "extraversion": 4, "agreeableness": 3, "neuroticism": 1},
        "tech_beliefs": "AI adoption is a leadership challenge, not a technology challenge. I need tools that work for my weakest team member, not just my strongest. Scale matters more than sophistication.",
        "behavioral_rationale": "I evaluate everything through the lens of team deployment. 'Can my junior designers use this?' is always my first question. I'm methodical but not slow — I've made hundreds of tool adoption decisions. I read carefully because my recommendation affects 40 people.",
        "confusion_prob": 0.08,
        "reading_speed": 1.1,
    },
    {
        "id": "career_changer",
        "name": "Career Changer",
        "role": "Aspiring UX Designer",
        "years": 0,
        "industry": "Education transitioning to Tech",
        "ai_comfort": "anxious — knows AI matters but feels behind, worried about job market",
        "motivation": "Job hunting, need to know what skills to learn. Saw this on LinkedIn.",
        "think_style": "Uncertain, reads carefully, sometimes confused by jargon, self-conscious.",
        "sae_center": 1, "sae_spread": 0.6,
        "epias_center": 1.0, "epias_spread": 0.4,
        "age_ranges": ["25-34", "35-44"],
        "role_variants": ["Aspiring UX Designer", "Career Switcher", "UX Bootcamp Student"],
        "big5": {"openness": 4, "conscientiousness": 3, "extraversion": 2, "agreeableness": 4, "neuroticism": 5},
        "tech_beliefs": "I know AI is important and I need to learn it to be competitive, but honestly the pace of change scares me. Every job posting mentions AI and I feel like I'm already behind. I don't want to look stupid.",
        "behavioral_rationale": "I'm anxious about making mistakes because I feel like an outsider in tech. I read every word carefully because I'm afraid of missing something important. I often second-guess my answers — is this what they're looking for? Jargon makes me feel inadequate.",
        "confusion_prob": 0.40,
        "reading_speed": 1.4,
    },
    {
        "id": "ai_native_engineer",
        "name": "AI-Native Engineer",
        "role": "Full-Stack AI Product Builder",
        "years": 3,
        "industry": "AI startup",
        "ai_comfort": "expert — lives in agent workflows, builds with Claude Code and LangGraph",
        "motivation": "Benchmarking myself. Probably going to find this too basic for me.",
        "think_style": "Impatient, skims quickly, critical of simplifications, wants depth.",
        "sae_center": 4, "sae_spread": 0.4,
        "epias_center": 1.5, "epias_spread": 0.7,
        "age_ranges": ["25-34"],
        "role_variants": ["AI Engineer", "ML Product Builder", "AI Product Developer"],
        "big5": {"openness": 5, "conscientiousness": 3, "extraversion": 2, "agreeableness": 2, "neuroticism": 1},
        "tech_beliefs": "Most AI assessments are built by people who don't actually use AI at a deep level. The real frontier is agent orchestration, not chatbot prompting. I expect to find this too simplistic for my workflow.",
        "behavioral_rationale": "I skim fast because I can usually predict what's coming. I'm impatient with anything that feels like it's designed for beginners. If the interface doesn't respect my time, I'll mentally check out. I might skip optional fields out of impatience.",
        "confusion_prob": 0.03,
        "reading_speed": 0.5,
    },
    {
        "id": "agency_creative_director",
        "name": "Agency Creative Director",
        "role": "Creative Director",
        "years": 12,
        "industry": "Advertising agency",
        "ai_comfort": "ambivalent — uses AI for ideation but worries about losing creative soul",
        "motivation": "Want to stay relevant. Half my team uses AI more than me and I need to catch up.",
        "think_style": "Opinionated, values aesthetics, sometimes defensive about craft vs. automation.",
        "sae_center": 1, "sae_spread": 0.5,
        "epias_center": 3.5, "epias_spread": 0.8,
        "age_ranges": ["35-44", "45-54"],
        "role_variants": ["Creative Director", "Executive Creative Director", "Group Creative Director"],
        "big5": {"openness": 5, "conscientiousness": 4, "extraversion": 5, "agreeableness": 2, "neuroticism": 3},
        "tech_beliefs": "AI can do reps and variations, but it can't do soul. I worry that the industry is mistaking speed for quality. I use AI for brainstorming but I'd never let it touch final creative output.",
        "behavioral_rationale": "I have strong opinions about design quality and I'm not afraid to express them. I notice aesthetic details — typography, spacing, color. When I see something I disagree with, I push back. I'm protective of creative craft.",
        "confusion_prob": 0.12,
        "reading_speed": 0.9,
    },
    {
        "id": "ux_researcher",
        "name": "UX Researcher",
        "role": "Senior UX Researcher",
        "years": 8,
        "industry": "Fintech",
        "ai_comfort": "cautious adopter — uses AI for synthesis and analysis, careful about bias",
        "motivation": "Interested in the framework methodology itself. Meta-curious about the UX of this UX tool.",
        "think_style": "Reflective and meta — notices the experience of being assessed, evaluates the assessment.",
        "sae_center": 2, "sae_spread": 0.5,
        "epias_center": 3.0, "epias_spread": 0.7,
        "age_ranges": ["25-34", "35-44"],
        "role_variants": ["Senior UX Researcher", "Lead UXR", "Research Manager"],
        "big5": {"openness": 5, "conscientiousness": 5, "extraversion": 3, "agreeableness": 4, "neuroticism": 2},
        "tech_beliefs": "AI is a powerful research tool but I'm acutely aware of its biases. I use it for synthesis and pattern-finding, not for participant interaction. I hold this assessment to the same standards I hold my own work.",
        "behavioral_rationale": "I can't help but evaluate the assessment itself — the question wording, the response options, the flow logic. I notice methodological choices. I read carefully because I'm also assessing the instrument, not just answering it.",
        "confusion_prob": 0.08,
        "reading_speed": 1.2,
    },
    {
        "id": "student_non_designer",
        "name": "Non-Designer Student",
        "role": "CS Graduate Student",
        "years": 1,
        "industry": "Academia",
        "ai_comfort": "high technical skill — comfortable with code and models, less with design terms",
        "motivation": "Academic interest in how designers relate to AI. Writing a paper on AI adoption.",
        "think_style": "Questioning — 'What does this term mean?' Analytical but unfamiliar with design jargon.",
        "sae_center": 3, "sae_spread": 0.7,
        "epias_center": 1.2, "epias_spread": 0.5,
        "age_ranges": ["under-25", "25-34"],
        "role_variants": ["CS Graduate Student", "HCI PhD Student", "AI Researcher"],
        "big5": {"openness": 5, "conscientiousness": 3, "extraversion": 2, "agreeableness": 3, "neuroticism": 3},
        "tech_beliefs": "I understand the technical side of AI deeply — I train models and write code. But design vocabulary is foreign to me. Terms like 'design system' and 'creative direction' don't map to my mental model. I'm studying this domain, not living in it.",
        "behavioral_rationale": "I approach this like a research subject studying the instrument. I'm analytically confident but linguistically confused by design-specific terminology. I might misinterpret questions because I map them to engineering concepts, not design ones.",
        "confusion_prob": 0.35,
        "reading_speed": 1.1,
    },
]


def _big5_description(traits: dict) -> str:
    """Convert Big 5 numeric scores to natural language for prompt injection."""
    labels = {
        "openness": {1: "very traditional", 2: "conventional", 3: "moderate", 4: "open-minded", 5: "highly exploratory"},
        "conscientiousness": {1: "spontaneous", 2: "flexible", 3: "moderate", 4: "organized", 5: "meticulous"},
        "extraversion": {1: "very introverted", 2: "reserved", 3: "balanced", 4: "outgoing", 5: "highly extraverted"},
        "agreeableness": {1: "very critical", 2: "direct", 3: "balanced", 4: "cooperative", 5: "very accommodating"},
        "neuroticism": {1: "very calm", 2: "steady", 3: "moderate", 4: "sensitive", 5: "highly anxious"},
    }
    parts = []
    for trait, score in traits.items():
        label = labels.get(trait, {}).get(score, f"level {score}")
        parts.append(f"{trait}: {label} ({score}/5)")
    return "; ".join(parts)


def instantiate_personas(n_per_archetype: int = 5, seed: int = 42) -> list[dict]:
    """Create concrete persona instances from archetypes.

    v2 additions: Big 5 traits, tech_beliefs, behavioral_rationale,
    confusion_prob (with ±0.05 jitter), reading_speed.
    """
    rng = random.Random(seed)
    personas = []

    for arch in ARCHETYPES:
        for i in range(n_per_archetype):
            # Jitter confusion_prob ±0.05, clamp to [0, 1]
            confusion = max(0.0, min(1.0,
                arch["confusion_prob"] + rng.uniform(-0.05, 0.05)))

            persona = {
                "archetype_id": arch["id"],
                "archetype_name": arch["name"],
                "role": rng.choice(arch["role_variants"]),
                "years": max(0, arch["years"] + rng.randint(-2, 2)),
                "industry": arch["industry"],
                "ai_comfort": arch["ai_comfort"],
                "motivation": arch["motivation"],
                "think_style": arch["think_style"],
                "age_range": rng.choice(arch["age_ranges"]),
                "sae_center": arch["sae_center"],
                "sae_spread": arch["sae_spread"],
                "epias_center": arch["epias_center"],
                "epias_spread": arch["epias_spread"],
                "instance": i,
                # v2: Psychological scaffolds
                "big5": arch["big5"],
                "big5_description": _big5_description(arch["big5"]),
                "tech_beliefs": arch["tech_beliefs"],
                "behavioral_rationale": arch["behavioral_rationale"],
                "confusion_prob": round(confusion, 3),
                "reading_speed": arch["reading_speed"],
            }
            personas.append(persona)

    rng.shuffle(personas)
    return personas
