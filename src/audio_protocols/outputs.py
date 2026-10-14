"""JSON- und Markdown-Ausgaben für Transkripte."""

import json
from pathlib import Path

from .models import Transcript
from .validation import ensure_output_paths_available, output_paths


def format_timestamp(seconds: float) -> str:
    """Formatiert Sekunden als HH:MM:SS.mmm."""

    milliseconds = max(0, round(float(seconds) * 1000))
    hours, remainder = divmod(milliseconds, 3_600_000)
    minutes, remainder = divmod(remainder, 60_000)
    whole_seconds, millis = divmod(remainder, 1_000)
    return f"{hours:02d}:{minutes:02d}:{whole_seconds:02d}.{millis:03d}"


def _display_optional(value: object | None) -> str:
    return "nicht verfügbar" if value is None else str(value)


def render_markdown(transcript: Transcript) -> str:
    """Erzeugt eine lesbare Markdown-Fassung ohne zusätzliche Annahmen."""

    lines = [
        f"# Transkript: {transcript.source_file}",
        "",
        "## Metadaten",
        "",
        f"- Modell: `{transcript.model}`",
        f"- Erkannte Sprache: `{_display_optional(transcript.language)}`",
        "- Spracherkennungs-Konfidenz: "
        f"`{_display_optional(transcript.language_probability)}`",
        "- Dauer in Sekunden: "
        f"`{_display_optional(transcript.duration_seconds)}`",
        "",
        "## Segmente",
        "",
    ]

    if not transcript.segments:
        lines.append("_Keine Transkriptsegmente vorhanden._")
    else:
        for segment in transcript.segments:
            start = format_timestamp(segment.start)
            end = format_timestamp(segment.end)
            lines.append(f"`[{start} – {end}]` {segment.text}")

    return "\n".join(lines) + "\n"


def write_outputs(
    transcript: Transcript,
    audio_path: Path,
    output_dir: str | Path,
    *,
    overwrite: bool = False,
) -> tuple[Path, Path]:
    """Schreibt JSON und Markdown und gibt beide Pfade zurück."""

    paths = output_paths(audio_path, output_dir)
    ensure_output_paths_available(paths, overwrite=overwrite)
    paths[0].parent.mkdir(parents=True, exist_ok=True)
    paths[0].write_text(
        json.dumps(transcript.to_dict(), ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    paths[1].write_text(render_markdown(transcript), encoding="utf-8")
    return paths
