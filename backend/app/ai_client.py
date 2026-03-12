import os
from typing import List, Literal, Dict, Optional
import google.generativeai as genai

genai.configure(api_key=os.getenv("GEMINI_API_KEY"))

_MODEL_NAME = "models/gemini-2.5-flash"

def _system_prompt() -> str:
    """
    Refined behavior for the Morgan State Faculty Advisor.
    """
    return (
        "You are a Morgan State University Faculty Advisor. "
        "Your goal is to help students graduate on time by providing accurate academic guidance. "
        "Use the official course and faculty information provided from the Morgan State database to answer questions. "
        "Be encouraging, professional, and proactive in suggesting relevant courses. "
        "If you are unsure of specific data, suggest the student contact the appropriate department office."
    )

def generate_ai_reply(
    history: List[Dict[str, str]],
    extra_context: Optional[str] = None,
) -> str:
    contents = [
        {
            "role": "user",
            "parts": [_system_prompt()],
        }
    ]

    if extra_context:
        contents.append(
            {
                "role": "user",
                "parts": [
                    "Here is current course data from the Morgan State database to help you answer:\\n"
                    + extra_context
                ],
            }
        )

    for msg in history:
        role = "model" if msg["role"] == "assistant" else "user"
        contents.append({"role": role, "parts": [msg["content"]]})

    model = genai.GenerativeModel(_MODEL_NAME)
    response = model.generate_content(contents)

    text = getattr(response, "text", None)
    if not text:
        return "I'm sorry, I'm having trouble processing that request. Please try again or contact your advisor."
    return text