import asyncio
import sys
from types import SimpleNamespace

import pytest

from app.attachments import _extract_pdf_text, extract_attachment_context


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


def test_pdf_extraction_preserves_line_boundaries(monkeypatch):
    class DummyPage:
        def extract_text(self):
            return "COMPLETE\nCOSC 241 A\nIN-PROGRESS\nCOSC 459 IP (3)\n"

    class DummyReader:
        def __init__(self, _):
            self.pages = [DummyPage()]

    monkeypatch.setitem(sys.modules, "pypdf", SimpleNamespace(PdfReader=DummyReader))

    extracted = _extract_pdf_text(b"%PDF-fake")

    assert extracted is not None
    assert "\n" in extracted
    assert "COSC 241 A" in extracted
    assert "COSC 459 IP (3)" in extracted
