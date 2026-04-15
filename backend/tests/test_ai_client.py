import importlib
from types import SimpleNamespace


def test_generate_ai_reply_uses_runtime_api_key(monkeypatch):
    monkeypatch.delenv("GEMINI_API_KEY", raising=False)
    monkeypatch.delenv("GOOGLE_API_KEY", raising=False)

    from app import ai_client

    ai_client = importlib.reload(ai_client)

    configure_calls: list[str | None] = []

    class FakeModel:
        def __init__(self, name):
            self.name = name

        def generate_content(self, contents):
            return SimpleNamespace(text="live reply")

    fake_genai = SimpleNamespace(
        configure=lambda api_key=None: configure_calls.append(api_key),
        GenerativeModel=FakeModel,
        upload_file=lambda *args, **kwargs: None,
        delete_file=lambda *args, **kwargs: None,
    )

    monkeypatch.setattr(ai_client, "genai", fake_genai)
    monkeypatch.setenv("GEMINI_API_KEY", "runtime-key")

    reply = ai_client.generate_ai_reply(
        [{"role": "user", "content": "Say hello in one sentence."}],
        extra_context="Morgan State advising context test",
    )

    assert reply == "live reply"
    assert configure_calls[-1] == "runtime-key"
