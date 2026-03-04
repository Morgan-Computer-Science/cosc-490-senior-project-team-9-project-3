# app/ai_client.py

import os
from typing import List, Literal, Dict, Optional

import google.generativeai as genai

# Configure Gemini with API key from environment
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))

ModelRole = Literal["user", "assistant", "system"]

# Central place to change the model name if needed
_MODEL_NAME = "models/gemini-2.5-flash"


def _system_prompt() -> str:
    """
    Core behavior of the Morgan State AI Advisor.
    """
    return (
        "You are the Morgan State University AI Advisor. "
        "You assist Morgan students with academic advising, degree planning, "
        "course selection, registration, campus resources, and general guidance. "
        "Use the official course and faculty information provided to you when answering. "
        "If you are unsure or the data is missing, say you are not certain and suggest "
        "contacting the appropriate Morgan State office."
    )


def generate_ai_reply(
    history: List[Dict[str, str]],
    extra_context: Optional[str] = None,
) -> str:
    """
    Generate an AI reply given chat history and optional catalog/faculty context.

    history: list of dicts like:
        [{ "role": "user" | "assistant", "content": "..." }, ...]
    extra_context: optional string with course/faculty data from the database.
    """
    # Start with the system prompt
    contents = [
        {
            "role": "user",
            "parts": [_system_prompt()],
        }
    ]

    # Inject course catalog / faculty info IF we have it
    if extra_context:
        contents.append(
            {
                "role": "user",
                "parts": [
                    "Here is structured information from the Morgan State database:\n"
                    + extra_context
                ],
            }
        )

    # Then add conversation history
    for msg in history:
        role = "model" if msg["role"] == "assistant" else "user"
        contents.append({"role": role, "parts": [msg["content"]]})

    model = genai.GenerativeModel(_MODEL_NAME)
    response = model.generate_content(contents)

    # To always return a none empty string, never non 
    text = getattr(response, "text", None)
    if not text:
        return (
            "I'm sorry, I couldn't generate a full response right now. "
            "Please try rephrasing your question or contact a human advisor."
        )

    return text.strip()