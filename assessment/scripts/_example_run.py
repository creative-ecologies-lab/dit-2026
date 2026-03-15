"""Single-question example run — review before doing all 60."""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from openai import OpenAI
from assessment.questions import EPIAS_QUESTIONS_DESIGN

client = OpenAI()
q = EPIAS_QUESTIONS_DESIGN[0][0]

print("Question ID:", q["id"])
print("Dimension:", q["dimension"])
print("Current stem:", q["question"])
print()

options_text = "\n".join(f"  {opt['stage']}: {opt['text']}" for opt in q["options"])

SYSTEM = (
    "You are an expert survey designer specializing in professional self-assessment "
    "instruments for product designers and UX researchers. You write concise, precise "
    "question stems for practice-maturity assessments."
)

USER = "\n".join([
    "This is a self-assessment survey for product designers and UX researchers measuring",
    "AI practice maturity. Respondents first answer 6 SAE questions (like 'Which best",
    "describes how you regularly use AI in your work?') that score them to a level L0-L5.",
    "They then see 5 EPIAS questions for their level. Each EPIAS question has 5 options",
    "ranging from E (still figuring it out, inconsistent) through P (reliable but personal),",
    "I (documented, others can follow it), A (packaged, teams run it without your help),",
    "to S (you set the org-wide standard and coach others).",
    "",
    "The current EPIAS stems are too wordy -- they describe a specific scenario",
    "('When you get a vague request from a PM...') and read like 'describe what you do.'",
    "They should be short plain questions like the SAE ones: 'Which best describes your X practice?'",
    "",
    "Rules for the new stem:",
    "- One plain question, 15 words or fewer",
    "- Starts with 'Which best describes...' or similar direct phrasing",
    "- Names the specific dimension so the respondent knows what's being assessed",
    "- No sub-clauses, no dashes, no explanation of the spectrum",
    "- Reads naturally -- a person should understand it immediately",
    "",
    "Good examples of the pattern:",
    "  'Which best describes your design-handoff practice?'",
    "  'Which best describes how you track AI-influenced design decisions?'",
    "  'Which best describes your prompt organization practice?'",
    "",
    "Now write a new stem for this question:",
    "",
    "Track: Product Design",
    "SAE Level: L0 (no AI -- manual design workflow)",
    "Dimension: " + q["dimension"],
    "Current stem: " + q["question"],
    "",
    "Options the stem must introduce (DO NOT change these):",
    options_text,
    "",
    "Return ONLY the new question stem -- no quotes, no explanation.",
])

resp = client.responses.create(
    model="gpt-5.1",
    input=[
        {"role": "system", "content": [{"type": "input_text", "text": SYSTEM}]},
        {"role": "user", "content": [{"type": "input_text", "text": USER}]},
    ],
    max_output_tokens=2000,
    reasoning={"effort": "medium"},
)

result = ""
if hasattr(resp, "output_text") and resp.output_text:
    result = resp.output_text.strip()
elif hasattr(resp, "output") and resp.output:
    for block in resp.output:
        content = getattr(block, "content", None)
        if not content:
            continue
        for item in content:
            text = getattr(item, "text", None)
            if text:
                result = text.strip()
                break
        if result:
            break

if not result:
    raise ValueError(f"No text in response: {resp}")

print("NEW STEM:", result)
