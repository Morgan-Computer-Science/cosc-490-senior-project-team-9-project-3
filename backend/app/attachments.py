from dataclasses import dataclass
from io import BytesIO
from pathlib import Path
import re
import tempfile
from typing import Optional

from fastapi import HTTPException, UploadFile, status


MAX_ATTACHMENT_BYTES = 10 * 1024 * 1024
TEXT_MIME_PREFIXES = ("text/",)
TEXT_MIME_TYPES = {
    "application/json",
    "application/xml",
    "application/javascript",
}
IMAGE_MIME_PREFIXES = ("image/",)
PDF_MIME_TYPE = "application/pdf"


@dataclass(frozen=True)
class AttachmentContext:
    filename: str
    content_type: str
    context_text: str
    summary: str
    extracted_text: Optional[str] = None
    temp_path: Optional[str] = None
    document_type: str = "generic_file"


def _write_temp_attachment(filename: str, file_bytes: bytes) -> str:
    suffix = Path(filename).suffix or ".bin"
    with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as temp_file:
        temp_file.write(file_bytes)
        return temp_file.name


def _normalize_text(text: str) -> str:
    return re.sub(r"\s+", " ", text).strip()


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
        return _normalize_text(" ".join(pages)) or None
    except Exception:
        return None


async def extract_attachment_context(attachment: Optional[UploadFile]) -> Optional[AttachmentContext]:
    if not attachment:
        return None

    filename = attachment.filename or "uploaded-file"
    content_type = attachment.content_type or "application/octet-stream"
    file_bytes = await attachment.read()
    await attachment.close()

    if len(file_bytes) > MAX_ATTACHMENT_BYTES:
        raise HTTPException(
            status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
            detail="Attachments must be 10 MB or smaller.",
        )

    if content_type == PDF_MIME_TYPE or filename.lower().endswith(".pdf"):
        temp_path = _write_temp_attachment(filename, file_bytes)
        extracted_text = _extract_pdf_text(file_bytes)
        document_type = _infer_document_type(filename, content_type, extracted_text)
        if extracted_text:
            excerpt = extracted_text[:4000]
            return AttachmentContext(
                filename=filename,
                content_type=content_type,
                summary=f"{document_type.replace('_', ' ').title()} uploaded: {filename}",
                context_text=(
                    f"Student uploaded a {document_type.replace('_', ' ')} PDF named {filename}. "
                    f"Extracted document text excerpt: {excerpt}"
                ),
                extracted_text=extracted_text,
                temp_path=temp_path,
                document_type=document_type,
            )
        return AttachmentContext(
            filename=filename,
            content_type=content_type,
            summary=f"{document_type.replace('_', ' ').title()} uploaded: {filename}",
            context_text=(
                f"Student uploaded a {document_type.replace('_', ' ')} PDF named {filename}. "
                "The local parser could not extract readable text from this file. "
                "Use the student's question, filename, and any available advising context carefully."
            ),
            temp_path=temp_path,
            document_type=document_type,
        )

    if content_type.startswith(TEXT_MIME_PREFIXES) or content_type in TEXT_MIME_TYPES:
        decoded_text = file_bytes.decode("utf-8", errors="ignore")
        excerpt = _normalize_text(decoded_text)[:4000]
        document_type = _infer_document_type(filename, content_type, decoded_text)
        return AttachmentContext(
            filename=filename,
            content_type=content_type,
            summary=f"{document_type.replace('_', ' ').title()} uploaded: {filename}",
            context_text=(
                f"Student uploaded a {document_type.replace('_', ' ')} text document named {filename}. "
                f"Extracted content excerpt: {excerpt or 'No readable text found.'}"
            ),
            extracted_text=decoded_text,
            document_type=document_type,
        )

    if content_type.startswith(IMAGE_MIME_PREFIXES):
        temp_path = _write_temp_attachment(filename, file_bytes)
        document_type = _infer_document_type(filename, content_type)
        return AttachmentContext(
            filename=filename,
            content_type=content_type,
            summary=f"{document_type.replace('_', ' ').title()} uploaded: {filename}",
            context_text=(
                f"Student uploaded a {document_type.replace('_', ' ')} image named {filename} with content type {content_type}. "
                "Use the image itself along with the advising context to answer questions about schedules, screenshots, forms, transcripts, or planning materials."
            ),
            temp_path=temp_path,
            document_type=document_type,
        )

    document_type = _infer_document_type(filename, content_type)
    return AttachmentContext(
        filename=filename,
        content_type=content_type,
        summary=f"{document_type.replace('_', ' ').title()} uploaded: {filename}",
        context_text=(
            f"Student uploaded a file named {filename} with content type {content_type}. "
            "Treat it as supporting context, but note that no specialized parser exists yet for this file type."
        ),
        document_type=document_type,
    )
