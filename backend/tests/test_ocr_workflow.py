import asyncio

import pytest

from app.attachments import extract_attachment_context


class DummyUpload:
    def __init__(self, filename, content_type, payload):
        self.filename = filename
        self.content_type = content_type
        self._payload = payload

    async def read(self):
        return self._payload

    async def close(self):
        return None


def test_text_attachment_returns_structured_analysis():
    upload = DummyUpload("transcript.txt", "text/plain", b"Completed: COSC 111. Planned: MATH 141")
    analysis = asyncio.run(extract_attachment_context(upload))
    assert analysis.detected_document_type in {"transcript", "text_document"}
    assert analysis.extraction_method == "text_local"
    assert "COSC111" in analysis.signals.matched_course_codes


def test_unsupported_attachment_is_rejected():
    upload = DummyUpload("bad.exe", "application/octet-stream", b"fake")
    with pytest.raises(Exception):
        asyncio.run(extract_attachment_context(upload))
