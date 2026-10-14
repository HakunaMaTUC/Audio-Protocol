"""Datentypen für nachvollziehbare Transkriptionsergebnisse."""

from dataclasses import dataclass, field
from typing import Any


@dataclass(frozen=True)
class TranscriptSegment:
    """Ein zeitlich abgegrenztes Segment des Transkripts."""

    start: float
    end: float
    text: str

    def to_dict(self) -> dict[str, Any]:
        return {
            "start_seconds": self.start,
            "end_seconds": self.end,
            "text": self.text,
        }


@dataclass
class Transcript:
    """Transkript mit den tatsächlich verfügbaren Metadaten."""

    source_file: str
    model: str
    language: str | None = None
    language_probability: float | None = None
    duration_seconds: float | None = None
    segments: list[TranscriptSegment] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        result: dict[str, Any] = {
            "source_file": self.source_file,
            "model": self.model,
            "segments": [segment.to_dict() for segment in self.segments],
        }
        optional_values = {
            "language": self.language,
            "language_probability": self.language_probability,
            "duration_seconds": self.duration_seconds,
        }
        result.update(
            {
                key: value
                for key, value in optional_values.items()
                if value is not None
            }
        )
        return result
