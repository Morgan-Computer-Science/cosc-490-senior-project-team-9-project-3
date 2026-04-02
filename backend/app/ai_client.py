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
    attachment_path: Optional[str] = None,
    attachment_mime_type: Optional[str] = None,
    attachment_summary: Optional[str] = None,
    attachment_document_type: Optional[str] = None,
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
    uploaded_file = None
    if attachment_path:
        uploaded_file = genai.upload_file(
            attachment_path,
            mime_type=attachment_mime_type,
            display_name=attachment_summary,
        )
        contents.append(
            {
                "role": "user",
                "parts": [
                    (
                        "Analyze the attached file together with the Morgan State advising context. "
                        f"The attachment should be treated as: {attachment_document_type or 'supporting document'}. "
                        "If the file is a schedule, degree audit, transcript, or form, extract only the details that matter for advising. "
                        "If the file is an image or screenshot, describe only what is relevant to the student's advising question."
                    ),
                    uploaded_file,
                ],
            }
        )

    try:
        response = model.generate_content(contents)
    finally:
        if uploaded_file is not None:
            try:
                genai.delete_file(uploaded_file.name)
            except Exception:
                pass
    text = getattr(response, "text", None)

    if not text:
        return (
            "I'm sorry, I'm having trouble processing that request right now. "
            "Please try again or contact your advisor."
        )

    return text.strip()
