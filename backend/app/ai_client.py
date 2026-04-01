import os
from typing import Dict, List, Optional

import google.generativeai as genai

_API_KEY = os.getenv("GEMINI_API_KEY") or os.getenv("GOOGLE_API_KEY")
genai.configure(api_key=_API_KEY)

_MODEL_NAME = "models/gemini-2.5-flash"


def _system_prompt() -> str:
    return (
        "You are a Morgan State University academic advisor assistant. "
        "Use only the provided Morgan State advising context and student profile for factual claims. "
        "The retrieved context may include courses, degree requirements, departments, faculty, or support resources. "
        "Do not invent prerequisites, instructors, policies, deadlines, or degree requirements. "
        "If the context is insufficient, say that clearly and suggest the best next contact point. "
        "Be practical, supportive, and concise. "
        "Prefer plain text without markdown emphasis, and keep answers easy for students to skim."
    )


def generate_ai_reply(
    history: List[Dict[str, str]],
    extra_context: Optional[str] = None,
) -> str:
    contents = [{"role": "user", "parts": [_system_prompt()]}]

    if extra_context:
        contents.append(
            {
                "role": "user",
                "parts": [f"Here is current advising context to use:\n{extra_context}"],
            }
        )

    for msg in history:
        role = "model" if msg["role"] == "assistant" else "user"
        contents.append({"role": role, "parts": [msg["content"]]})

    model = genai.GenerativeModel(_MODEL_NAME)
    response = model.generate_content(contents)
    text = getattr(response, "text", None)

    if not text:
        return (
            "I'm sorry, I'm having trouble processing that request right now. "
            "Please try again or contact your advisor."
        )

    return text.strip()
