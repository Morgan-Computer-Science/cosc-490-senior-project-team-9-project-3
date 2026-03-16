import os
from typing import List, Dict, Optional
import google.generativeai as genai

genai.configure(api_key=os.getenv("GEMINI_API_KEY"))

_MODEL_NAME = "models/gemini-2.5-flash"


def _system_prompt() -> str:
    return (
        "You are a Morgan State University academic advisor assistant. "
        "Answer using only the provided Morgan State course and advising data when making factual claims. "
        "If instructor information is present in the provided context, state it directly. "
        "Do not say information is missing if it appears in the provided context. "
        "Do not invent course details, instructors, faculty assignments, or university policies. "
        "If the provided data is insufficient, clearly say so and recommend contacting the correct department. "
        "Be concise, accurate, supportive, and practical."
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
                    "Here is current Morgan State data to use when answering:\n"
                    + extra_context
                ],
            }
        )

    for msg in history:
        role = "model" if msg["role"] == "assistant" else "user"
        contents.append(
            {
                "role": role,
                "parts": [msg["content"]],
            }
        )

    model = genai.GenerativeModel(_MODEL_NAME)
    response = model.generate_content(contents)

    text = getattr(response, "text", None)
    if not text:
        return (
            "I'm sorry, I'm having trouble processing that request right now. "
            "Please try again or contact your advisor."
        )

    return text