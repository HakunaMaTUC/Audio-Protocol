"""Adapter für faster-whisper mit automatischer Spracherkennung."""

from collections.abc import Callable
from pathlib import Path

from .models import Transcript, TranscriptSegment


class TranscriptionError(RuntimeError):
    """Verständlicher Fehler beim Laden oder Ausführen der Transkription."""


def transcribe_audio(
    audio_path: Path,
    *,
    model_name: str = "small",
    device: str = "cpu",
    compute_type: str = "int8",
    model_cache_dir: Path | None = None,
    progress_callback: Callable[[int, float], None] | None = None,
) -> Transcript:
    """Transkribiert eine Datei lokal und übernimmt die Bibliotheksmetadaten.

    `language=None` aktiviert die automatische Spracherkennung. `task="transcribe"`
    verhindert eine Übersetzung in eine andere Sprache.
    """

    try:
        from faster_whisper import WhisperModel
    except ImportError as exc:
        raise TranscriptionError(
            "faster-whisper ist nicht installiert. "
            "Installiere die Projektabhängigkeiten mit "
            "'python -m pip install -e \".[test]\"'."
        ) from exc

    model_kwargs: dict[str, object] = {
        "device": device,
        "compute_type": compute_type,
    }
    if model_cache_dir is not None:
        model_kwargs["download_root"] = str(model_cache_dir)

    try:
        model = WhisperModel(model_name, **model_kwargs)
        segment_iterator, info = model.transcribe(
            str(audio_path),
            language=None,
            task="transcribe",
            vad_filter=True,
        )
        segments: list[TranscriptSegment] = []
        last_reported_count = 0
        for index, segment in enumerate(segment_iterator, start=1):
            parsed_segment = TranscriptSegment(
                start=float(segment.start),
                end=float(segment.end),
                text=str(segment.text).strip(),
            )
            segments.append(parsed_segment)

            # A callback keeps the CLI responsive without adding a progress
            # bar dependency. Report periodically and once for the final
            # segment when the total is not a multiple of ten.
            if progress_callback is not None and index % 10 == 0:
                progress_callback(index, parsed_segment.end)
                last_reported_count = index

        if progress_callback is not None and segments:
            if last_reported_count != len(segments):
                progress_callback(len(segments), segments[-1].end)
    except Exception as exc:
        raise TranscriptionError(f"Transkription fehlgeschlagen: {exc}") from exc

    language = getattr(info, "language", None)
    language_probability = getattr(info, "language_probability", None)
    duration = getattr(info, "duration", None)

    return Transcript(
        source_file=audio_path.name,
        model=model_name,
        language=str(language) if language is not None else None,
        language_probability=(
            float(language_probability)
            if language_probability is not None
            else None
        ),
        duration_seconds=float(duration) if duration is not None else None,
        segments=segments,
    )
