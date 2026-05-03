from typing import Optional


WELLNESS_TOKENS = {
    "anxious",
    "anxiety",
    "burned",
    "burnt",
    "counseling",
    "depressed",
    "depression",
    "mental",
    "overwhelmed",
    "panic",
    "sad",
    "stress",
    "stressed",
    "struggling",
    "suicidal",
    "upset",
    "worried",
}

PLANNING_TOKENS = {
    "after",
    "classes",
    "graduate",
    "next",
    "plan",
    "planning",
    "requirement",
    "requirements",
    "schedule",
    "semester",
    "take",
}

CAREER_TOKENS = {
    "career",
    "internship",
    "job",
    "resume",
}


def analyze_student_state(message: str, major: Optional[str] = None) -> dict[str, object]:
    lowered = message.lower()
    matched_wellness = sorted(token for token in WELLNESS_TOKENS if token in lowered)
    matched_planning = sorted(token for token in PLANNING_TOKENS if token in lowered)
    matched_career = sorted(token for token in CAREER_TOKENS if token in lowered)

    if matched_wellness:
        intent = "wellness_support"
        tone = "distressed"
    elif matched_planning:
        intent = "degree_planning"
        tone = "goal_oriented"
    elif matched_career:
        intent = "career_guidance"
        tone = "exploratory"
    else:
        intent = "general_advising"
        tone = "neutral"

    return {
        "intent": intent,
        "emotional_tone": tone,
        "needs_support": bool(matched_wellness),
        "matched_signals": matched_wellness or matched_planning or matched_career,
        "major": major,
    }
