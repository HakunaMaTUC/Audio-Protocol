import sys
from pathlib import Path
from types import SimpleNamespace

from audio_protocols.transcriber import transcribe_audio


def test_transcriber_uses_auto_language_and_no_translation(
    monkeypatch, tmp_path: Path
) -> None:
    calls = {}

    class FakeModel:
        def __init__(self, name, **kwargs):
            calls["model_name"] = name
            calls["model_kwargs"] = kwargs

        def transcribe(self, path, **kwargs):
            calls["path"] = path
            calls["transcribe_kwargs"] = kwargs
            segments = [SimpleNamespace(start=1, end=2, text=" Hallo ")]
            info = SimpleNamespace(
                language="de",
                language_probability=0.88,
                duration=4.5,
            )
            return iter(segments), info

    monkeypatch.setitem(
        sys.modules,
        "faster_whisper",
        SimpleNamespace(WhisperModel=FakeModel),
    )
    audio_path = tmp_path / "sample.wav"
    audio_path.write_bytes(b"test")

    result = transcribe_audio(audio_path, model_name="small")

    assert calls["model_name"] == "small"
    assert calls["model_kwargs"] == {"device": "cpu", "compute_type": "int8"}
    assert calls["transcribe_kwargs"]["language"] is None
    assert calls["transcribe_kwargs"]["task"] == "transcribe"
    assert result.language == "de"
    assert result.segments[0].text == "Hallo"


def test_transcriber_reports_progress_without_downloading_a_model(
    monkeypatch, tmp_path: Path
) -> None:
    class FakeModel:
        def __init__(self, name, **kwargs):
            pass

        def transcribe(self, path, **kwargs):
            segments = [SimpleNamespace(start=2, end=3, text=" Test ")]
            info = SimpleNamespace(language=None, duration=4.0)
            return iter(segments), info

    monkeypatch.setitem(
        sys.modules,
        "faster_whisper",
        SimpleNamespace(WhisperModel=FakeModel),
    )
    audio_path = tmp_path / "sample.wav"
    audio_path.write_bytes(b"test")
    progress: list[tuple[int, float]] = []

    transcribe_audio(
        audio_path,
        progress_callback=lambda count, seconds: progress.append((count, seconds)),
    )

    assert progress == [(1, 3.0)]
