"""Agent-based simulation of cohort assessment responses.

Creates realistic population distributions for demo cohorts by defining
persona archetypes with probabilistic answer profiles, running them through
the actual scorer, and storing results via the storage layer.

Designed for stress-testing at scale (10K+ agents) to evaluate:
  - Firestore write throughput and query performance
  - Heatmap visualization with realistic population distributions
  - Cohort differentiation and interpretability
  - Edge cases in the scoring algorithm

Usage:
    cd assessment
    python -m scripts.simulate_cohorts              # dry-run (print only)
    python -m scripts.simulate_cohorts --store      # store to active backend
    python -m scripts.simulate_cohorts --store --firestore  # force Firestore
    python -m scripts.simulate_cohorts --scale 2.0  # double all cohort sizes
"""

import argparse
import json
import os
import random
import sys
import time
from pathlib import Path

# Add assessment root to path so imports work
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from assessment.scorer import score_assessment
from assessment.questions import SAE_QUESTIONS, EPIAS_QUESTIONS


# ---------------------------------------------------------------------------
# Persona definitions
# ---------------------------------------------------------------------------
# Each persona has:
#   - sae_center: most likely SAE level (0-5)
#   - sae_spread: std-dev-like spread (higher = more variance)
#   - epias_center: most likely EPIAS stage as number (1=E, 2=P, 3=I, 4=A, 5=S)
#   - epias_spread: spread around center
#   - weight: relative frequency in the cohort

COHORT_PROFILES = {
    # -----------------------------------------------------------------------
    # Keynote audiences (~4,500 total)
    # -----------------------------------------------------------------------
    "sxsw-2026": {
        "description": "SXSW Design in Tech keynote — broad industry mix",
        "n": 1500,
        "personas": [
            {"label": "Curious newcomer",    "sae_center": 0, "sae_spread": 0.5, "epias_center": 1.5, "epias_spread": 0.8, "weight": 0.08},
            {"label": "Marketing designer",  "sae_center": 1, "sae_spread": 0.6, "epias_center": 2.0, "epias_spread": 0.9, "weight": 0.22},
            {"label": "Product designer",    "sae_center": 2, "sae_spread": 0.7, "epias_center": 2.5, "epias_spread": 1.0, "weight": 0.30},
            {"label": "Design engineer",     "sae_center": 3, "sae_spread": 0.6, "epias_center": 2.0, "epias_spread": 1.0, "weight": 0.20},
            {"label": "AI-forward leader",   "sae_center": 4, "sae_spread": 0.5, "epias_center": 3.0, "epias_spread": 1.0, "weight": 0.10},
            {"label": "Design director",     "sae_center": 1, "sae_spread": 0.4, "epias_center": 4.0, "epias_spread": 0.7, "weight": 0.05},
            {"label": "Startup founder",     "sae_center": 3, "sae_spread": 0.8, "epias_center": 2.0, "epias_spread": 1.2, "weight": 0.05},
        ],
        "roles": ["Product Designer", "UX Designer", "Design Lead", "UX Researcher",
                   "Design Engineer", "Creative Director", "Visual Designer",
                   "Design Manager", "Frontend Dev", "PM", "Startup Founder",
                   "Design Strategist", "Content Designer"],
        "age_distribution": {"Under 25": 0.10, "25-34": 0.35, "35-44": 0.30,
                             "45-54": 0.15, "55+": 0.05, "Prefer not to say": 0.05},
    },

    "config-2026": {
        "description": "Figma Config conference — design tool-savvy crowd",
        "n": 1200,
        "personas": [
            {"label": "Design student",      "sae_center": 1, "sae_spread": 0.5, "epias_center": 1.0, "epias_spread": 0.6, "weight": 0.10},
            {"label": "IC designer",         "sae_center": 2, "sae_spread": 0.5, "epias_center": 2.5, "epias_spread": 0.9, "weight": 0.35},
            {"label": "Senior designer",     "sae_center": 2, "sae_spread": 0.6, "epias_center": 3.0, "epias_spread": 0.9, "weight": 0.25},
            {"label": "Design systems lead", "sae_center": 3, "sae_spread": 0.5, "epias_center": 3.5, "epias_spread": 0.8, "weight": 0.15},
            {"label": "Plugin developer",    "sae_center": 3, "sae_spread": 0.6, "epias_center": 2.0, "epias_spread": 1.0, "weight": 0.10},
            {"label": "VP Design",           "sae_center": 2, "sae_spread": 0.5, "epias_center": 4.5, "epias_spread": 0.6, "weight": 0.05},
        ],
        "roles": ["Product Designer", "Senior Product Designer", "Design Systems Lead",
                   "Plugin Developer", "UX Designer", "Visual Designer",
                   "Design Manager", "VP Design", "Design Ops"],
        "age_distribution": {"Under 25": 0.15, "25-34": 0.40, "35-44": 0.28,
                             "45-54": 0.12, "55+": 0.02, "Prefer not to say": 0.03},
    },

    "webex-summit": {
        "description": "Web Summit / enterprise track — business-oriented, early AI adoption",
        "n": 1800,
        "personas": [
            {"label": "Non-technical exec",  "sae_center": 0, "sae_spread": 0.4, "epias_center": 2.0, "epias_spread": 1.0, "weight": 0.15},
            {"label": "Product manager",     "sae_center": 1, "sae_spread": 0.5, "epias_center": 2.5, "epias_spread": 1.0, "weight": 0.25},
            {"label": "UX designer",         "sae_center": 2, "sae_spread": 0.6, "epias_center": 2.0, "epias_spread": 0.9, "weight": 0.25},
            {"label": "Software engineer",   "sae_center": 3, "sae_spread": 0.7, "epias_center": 2.0, "epias_spread": 1.0, "weight": 0.15},
            {"label": "AI/ML engineer",      "sae_center": 4, "sae_spread": 0.5, "epias_center": 2.5, "epias_spread": 1.0, "weight": 0.10},
            {"label": "CTO / VP Eng",        "sae_center": 3, "sae_spread": 0.6, "epias_center": 4.0, "epias_spread": 0.8, "weight": 0.05},
            {"label": "Investor / analyst",  "sae_center": 1, "sae_spread": 0.6, "epias_center": 1.5, "epias_spread": 0.8, "weight": 0.05},
        ],
        "roles": ["Product Manager", "UX Designer", "Software Engineer",
                   "AI/ML Engineer", "CTO", "VP Engineering", "Design Lead",
                   "Business Analyst", "Founder", "Consultant", "Investor"],
        "age_distribution": {"Under 25": 0.05, "25-34": 0.30, "35-44": 0.35,
                             "45-54": 0.20, "55+": 0.05, "Prefer not to say": 0.05},
    },

    # -----------------------------------------------------------------------
    # Company / team cohorts (~3,000 total)
    # -----------------------------------------------------------------------
    "spotify-design": {
        "description": "Spotify design org — strong L2-L3, high maturity",
        "n": 400,
        "personas": [
            {"label": "Junior designer",    "sae_center": 1, "sae_spread": 0.5, "epias_center": 1.5, "epias_spread": 0.7, "weight": 0.15},
            {"label": "Mid designer",       "sae_center": 2, "sae_spread": 0.5, "epias_center": 2.5, "epias_spread": 0.8, "weight": 0.30},
            {"label": "Senior designer",    "sae_center": 3, "sae_spread": 0.6, "epias_center": 3.0, "epias_spread": 0.9, "weight": 0.25},
            {"label": "Staff designer",     "sae_center": 3, "sae_spread": 0.5, "epias_center": 3.5, "epias_spread": 0.8, "weight": 0.15},
            {"label": "Design lead",        "sae_center": 2, "sae_spread": 0.4, "epias_center": 4.0, "epias_spread": 0.7, "weight": 0.10},
            {"label": "Design systems eng", "sae_center": 4, "sae_spread": 0.5, "epias_center": 3.0, "epias_spread": 1.0, "weight": 0.05},
        ],
        "roles": ["Product Designer", "Senior Product Designer", "Staff Designer",
                   "Design Lead", "UX Researcher", "Design Systems Engineer",
                   "Interaction Designer", "Visual Designer"],
        "age_distribution": {"Under 25": 0.08, "25-34": 0.45, "35-44": 0.32,
                             "45-54": 0.10, "55+": 0.02, "Prefer not to say": 0.03},
    },

    "google-ux": {
        "description": "Google UX org — well-resourced, mixed automation levels",
        "n": 600,
        "personas": [
            {"label": "UX designer L3",     "sae_center": 1, "sae_spread": 0.5, "epias_center": 2.0, "epias_spread": 0.8, "weight": 0.15},
            {"label": "UX designer L4",     "sae_center": 2, "sae_spread": 0.5, "epias_center": 2.5, "epias_spread": 0.9, "weight": 0.25},
            {"label": "UX designer L5",     "sae_center": 2, "sae_spread": 0.6, "epias_center": 3.0, "epias_spread": 0.9, "weight": 0.20},
            {"label": "Interaction designer", "sae_center": 3, "sae_spread": 0.6, "epias_center": 2.5, "epias_spread": 1.0, "weight": 0.15},
            {"label": "UX engineer",        "sae_center": 3, "sae_spread": 0.5, "epias_center": 3.0, "epias_spread": 0.9, "weight": 0.10},
            {"label": "UX manager",         "sae_center": 2, "sae_spread": 0.5, "epias_center": 4.0, "epias_spread": 0.7, "weight": 0.10},
            {"label": "UX director",        "sae_center": 1, "sae_spread": 0.5, "epias_center": 4.5, "epias_spread": 0.6, "weight": 0.05},
        ],
        "roles": ["UX Designer", "Interaction Designer", "UX Engineer",
                   "UX Researcher", "UX Manager", "UX Director",
                   "Visual Designer", "Motion Designer"],
        "age_distribution": {"Under 25": 0.05, "25-34": 0.40, "35-44": 0.35,
                             "45-54": 0.15, "55+": 0.02, "Prefer not to say": 0.03},
    },

    "agency-creatives": {
        "description": "Creative agency collective — traditional craft + emerging AI",
        "n": 500,
        "personas": [
            {"label": "Traditional creative",  "sae_center": 0, "sae_spread": 0.4, "epias_center": 3.0, "epias_spread": 1.0, "weight": 0.20},
            {"label": "Junior creative",       "sae_center": 1, "sae_spread": 0.5, "epias_center": 1.5, "epias_spread": 0.8, "weight": 0.25},
            {"label": "Art director",          "sae_center": 1, "sae_spread": 0.6, "epias_center": 3.0, "epias_spread": 1.0, "weight": 0.20},
            {"label": "Digital designer",      "sae_center": 2, "sae_spread": 0.5, "epias_center": 2.0, "epias_spread": 0.9, "weight": 0.20},
            {"label": "Tech-savvy creative",   "sae_center": 3, "sae_spread": 0.5, "epias_center": 2.0, "epias_spread": 1.0, "weight": 0.10},
            {"label": "Creative technologist", "sae_center": 4, "sae_spread": 0.6, "epias_center": 2.5, "epias_spread": 1.0, "weight": 0.05},
        ],
        "roles": ["Art Director", "Creative Director", "Junior Designer",
                   "Visual Designer", "Copywriter", "Digital Designer",
                   "Creative Technologist", "Brand Strategist"],
        "age_distribution": {"Under 25": 0.15, "25-34": 0.30, "35-44": 0.25,
                             "45-54": 0.20, "55+": 0.05, "Prefer not to say": 0.05},
    },

    "fintech-design": {
        "description": "Fintech design teams — conservative adoption, high accountability",
        "n": 350,
        "personas": [
            {"label": "Compliance-aware designer", "sae_center": 1, "sae_spread": 0.4, "epias_center": 3.0, "epias_spread": 0.8, "weight": 0.20},
            {"label": "Product designer",          "sae_center": 2, "sae_spread": 0.5, "epias_center": 2.5, "epias_spread": 0.9, "weight": 0.30},
            {"label": "Senior designer",           "sae_center": 2, "sae_spread": 0.5, "epias_center": 3.5, "epias_spread": 0.8, "weight": 0.20},
            {"label": "Design lead",               "sae_center": 2, "sae_spread": 0.4, "epias_center": 4.0, "epias_spread": 0.7, "weight": 0.15},
            {"label": "Design engineer",           "sae_center": 3, "sae_spread": 0.5, "epias_center": 2.5, "epias_spread": 1.0, "weight": 0.10},
            {"label": "Head of design",            "sae_center": 1, "sae_spread": 0.4, "epias_center": 4.5, "epias_spread": 0.5, "weight": 0.05},
        ],
        "roles": ["Product Designer", "Senior Product Designer", "Design Lead",
                   "UX Researcher", "Design Engineer", "Head of Design",
                   "Compliance Designer", "Service Designer"],
        "age_distribution": {"Under 25": 0.05, "25-34": 0.35, "35-44": 0.35,
                             "45-54": 0.18, "55+": 0.04, "Prefer not to say": 0.03},
    },

    "startup-ai-native": {
        "description": "AI-native startups — high automation, low maturity (move fast)",
        "n": 300,
        "personas": [
            {"label": "Solo designer-engineer", "sae_center": 3, "sae_spread": 0.7, "epias_center": 1.5, "epias_spread": 0.8, "weight": 0.25},
            {"label": "AI product builder",     "sae_center": 4, "sae_spread": 0.5, "epias_center": 2.0, "epias_spread": 0.9, "weight": 0.25},
            {"label": "Vibe coder",             "sae_center": 3, "sae_spread": 0.8, "epias_center": 1.0, "epias_spread": 0.6, "weight": 0.20},
            {"label": "Technical founder",      "sae_center": 4, "sae_spread": 0.6, "epias_center": 2.5, "epias_spread": 1.0, "weight": 0.15},
            {"label": "Non-technical cofounder", "sae_center": 1, "sae_spread": 0.6, "epias_center": 2.0, "epias_spread": 1.0, "weight": 0.10},
            {"label": "ML engineer",            "sae_center": 4, "sae_spread": 0.4, "epias_center": 3.0, "epias_spread": 1.0, "weight": 0.05},
        ],
        "roles": ["Design Engineer", "Full-Stack Designer", "Technical Founder",
                   "AI Product Builder", "Frontend Engineer", "Founding Designer",
                   "ML Engineer", "Head of Product"],
        "age_distribution": {"Under 25": 0.20, "25-34": 0.45, "35-44": 0.25,
                             "45-54": 0.07, "55+": 0.01, "Prefer not to say": 0.02},
    },

    # -----------------------------------------------------------------------
    # Academic / education cohorts (~1,500 total)
    # -----------------------------------------------------------------------
    "mit-media-lab": {
        "description": "MIT Media Lab — high technical, L3-L4 skew",
        "n": 200,
        "personas": [
            {"label": "Masters student",     "sae_center": 2, "sae_spread": 0.6, "epias_center": 1.5, "epias_spread": 0.8, "weight": 0.20},
            {"label": "PhD researcher",      "sae_center": 3, "sae_spread": 0.5, "epias_center": 2.5, "epias_spread": 0.9, "weight": 0.30},
            {"label": "Research scientist",  "sae_center": 4, "sae_spread": 0.5, "epias_center": 3.0, "epias_spread": 1.0, "weight": 0.25},
            {"label": "PI / Faculty",        "sae_center": 3, "sae_spread": 0.6, "epias_center": 4.0, "epias_spread": 0.8, "weight": 0.15},
            {"label": "Visiting researcher", "sae_center": 2, "sae_spread": 0.7, "epias_center": 2.0, "epias_spread": 1.0, "weight": 0.10},
        ],
        "roles": ["Research Assistant", "PhD Researcher", "Research Scientist",
                   "Postdoc", "Faculty", "Visiting Researcher", "Lab Director"],
        "age_distribution": {"Under 25": 0.20, "25-34": 0.40, "35-44": 0.20,
                             "45-54": 0.12, "55+": 0.05, "Prefer not to say": 0.03},
    },

    "risd-design": {
        "description": "RISD design programs — craft-first, exploring AI cautiously",
        "n": 300,
        "personas": [
            {"label": "Undergrad student",   "sae_center": 0, "sae_spread": 0.5, "epias_center": 1.0, "epias_spread": 0.6, "weight": 0.30},
            {"label": "Grad student",        "sae_center": 1, "sae_spread": 0.5, "epias_center": 1.5, "epias_spread": 0.8, "weight": 0.25},
            {"label": "MFA candidate",       "sae_center": 1, "sae_spread": 0.6, "epias_center": 2.0, "epias_spread": 1.0, "weight": 0.20},
            {"label": "Faculty",             "sae_center": 0, "sae_spread": 0.5, "epias_center": 4.0, "epias_spread": 0.8, "weight": 0.10},
            {"label": "AI-curious student",  "sae_center": 2, "sae_spread": 0.6, "epias_center": 1.5, "epias_spread": 0.8, "weight": 0.10},
            {"label": "Visiting critic",     "sae_center": 1, "sae_spread": 0.7, "epias_center": 3.5, "epias_spread": 1.0, "weight": 0.05},
        ],
        "roles": ["Student", "Graduate Student", "MFA Candidate", "Faculty",
                   "Adjunct Professor", "Visiting Critic", "Design Fellow"],
        "age_distribution": {"Under 25": 0.45, "25-34": 0.30, "35-44": 0.10,
                             "45-54": 0.08, "55+": 0.04, "Prefer not to say": 0.03},
    },

    "hci-bootcamp": {
        "description": "Online HCI bootcamp cohort — career switchers, eager learners",
        "n": 500,
        "personas": [
            {"label": "Career switcher",     "sae_center": 1, "sae_spread": 0.5, "epias_center": 1.0, "epias_spread": 0.5, "weight": 0.35},
            {"label": "Junior with AI",      "sae_center": 2, "sae_spread": 0.6, "epias_center": 1.5, "epias_spread": 0.7, "weight": 0.25},
            {"label": "Experienced switcher", "sae_center": 1, "sae_spread": 0.5, "epias_center": 2.5, "epias_spread": 0.9, "weight": 0.20},
            {"label": "Self-taught dev",     "sae_center": 3, "sae_spread": 0.7, "epias_center": 1.5, "epias_spread": 0.8, "weight": 0.10},
            {"label": "Returning professional", "sae_center": 0, "sae_spread": 0.4, "epias_center": 2.0, "epias_spread": 1.0, "weight": 0.05},
            {"label": "Bootcamp instructor", "sae_center": 2, "sae_spread": 0.5, "epias_center": 3.5, "epias_spread": 0.8, "weight": 0.05},
        ],
        "roles": ["Student", "Career Switcher", "Junior Designer",
                   "Aspiring UX Designer", "Freelancer", "Self-Taught Dev",
                   "Instructor", "Mentor"],
        "age_distribution": {"Under 25": 0.20, "25-34": 0.40, "35-44": 0.25,
                             "45-54": 0.10, "55+": 0.02, "Prefer not to say": 0.03},
    },

    "global-south-design": {
        "description": "Global South design community — resource-constrained, high creativity",
        "n": 500,
        "personas": [
            {"label": "Self-taught designer",   "sae_center": 1, "sae_spread": 0.6, "epias_center": 1.5, "epias_spread": 0.8, "weight": 0.30},
            {"label": "Freelance designer",     "sae_center": 1, "sae_spread": 0.5, "epias_center": 2.5, "epias_spread": 1.0, "weight": 0.25},
            {"label": "Agency designer",        "sae_center": 2, "sae_spread": 0.6, "epias_center": 2.0, "epias_spread": 0.9, "weight": 0.20},
            {"label": "Tech startup designer",  "sae_center": 2, "sae_spread": 0.7, "epias_center": 1.5, "epias_spread": 0.8, "weight": 0.10},
            {"label": "NGO/civic designer",     "sae_center": 1, "sae_spread": 0.5, "epias_center": 3.0, "epias_spread": 1.0, "weight": 0.10},
            {"label": "Design educator",        "sae_center": 1, "sae_spread": 0.5, "epias_center": 3.5, "epias_spread": 0.9, "weight": 0.05},
        ],
        "roles": ["Freelance Designer", "Product Designer", "UI Designer",
                   "Graphic Designer", "Design Educator", "Agency Designer",
                   "Civic Designer", "Mobile Designer"],
        "age_distribution": {"Under 25": 0.25, "25-34": 0.40, "35-44": 0.20,
                             "45-54": 0.10, "55+": 0.02, "Prefer not to say": 0.03},
    },

    # -----------------------------------------------------------------------
    # Niche / edge-case cohorts (~1,000 total)
    # -----------------------------------------------------------------------
    "design-leadership": {
        "description": "Design leadership summit — high maturity, moderate automation",
        "n": 250,
        "personas": [
            {"label": "Design manager",     "sae_center": 1, "sae_spread": 0.5, "epias_center": 3.5, "epias_spread": 0.8, "weight": 0.25},
            {"label": "Head of design",     "sae_center": 2, "sae_spread": 0.5, "epias_center": 4.0, "epias_spread": 0.7, "weight": 0.25},
            {"label": "VP Design",          "sae_center": 1, "sae_spread": 0.5, "epias_center": 4.5, "epias_spread": 0.5, "weight": 0.20},
            {"label": "CDO",                "sae_center": 2, "sae_spread": 0.6, "epias_center": 5.0, "epias_spread": 0.5, "weight": 0.10},
            {"label": "Design ops lead",    "sae_center": 2, "sae_spread": 0.5, "epias_center": 3.5, "epias_spread": 0.8, "weight": 0.10},
            {"label": "Design advisor",     "sae_center": 1, "sae_spread": 0.6, "epias_center": 4.0, "epias_spread": 0.8, "weight": 0.10},
        ],
        "roles": ["Design Manager", "Head of Design", "VP Design",
                   "Chief Design Officer", "Design Ops Lead", "Design Advisor",
                   "Design Principal", "Design Fellow"],
        "age_distribution": {"Under 25": 0.01, "25-34": 0.15, "35-44": 0.40,
                             "45-54": 0.30, "55+": 0.10, "Prefer not to say": 0.04},
    },

    "ai-engineers": {
        "description": "AI Engineer World's Fair — high automation, variable maturity",
        "n": 400,
        "personas": [
            {"label": "ML engineer",         "sae_center": 4, "sae_spread": 0.5, "epias_center": 2.0, "epias_spread": 0.9, "weight": 0.25},
            {"label": "AI product builder",  "sae_center": 3, "sae_spread": 0.6, "epias_center": 2.5, "epias_spread": 1.0, "weight": 0.25},
            {"label": "Prompt engineer",     "sae_center": 3, "sae_spread": 0.5, "epias_center": 2.0, "epias_spread": 0.9, "weight": 0.15},
            {"label": "AI researcher",       "sae_center": 4, "sae_spread": 0.4, "epias_center": 3.0, "epias_spread": 1.0, "weight": 0.15},
            {"label": "Devtools builder",    "sae_center": 4, "sae_spread": 0.5, "epias_center": 3.5, "epias_spread": 0.8, "weight": 0.10},
            {"label": "AI hobbyist",         "sae_center": 2, "sae_spread": 0.8, "epias_center": 1.0, "epias_spread": 0.6, "weight": 0.10},
        ],
        "roles": ["ML Engineer", "AI Product Builder", "Prompt Engineer",
                   "AI Researcher", "DevTools Engineer", "Technical PM",
                   "Solutions Architect", "AI Hobbyist"],
        "age_distribution": {"Under 25": 0.12, "25-34": 0.45, "35-44": 0.28,
                             "45-54": 0.10, "55+": 0.02, "Prefer not to say": 0.03},
    },

    "gov-digital": {
        "description": "Government digital services — conservative, high accountability",
        "n": 350,
        "personas": [
            {"label": "Civil servant designer", "sae_center": 0, "sae_spread": 0.4, "epias_center": 2.5, "epias_spread": 1.0, "weight": 0.20},
            {"label": "GDS designer",           "sae_center": 1, "sae_spread": 0.5, "epias_center": 3.0, "epias_spread": 0.9, "weight": 0.25},
            {"label": "Service designer",       "sae_center": 1, "sae_spread": 0.5, "epias_center": 3.0, "epias_spread": 0.8, "weight": 0.20},
            {"label": "Content designer",       "sae_center": 1, "sae_spread": 0.5, "epias_center": 2.5, "epias_spread": 0.9, "weight": 0.15},
            {"label": "Digital lead",           "sae_center": 2, "sae_spread": 0.5, "epias_center": 4.0, "epias_spread": 0.7, "weight": 0.10},
            {"label": "Policy + design",        "sae_center": 0, "sae_spread": 0.3, "epias_center": 3.5, "epias_spread": 0.8, "weight": 0.10},
        ],
        "roles": ["Service Designer", "Content Designer", "Interaction Designer",
                   "User Researcher", "Digital Lead", "Policy Analyst",
                   "Accessibility Specialist", "Design Lead"],
        "age_distribution": {"Under 25": 0.05, "25-34": 0.25, "35-44": 0.35,
                             "45-54": 0.25, "55+": 0.07, "Prefer not to say": 0.03},
    },

    # -----------------------------------------------------------------------
    # Viral / social sharing cohorts (~3,000 total)
    # -----------------------------------------------------------------------
    "linkedin-maeda": {
        "description": "Maeda's LinkedIn post — ~800K followers, global, very mixed backgrounds",
        "n": 2500,
        "personas": [
            # Non-designers who are curious
            {"label": "Curious executive",     "sae_center": 0, "sae_spread": 0.5, "epias_center": 2.5, "epias_spread": 1.2, "weight": 0.10},
            {"label": "Non-design PM",         "sae_center": 1, "sae_spread": 0.6, "epias_center": 2.0, "epias_spread": 1.0, "weight": 0.10},
            # Mainstream designers
            {"label": "Early-career designer", "sae_center": 1, "sae_spread": 0.6, "epias_center": 1.5, "epias_spread": 0.8, "weight": 0.15},
            {"label": "Mid-career designer",   "sae_center": 2, "sae_spread": 0.6, "epias_center": 2.5, "epias_spread": 1.0, "weight": 0.20},
            {"label": "Senior designer",       "sae_center": 2, "sae_spread": 0.7, "epias_center": 3.0, "epias_spread": 1.0, "weight": 0.15},
            # Tech-forward
            {"label": "Design engineer",       "sae_center": 3, "sae_spread": 0.7, "epias_center": 2.0, "epias_spread": 1.0, "weight": 0.10},
            {"label": "AI practitioner",       "sae_center": 4, "sae_spread": 0.5, "epias_center": 2.5, "epias_spread": 1.0, "weight": 0.05},
            # Leadership
            {"label": "Design leader",         "sae_center": 1, "sae_spread": 0.5, "epias_center": 4.0, "epias_spread": 0.8, "weight": 0.08},
            # Global South / non-traditional
            {"label": "Global freelancer",     "sae_center": 1, "sae_spread": 0.6, "epias_center": 2.0, "epias_spread": 1.0, "weight": 0.05},
            {"label": "Student",               "sae_center": 1, "sae_spread": 0.7, "epias_center": 1.0, "epias_spread": 0.5, "weight": 0.02},
        ],
        "roles": ["Product Designer", "UX Designer", "Design Lead", "PM",
                   "Software Engineer", "Creative Director", "Design Manager",
                   "Freelancer", "Student", "VP Design", "Consultant",
                   "Brand Designer", "Entrepreneur", "Researcher",
                   "Design Educator", "Service Designer"],
        "age_distribution": {"Under 25": 0.08, "25-34": 0.30, "35-44": 0.32,
                             "45-54": 0.20, "55+": 0.06, "Prefer not to say": 0.04},
    },

    # -----------------------------------------------------------------------
    # Demo / tester cohorts
    # -----------------------------------------------------------------------
    "sxsw-2026-tester": {
        "description": "SXSW 2026 tester group — broad industry mix, 4K demo population",
        "n": 4000,
        "personas": [
            {"label": "Curious newcomer",    "sae_center": 0, "sae_spread": 0.5, "epias_center": 2.0, "epias_spread": 1.2, "weight": 0.07},
            {"label": "Marketing designer",  "sae_center": 1, "sae_spread": 0.6, "epias_center": 2.0, "epias_spread": 0.9, "weight": 0.20},
            {"label": "Product designer",    "sae_center": 2, "sae_spread": 0.7, "epias_center": 2.5, "epias_spread": 1.0, "weight": 0.25},
            {"label": "Design engineer",     "sae_center": 3, "sae_spread": 0.6, "epias_center": 2.0, "epias_spread": 1.0, "weight": 0.17},
            {"label": "AI-forward leader",   "sae_center": 4, "sae_spread": 0.5, "epias_center": 3.0, "epias_spread": 1.0, "weight": 0.08},
            {"label": "Design director",     "sae_center": 1, "sae_spread": 0.4, "epias_center": 4.0, "epias_spread": 0.7, "weight": 0.05},
            {"label": "Startup founder",     "sae_center": 3, "sae_spread": 0.8, "epias_center": 2.0, "epias_spread": 1.2, "weight": 0.04},
            {"label": "Design steward",      "sae_center": 1, "sae_spread": 1.2, "epias_center": 5.0, "epias_spread": 0.5, "weight": 0.06},
            {"label": "AI steward",          "sae_center": 4, "sae_spread": 1.0, "epias_center": 5.0, "epias_spread": 0.5, "weight": 0.04},
            {"label": "Full auto pioneer",   "sae_center": 5, "sae_spread": 0.4, "epias_center": 3.0, "epias_spread": 1.2, "weight": 0.04},
        ],
        "roles": ["Product Designer", "UX Designer", "Design Lead", "UX Researcher",
                   "Design Engineer", "Creative Director", "Visual Designer",
                   "Design Manager", "Frontend Dev", "PM", "Startup Founder",
                   "Design Strategist", "Content Designer"],
        "age_distribution": {"Under 25": 0.10, "25-34": 0.35, "35-44": 0.30,
                             "45-54": 0.15, "55+": 0.05, "Prefer not to say": 0.05},
    },

    "sxsw-2026-test-group": {
        "description": "Small test group — verifying group ID functionality",
        "n": 150,
        "personas": [
            {"label": "Mixed tester",  "sae_center": 2, "sae_spread": 1.0, "epias_center": 2.5, "epias_spread": 1.2, "weight": 1.0},
        ],
        "roles": ["Tester"],
        "age_distribution": {"25-34": 0.50, "35-44": 0.50},
    },

    "other-test-group": {
        "description": "Secondary test group — alternative distribution for comparison",
        "n": 100,
        "personas": [
            {"label": "Tech-heavy tester",  "sae_center": 3, "sae_spread": 0.8, "epias_center": 1.5, "epias_spread": 0.8, "weight": 0.5},
            {"label": "Leader tester",       "sae_center": 1, "sae_spread": 0.6, "epias_center": 4.0, "epias_spread": 0.7, "weight": 0.5},
        ],
        "roles": ["Tester"],
        "age_distribution": {"25-34": 0.50, "35-44": 0.50},
    },

    "sxsw-livestream": {
        "description": "SXSW livestream viewers — remote, couldn't attend in person",
        "n": 500,
        "personas": [
            {"label": "Remote viewer",       "sae_center": 1, "sae_spread": 0.7, "epias_center": 2.0, "epias_spread": 1.0, "weight": 0.30},
            {"label": "Design curious",      "sae_center": 1, "sae_spread": 0.6, "epias_center": 1.5, "epias_spread": 0.8, "weight": 0.25},
            {"label": "International pro",   "sae_center": 2, "sae_spread": 0.6, "epias_center": 2.5, "epias_spread": 1.0, "weight": 0.20},
            {"label": "Tech professional",   "sae_center": 3, "sae_spread": 0.6, "epias_center": 2.0, "epias_spread": 1.0, "weight": 0.15},
            {"label": "Senior leader",       "sae_center": 1, "sae_spread": 0.5, "epias_center": 3.5, "epias_spread": 0.9, "weight": 0.10},
        ],
        "roles": ["Designer", "Product Manager", "Engineer", "Design Lead",
                   "Freelancer", "Student", "Consultant", "Researcher"],
        "age_distribution": {"Under 25": 0.12, "25-34": 0.35, "35-44": 0.28,
                             "45-54": 0.15, "55+": 0.06, "Prefer not to say": 0.04},
    },
}


# ---------------------------------------------------------------------------
# Simulation engine
# ---------------------------------------------------------------------------

def _clamp(val, lo, hi):
    return max(lo, min(hi, val))


def _weighted_choice(items, weights):
    """Pick from items using weights (must sum to ~1)."""
    return random.choices(items, weights=weights, k=1)[0]


def _sample_level(center, spread):
    """Sample an SAE level (0-5) from a Gaussian centered on `center`."""
    raw = random.gauss(center, spread)
    return _clamp(round(raw), 0, 5)


def _sample_stage(center, spread):
    """Sample an EPIAS stage number (1-5) from a Gaussian."""
    raw = random.gauss(center, spread)
    return _clamp(round(raw), 1, 5)


NUM_TO_STAGE = {1: "E", 2: "P", 3: "I", 4: "A", 5: "S"}


def simulate_agent(persona):
    """Simulate one agent taking the full assessment.

    Returns (answers_dict, metadata_dict).
    """
    answers = {}

    # Stage 1: SAE questions — each answer is a level 0-5
    for q in SAE_QUESTIONS:
        answers[q["id"]] = _sample_level(persona["sae_center"], persona["sae_spread"])

    # Score SAE to determine which EPIAS questions to answer
    partial_score = score_assessment(answers)
    sae_level = partial_score["sae_level"]

    # Stage 2: EPIAS questions for the determined SAE level
    epias_qs = EPIAS_QUESTIONS.get(sae_level, [])
    for q in epias_qs:
        stage_num = _sample_stage(persona["epias_center"], persona["epias_spread"])
        answers[q["id"]] = NUM_TO_STAGE[stage_num]

    # Final score
    final_score = score_assessment(answers)
    return answers, final_score


def simulate_cohort(cohort_code, profile, store=False, scale=1.0):
    """Simulate all agents in a cohort and optionally store results."""
    results = []
    n = max(1, round(profile["n"] * scale))
    personas = profile["personas"]
    persona_weights = [p["weight"] for p in personas]
    age_ranges = list(profile["age_distribution"].keys())
    age_weights = list(profile["age_distribution"].values())
    roles = profile["roles"]

    store_fn = None
    if store:
        from storage import store_result
        store_fn = store_result

    t0 = time.time()
    batch_size = 100

    for i in range(n):
        persona = _weighted_choice(personas, persona_weights)
        answers, score = simulate_agent(persona)
        age = _weighted_choice(age_ranges, age_weights)
        role = random.choice(roles)

        result = {
            "agent_id": i + 1,
            "persona": persona["label"],
            "sae_level": score["sae_level"],
            "sae_name": score["sae_name"],
            "epias_stage": score["epias_stage"],
            "epias_name": score["epias_name"],
            "age_range": age,
            "role": role,
        }
        results.append(result)

        if store_fn:
            store_fn(
                sae_level=score["sae_level"],
                epias_stage=score["epias_stage"],
                cohort=cohort_code,
                age_range=age,
                role=role,
            )

        # Progress reporting for large cohorts
        if (i + 1) % batch_size == 0 or i == n - 1:
            elapsed = time.time() - t0
            rate = (i + 1) / elapsed if elapsed > 0 else 0
            print(f"    [{i+1:>5}/{n}] {rate:.0f} agents/sec", end="\r")

    if n >= batch_size:
        elapsed = time.time() - t0
        print(f"    Completed {n} agents in {elapsed:.1f}s ({n/elapsed:.0f}/sec)   ")

    return results


def print_summary(cohort_code, results):
    """Print a distribution summary for a simulated cohort."""
    print(f"\n{'='*60}")
    print(f"  {cohort_code}  ({len(results)} agents)")
    print(f"{'='*60}")

    # SAE distribution
    sae_counts = {}
    for r in results:
        sae_counts[r["sae_level"]] = sae_counts.get(r["sae_level"], 0) + 1

    print("\n  SAE Level Distribution:")
    for level in range(6):
        count = sae_counts.get(level, 0)
        bar = "#" * count
        print(f"    L{level}: {bar} ({count})")

    # EPIAS distribution
    epias_counts = {}
    for r in results:
        epias_counts[r["epias_stage"]] = epias_counts.get(r["epias_stage"], 0) + 1

    print("\n  EPIAS Stage Distribution:")
    for stage in ["E", "P", "I", "A", "S"]:
        count = epias_counts.get(stage, 0)
        bar = "#" * count
        print(f"    {stage}: {bar} ({count})")

    # Heatmap grid
    print("\n  Heatmap Grid (SAE x EPIAS):")
    print(f"       {'E':>4} {'P':>4} {'I':>4} {'A':>4} {'S':>4}")
    for level in range(6):
        row = []
        for stage in ["E", "P", "I", "A", "S"]:
            c = sum(1 for r in results if r["sae_level"] == level and r["epias_stage"] == stage)
            row.append(f"{c:>4}")
        print(f"    L{level} {''.join(row)}")

    # Persona breakdown
    print("\n  Persona Breakdown:")
    persona_counts = {}
    for r in results:
        persona_counts[r["persona"]] = persona_counts.get(r["persona"], 0) + 1
    for p, c in sorted(persona_counts.items(), key=lambda x: -x[1]):
        print(f"    {p}: {c}")


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def print_cross_cohort_analysis(all_results):
    """Print comparative analysis across all cohorts."""
    print(f"\n{'='*70}")
    print(f"  CROSS-COHORT COMPARATIVE ANALYSIS")
    print(f"{'='*70}")

    # Per-cohort mean SAE and EPIAS
    stage_to_num = {"E": 1, "P": 2, "I": 3, "A": 4, "S": 5}
    print(f"\n  {'Cohort':<22} {'N':>5} {'Mean SAE':>9} {'Mean EPIAS':>11} {'Profile':>10}")
    print(f"  {'-'*22} {'-'*5} {'-'*9} {'-'*11} {'-'*10}")

    for code, results in all_results.items():
        n = len(results)
        mean_sae = sum(r["sae_level"] for r in results) / n
        mean_epias = sum(stage_to_num[r["epias_stage"]] for r in results) / n

        # Classify the cohort profile
        if mean_sae >= 3 and mean_epias >= 3:
            profile = "Advanced"
        elif mean_sae >= 3 and mean_epias < 3:
            profile = "Tech-first"
        elif mean_sae < 2 and mean_epias >= 3:
            profile = "Craft-deep"
        elif mean_sae < 2 and mean_epias < 2:
            profile = "Emerging"
        else:
            profile = "Balanced"

        print(f"  {code:<22} {n:>5} {mean_sae:>9.2f} {mean_epias:>11.2f} {profile:>10}")

    # Global heatmap
    all_flat = []
    for results in all_results.values():
        all_flat.extend(results)

    print(f"\n  GLOBAL HEATMAP ({len(all_flat)} total responses):")
    print(f"       {'E':>6} {'P':>6} {'I':>6} {'A':>6} {'S':>6} {'Total':>7}")
    for level in range(6):
        row = []
        row_total = 0
        for stage in ["E", "P", "I", "A", "S"]:
            c = sum(1 for r in all_flat if r["sae_level"] == level and r["epias_stage"] == stage)
            row.append(f"{c:>6}")
            row_total += c
        print(f"    L{level} {''.join(row)} {row_total:>7}")

    # Cell coverage analysis
    populated = 0
    sparse = []
    for level in range(6):
        for stage in ["E", "P", "I", "A", "S"]:
            c = sum(1 for r in all_flat if r["sae_level"] == level and r["epias_stage"] == stage)
            if c > 0:
                populated += 1
            if 0 < c < 5:
                sparse.append(f"L{level}_{stage}({c})")

    print(f"\n  Cell coverage: {populated}/30 cells populated ({populated/30*100:.0f}%)")
    if sparse:
        print(f"  Sparse cells (<5 responses): {', '.join(sparse)}")

    # Edge case report
    print(f"\n  EDGE CASES & INTERPRETABILITY:")
    l5_count = sum(1 for r in all_flat if r["sae_level"] == 5)
    l0_count = sum(1 for r in all_flat if r["sae_level"] == 0)
    steward_count = sum(1 for r in all_flat if r["epias_stage"] == "S")
    print(f"    L5 (Full Automation): {l5_count} ({l5_count/len(all_flat)*100:.1f}%) — should be rare")
    print(f"    L0 (Manual):         {l0_count} ({l0_count/len(all_flat)*100:.1f}%) — craft-only baseline")
    print(f"    S (Steward):         {steward_count} ({steward_count/len(all_flat)*100:.1f}%) — organizational leaders")

    # Maeda's key insight test: are there more high-maturity low-SAE than low-maturity high-SAE?
    high_mat_low_sae = sum(1 for r in all_flat if r["sae_level"] <= 1 and r["epias_stage"] in ("A", "S"))
    low_mat_high_sae = sum(1 for r in all_flat if r["sae_level"] >= 4 and r["epias_stage"] in ("E",))
    print(f"\n  MAEDA INSIGHT TEST:")
    print(f"    'An S-Steward at L1 > E-Explorer at L4'")
    print(f"    High-maturity, low-SAE (L0-1, A/S): {high_mat_low_sae}")
    print(f"    Low-maturity, high-SAE (L4-5, E):   {low_mat_high_sae}")
    if high_mat_low_sae > low_mat_high_sae:
        print(f"    -> Distribution validates the insight (craft-deep > tech-shallow)")
    else:
        print(f"    -> Distribution challenges the insight — may need persona tuning")


def main():
    parser = argparse.ArgumentParser(description="Simulate cohort assessment responses")
    parser.add_argument("--store", action="store_true",
                        help="Store results to active backend (in-memory or Firestore)")
    parser.add_argument("--firestore", action="store_true",
                        help="Force FIRESTORE_ENABLED=true")
    parser.add_argument("--cohorts", nargs="*", default=None,
                        help="Specific cohort codes to simulate (default: all)")
    parser.add_argument("--seed", type=int, default=42,
                        help="Random seed for reproducibility")
    parser.add_argument("--scale", type=float, default=1.0,
                        help="Scale factor for cohort sizes (e.g., 2.0 = double)")
    parser.add_argument("--json", type=str, default=None,
                        help="Export all results to a JSON file")
    args = parser.parse_args()

    if args.firestore:
        os.environ["FIRESTORE_ENABLED"] = "true"

    random.seed(args.seed)

    cohorts = args.cohorts or list(COHORT_PROFILES.keys())
    all_results = {}
    total = 0
    t_start = time.time()

    for code in cohorts:
        if code not in COHORT_PROFILES:
            print(f"  Unknown cohort: {code}, skipping")
            continue

        profile = COHORT_PROFILES[code]
        n_scaled = max(1, round(profile["n"] * args.scale))
        print(f"\nSimulating {n_scaled} agents for '{code}'...")
        print(f"  {profile['description']}")

        results = simulate_cohort(code, profile, store=args.store, scale=args.scale)
        print_summary(code, results)
        all_results[code] = results
        total += len(results)

    # Cross-cohort analysis
    if len(all_results) > 1:
        print_cross_cohort_analysis(all_results)

    elapsed = time.time() - t_start
    print(f"\n{'='*70}")
    print(f"  Total: {total} simulated responses across {len(all_results)} cohorts")
    print(f"  Elapsed: {elapsed:.1f}s ({total/elapsed:.0f} agents/sec)")
    if args.store:
        backend = "Firestore" if os.environ.get("FIRESTORE_ENABLED", "").lower() in ("1", "true") else "in-memory"
        print(f"  Stored to: {backend}")
    else:
        print(f"  DRY RUN — no results stored. Use --store to persist.")

    if args.json:
        export = {code: results for code, results in all_results.items()}
        with open(args.json, "w", encoding="utf-8") as f:
            json.dump(export, f, indent=2)
        print(f"  Exported to: {args.json}")

    print(f"{'='*70}\n")


if __name__ == "__main__":
    main()
