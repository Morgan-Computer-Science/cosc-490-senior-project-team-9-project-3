from dataclasses import dataclass, field
from io import BytesIO
from pathlib import Path
import re
import tempfile
from typing import Optional

from fastapi import HTTPException, UploadFile, status

from .ai_client import extract_text_from_attachment
from .config import MAX_ATTACHMENT_BYTES
from .rag import extract_all_course_codes, extract_attachment_course_signals, extract_known_course_codes

TEXT_MIME_PREFIXES = ("text/",)
TEXT_MIME_TYPES = {
    "application/json",
    "application/xml",
    "application/javascript",
}
IMAGE_MIME_PREFIXES = ("image/",)
PDF_MIME_TYPE = "application/pdf"
ALLOWED_ATTACHMENT_SUFFIXES = {".pdf", ".txt", ".md", ".csv", ".json", ".png", ".jpg", ".jpeg", ".webp"}
ALLOWED_ATTACHMENT_MIME_PREFIXES = TEXT_MIME_PREFIXES + IMAGE_MIME_PREFIXES
ALLOWED_ATTACHMENT_MIME_TYPES = TEXT_MIME_TYPES | {PDF_MIME_TYPE}


@dataclass(frozen=True)
class DocumentCourseSignals:
    completed_codes: tuple[str, ...] = ()
    planned_codes: tuple[str, ...] = ()
    remaining_codes: tuple[str, ...] = ()
    matched_course_codes: tuple[str, ...] = ()
    unknown_course_codes: tuple[str, ...] = ()


@dataclass(frozen=True)
class TranscriptSummary:
    gpa: Optional[str] = None
    earned_credits: Optional[str] = None
    standing: Optional[str] = None
    advisor: Optional[str] = None


@dataclass(frozen=True)
class AttachmentContext:
    filename: str
    content_type: str
    context_text: str
    summary: str
    extracted_text: Optional[str] = None
    temp_path: Optional[str] = None
    document_type: str = "generic_file"
    extraction_method: str = "none"
    confidence_note: Optional[str] = None
    signals: DocumentCourseSignals = field(default_factory=DocumentCourseSignals)
    transcript_summary: TranscriptSummary = field(default_factory=TranscriptSummary)

    @property
    def detected_document_type(self) -> str:
        return self.document_type


def _write_temp_attachment(filename: str, file_bytes: bytes) -> str:
    suffix = Path(filename).suffix or ".bin"
    with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as temp_file:
        temp_file.write(file_bytes)
        return temp_file.name


def _normalize_text(text: str) -> str:
    return re.sub(r"\s+", " ", text).strip()


def _normalize_multiline_text(text: str) -> str:
    lines = [re.sub(r"[ \t]+", " ", line).strip() for line in text.splitlines()]
    return "\n".join(line for line in lines if line).strip()


def _build_confidence_note(extracted_text: Optional[str], extraction_method: str) -> Optional[str]:
    if extraction_method == "none":
        return "This file type could not be fully analyzed. Review it manually before making important academic decisions."
    if not extracted_text or len(_normalize_text(extracted_text)) < 80:
        return "Extraction was limited. Review the original document before making important academic decisions."
    return None


def build_document_course_signals(extracted_text: Optional[str], document_type: str) -> DocumentCourseSignals:
    if not extracted_text:
        return DocumentCourseSignals()

    interpreted = extract_attachment_course_signals(extracted_text, document_type, limit=30)
    matched = tuple(extract_known_course_codes(extracted_text, limit=30))

    mentioned_candidates = set(extract_all_course_codes(extracted_text, limit=60))
    unknown = tuple(sorted(code for code in mentioned_candidates if code not in matched))

    return DocumentCourseSignals(
        completed_codes=tuple(sorted(interpreted.completed_codes)),
        planned_codes=tuple(sorted(interpreted.planned_codes)),
        remaining_codes=tuple(sorted(interpreted.remaining_codes)),
        matched_course_codes=matched,
        unknown_course_codes=unknown,
    )


def extract_transcript_summary(extracted_text: Optional[str], document_type: str) -> TranscriptSummary:
    if not extracted_text or document_type not in {"transcript", "degree_audit", "pdf_document"}:
        return TranscriptSummary()

    normalized = _normalize_multiline_text(extracted_text)

    gpa_match = re.search(
        r"(?i)(?:current|cumulative|overall)?\s*gpa\s*[:=]?\s*([0-4]\.\d{1,3})"
        r"|gpa\s+([0-4]\.\d{1,3})",
        normalized,
    )
    earned_credits_match = re.search(
        r"(?i)(?:earned|completed)\s+credits?\s*[:=]?\s*(\d+(?:\.\d+)?)",
        normalized,
    )
    standing_match = re.search(
        r"(?i)(?:academic\s+standing|class\s+standing|student\s+standing)\s*[:=]?\s*([A-Za-z ]{3,40}?)(?=\s+Graduation\s+Term|\s+Advisor|\n|$)",
        normalized,
    )
    advisor_match = re.search(
        r"(?im)\b(?:primary\s+)?advisor\s*[:=]?\s+([A-Za-z][A-Za-z .,'-]{1,80})\s*$",
        normalized,
    )

    gpa = next((group for group in (gpa_match.group(1), gpa_match.group(2)) if group), None) if gpa_match else None
    earned_credits = earned_credits_match.group(1) if earned_credits_match else None
    standing = standing_match.group(1).strip(" .") if standing_match else None
    advisor = advisor_match.group(1).strip(" .") if advisor_match else None

    return TranscriptSummary(
        gpa=gpa,
        earned_credits=earned_credits,
        standing=standing,
        advisor=advisor,
    )


def validate_attachment_upload(filename: str, content_type: str, file_bytes: bytes) -> None:
    suffix = Path(filename).suffix.lower()
    allowed_mime = content_type in ALLOWED_ATTACHMENT_MIME_TYPES or content_type.startswith(ALLOWED_ATTACHMENT_MIME_PREFIXES)

    if len(file_bytes) > MAX_ATTACHMENT_BYTES:
        raise HTTPException(
            status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
            detail="Attachments must be 10 MB or smaller.",
        )

    if suffix not in ALLOWED_ATTACHMENT_SUFFIXES and not allowed_mime:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Unsupported attachment type.",
        )


def _infer_document_type(filename: str, content_type: str, extracted_text: Optional[str] = None) -> str:
    lowered_name = filename.lower()
    lowered_text = (extracted_text or "").lower()
    combined = f"{lowered_name} {lowered_text}"

    if any(token in combined for token in ["degree audit", "audit", "degreeworks", "requirement status"]):
        return "degree_audit"
    if any(token in combined for token in ["transcript", "grade report", "completed courses", "course history"]):
        return "transcript"
    if any(token in combined for token in ["schedule", "timetable", "weekly view", "calendar"]):
        return "schedule"
    if any(token in combined for token in ["registration", "advisor approval", "form"]):
        return "academic_form"
    if content_type.startswith(IMAGE_MIME_PREFIXES):
        return "image_screenshot"
    if content_type == PDF_MIME_TYPE or lowered_name.endswith(".pdf"):
        return "pdf_document"
    if content_type.startswith(TEXT_MIME_PREFIXES):
        return "text_document"
    return "generic_file"


def _extract_pdf_text(file_bytes: bytes) -> Optional[str]:
    try:
        from pypdf import PdfReader
    except ImportError:
        return None

    try:
        reader = PdfReader(BytesIO(file_bytes))
        pages = []
        for page in reader.pages[:4]:
            extracted = page.extract_text() or ""
            if extracted.strip():
                pages.append(extracted)
        return _normalize_multiline_text("\n\n".join(pages)) or None
    except Exception:
        return None


def _extract_gemini_text(
    temp_path: Optional[str],
    content_type: str,
    document_type: str,
    filename: str,
) -> Optional[str]:
    if not temp_path:
        return None
    return extract_text_from_attachment(
        attachment_path=temp_path,
        attachment_mime_type=content_type,
        attachment_document_type=document_type,
        attachment_summary=filename,
    )


def _build_analysis(
    *,
    filename: str,
    content_type: str,
    document_type: str,
    extraction_method: str,
    extracted_text: Optional[str],
    temp_path: Optional[str],
    context_text: str,
    summary: str,
) -> AttachmentContext:
    transcript_summary = extract_transcript_summary(extracted_text, document_type)
    return AttachmentContext(
        filename=filename,
        content_type=content_type,
        summary=summary,
        context_text=context_text,
        extracted_text=extracted_text,
        temp_path=temp_path,
        document_type=document_type,
        extraction_method=extraction_method,
        confidence_note=_build_confidence_note(extracted_text, extraction_method),
        signals=build_document_course_signals(extracted_text, document_type),
        transcript_summary=transcript_summary,
    )


async def extract_attachment_context(attachment: Optional[UploadFile]) -> Optional[AttachmentContext]:
    if not attachment:
        return None

    filename = attachment.filename or "uploaded-file"
    content_type = attachment.content_type or "application/octet-stream"
    file_bytes = await attachment.read()
    await attachment.close()
    validate_attachment_upload(filename, content_type, file_bytes)

    if content_type == PDF_MIME_TYPE or filename.lower().endswith(".pdf"):
        temp_path = _write_temp_attachment(filename, file_bytes)
        extracted_text = _extract_pdf_text(file_bytes)
        extraction_method = "pdf_local"
        document_type = _infer_document_type(filename, content_type, extracted_text)
        if not extracted_text:
            extracted_text = _extract_gemini_text(temp_path, content_type, document_type, filename)
            extraction_method = "pdf_gemini"
            document_type = _infer_document_type(filename, content_type, extracted_text)
        if extracted_text:
            excerpt = extracted_text[:4000]
            return _build_analysis(
                filename=filename,
                content_type=content_type,
                document_type=document_type,
                extraction_method=extraction_method,
                extracted_text=extracted_text,
                temp_path=temp_path,
                summary=f"{document_type.replace('_', ' ').title()} uploaded: {filename}",
                context_text=(
                    f"Student uploaded a {document_type.replace('_', ' ')} PDF named {filename}. "
                    f"Extracted document text excerpt: {excerpt}"
                ),
            )
        return _build_analysis(
            filename=filename,
            content_type=content_type,
            document_type=document_type,
            extraction_method=extraction_method,
            extracted_text=None,
            temp_path=temp_path,
            summary=f"{document_type.replace('_', ' ').title()} uploaded: {filename}",
            context_text=(
                f"Student uploaded a {document_type.replace('_', ' ')} PDF named {filename}. "
                "The local parser could not extract readable text from this file. "
                "Use the student's question, filename, and any available advising context carefully."
            ),
        )

    if content_type.startswith(TEXT_MIME_PREFIXES) or content_type in TEXT_MIME_TYPES:
        decoded_text = file_bytes.decode("utf-8", errors="ignore")
        excerpt = _normalize_text(decoded_text)[:4000]
        document_type = _infer_document_type(filename, content_type, decoded_text)
        return _build_analysis(
            filename=filename,
            content_type=content_type,
            document_type=document_type,
            extraction_method="text_local",
            extracted_text=decoded_text,
            temp_path=None,
            summary=f"{document_type.replace('_', ' ').title()} uploaded: {filename}",
            context_text=(
                f"Student uploaded a {document_type.replace('_', ' ')} text document named {filename}. "
                f"Extracted content excerpt: {excerpt or 'No readable text found.'}"
            ),
        )

    if content_type.startswith(IMAGE_MIME_PREFIXES):
        temp_path = _write_temp_attachment(filename, file_bytes)
        initial_document_type = _infer_document_type(filename, content_type)
        extracted_text = _extract_gemini_text(temp_path, content_type, initial_document_type, filename)
        document_type = _infer_document_type(filename, content_type, extracted_text)
        excerpt_text = (
            f" Extracted visible text excerpt: {_normalize_text(extracted_text)[:4000]}"
            if extracted_text else
            ""
        )
        return _build_analysis(
            filename=filename,
            content_type=content_type,
            document_type=document_type,
            extraction_method="image_gemini",
            extracted_text=extracted_text,
            temp_path=temp_path,
            summary=f"{document_type.replace('_', ' ').title()} uploaded: {filename}",
            context_text=(
                f"Student uploaded a {document_type.replace('_', ' ')} image named {filename} with content type {content_type}. "
                "Use the image itself along with the advising context to answer questions about schedules, screenshots, forms, transcripts, or planning materials."
                f"{excerpt_text}"
            ),
        )

    document_type = _infer_document_type(filename, content_type)
    return _build_analysis(
        filename=filename,
        content_type=content_type,
        document_type=document_type,
        extraction_method="none",
        extracted_text=None,
        temp_path=None,
        summary=f"{document_type.replace('_', ' ').title()} uploaded: {filename}",
        context_text=(
            f"Student uploaded a file named {filename} with content type {content_type}. "
            "Treat it as supporting context, but note that no specialized parser exists yet for this file type."
        ),
    )
