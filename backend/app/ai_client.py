import logging
import os
from pathlib import Path
from typing import Dict, List, Optional

import google.generativeai as genai
from dotenv import load_dotenv

logger = logging.getLogger(__name__)
_BACKEND_ENV_PATH = Path(__file__).resolve().parents[1] / ".env"

_MODEL_NAME = "models/gemini-2.5-flash"


def _get_runtime_api_key() -> str:
    load_dotenv(_BACKEND_ENV_PATH)
    api_key = os.getenv("GEMINI_API_KEY") or os.getenv("GOOGLE_API_KEY")
    if not api_key:
        raise RuntimeError("Gemini API key is not configured in backend/.env or the process environment.")
    return api_key


def _build_model():
    genai.configure(api_key=_get_runtime_api_key())
    return genai.GenerativeModel(_MODEL_NAME)


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


def _attachment_prompt(document_type: Optional[str]) -> str:
    normalized_type = (document_type or "supporting document").replace("_", " ")
    guidance_map = {
        "schedule": (
            "Focus on listed courses, overall load balance, likely sequencing concerns, and anything the student "
            "should double-check with advising before registration."
        ),
        "transcript": (
            "Focus on courses that appear completed, what that suggests about likely next classes, and any limits "
            "in the transcript evidence."
        ),
        "degree_audit": (
            "Focus on remaining requirements, progress signals, requirement gaps, and any parts of the audit that "
            "still need advisor confirmation."
        ),
        "academic_form": (
            "Focus on what action the form appears to require, which office is most relevant, and any missing "
            "details the student should confirm."
        ),
        "image_screenshot": (
            "Describe only the parts of the screenshot that matter for advising, planning, deadlines, or next steps."
        ),
        "pdf_document": (
            "Summarize the advising-relevant points from the PDF and avoid repeating administrative filler."
        ),
        "text_document": (
            "Pull out the advising-relevant facts from the text and tie them back to the student's question."
        ),
    }
    specific_guidance = guidance_map.get(document_type or "", guidance_map["text_document"])
    return (
        "Analyze the attached file together with the Morgan State advising context. "
        f"The attachment should be treated as: {normalized_type}. "
        "Use only information you can actually infer from the file and provided context. "
        "If the file is ambiguous, say what is unclear instead of guessing. "
        f"{specific_guidance}"
    )


def extract_text_from_attachment(
    attachment_path: str,
    attachment_mime_type: Optional[str] = None,
    attachment_document_type: Optional[str] = None,
    attachment_summary: Optional[str] = None,
) -> Optional[str]:
    if not attachment_path:
        return None

    try:
        model = _build_model()
    except RuntimeError:
        return None
    uploaded_file = None
    try:
        uploaded_file = genai.upload_file(
            attachment_path,
            mime_type=attachment_mime_type,
            display_name=attachment_summary,
        )
        response = model.generate_content(
            [
                (
                    "Extract readable text from this attachment for Morgan State advising workflows. "
                    f"Treat the file as {((attachment_document_type or 'supporting document').replace('_', ' '))}. "
                    "Return only the extracted text content with minimal cleanup. "
                    "If the file contains a schedule, transcript, degree audit, or form, preserve course codes, headings, and important labels. "
                    "Do not summarize or explain."
                ),
                uploaded_file,
            ]
        )
        text = getattr(response, "text", None)
        if not text:
            return None
        cleaned = text.strip()
        return cleaned or None
    except Exception:
        logger.exception("Gemini OCR extraction failed for attachment '%s'.", attachment_summary or attachment_path)
        return None
    finally:
        if uploaded_file is not None:
            try:
                genai.delete_file(uploaded_file.name)
            except Exception:
                pass


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

    model = _build_model()
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
                    _attachment_prompt(attachment_document_type),
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
