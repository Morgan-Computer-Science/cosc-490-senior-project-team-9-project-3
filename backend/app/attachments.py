from dataclasses import dataclass
from io import BytesIO
import re
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


def _normalize_text(text: str) -> str:
    return re.sub(r"\s+", " ", text).strip()


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
        extracted_text = _extract_pdf_text(file_bytes)
        if extracted_text:
            excerpt = extracted_text[:4000]
            return AttachmentContext(
                filename=filename,
                content_type=content_type,
                summary=f"PDF uploaded: {filename}",
                context_text=(
                    f"Student uploaded a PDF named {filename}. "
                    f"Extracted document text excerpt: {excerpt}"
                ),
            )
        return AttachmentContext(
            filename=filename,
            content_type=content_type,
            summary=f"PDF uploaded: {filename}",
            context_text=(
                f"Student uploaded a PDF named {filename}. "
                "The local parser could not extract readable text from this file. "
                "Use the student's question, filename, and any available advising context carefully."
            ),
        )

    if content_type.startswith(TEXT_MIME_PREFIXES) or content_type in TEXT_MIME_TYPES:
        decoded_text = file_bytes.decode("utf-8", errors="ignore")
        excerpt = _normalize_text(decoded_text)[:4000]
        return AttachmentContext(
            filename=filename,
            content_type=content_type,
            summary=f"Document uploaded: {filename}",
            context_text=(
                f"Student uploaded a text-based document named {filename}. "
                f"Extracted content excerpt: {excerpt or 'No readable text found.'}"
            ),
        )

    if content_type.startswith(IMAGE_MIME_PREFIXES):
        return AttachmentContext(
            filename=filename,
            content_type=content_type,
            summary=f"Image uploaded: {filename}",
            context_text=(
                f"Student uploaded an image named {filename} with content type {content_type}. "
                "This first version stores the image metadata and file context, but it does not yet perform full visual OCR or screenshot understanding."
            ),
        )

    return AttachmentContext(
        filename=filename,
        content_type=content_type,
        summary=f"File uploaded: {filename}",
        context_text=(
            f"Student uploaded a file named {filename} with content type {content_type}. "
            "Treat it as supporting context, but note that no specialized parser exists yet for this file type."
        ),
    )
