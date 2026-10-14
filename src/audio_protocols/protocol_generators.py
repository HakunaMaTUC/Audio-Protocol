"""Austauschbare Schnittstelle für spätere Protokollgeneratoren."""

from dataclasses import dataclass
from typing import Protocol

from .models import Transcript
from .protocols import ProtocolValidationError, ResultProtocol


class ResultProtocolGenerator(Protocol):
    """Vertrag für regelbasierte oder sprachmodellgestützte Generatoren."""

    def generate(
        self,
        transcript: Transcript,
        *,
        title: str | None = None,
        context: str | None = None,
    ) -> ResultProtocol:
        """Erzeugt ein Ergebnisprotokoll aus einem bestehenden Transkript."""


class ProtocolGenerationError(RuntimeError):
    """Fehler an der Grenze zwischen Transkript und Protokollgenerator."""


@dataclass(frozen=True)
class MockResultProtocolGenerator:
    """Deterministischer Mock ohne Modell- oder Regelverarbeitung.

    Der Mock gibt eine vorgegebene, strukturgeprüfte Antwort zurück. Damit
    können Schnittstelle und Ausgabeform getestet werden, ohne ein Modell zu
    installieren oder Inhalte automatisch interpretieren zu lassen.
    """

    response: ResultProtocol

    def generate(
        self,
        transcript: Transcript,
        *,
        title: str | None = None,
        context: str | None = None,
    ) -> ResultProtocol:
        del title, context
        if not isinstance(transcript, Transcript):
            raise ProtocolGenerationError(
                "Der Generator erwartet ein validiertes Transcript-Objekt."
            )
        if self.response.source_file != transcript.source_file:
            raise ProtocolGenerationError(
                "Die Mock-Antwort gehört nicht zur übergebenen Transkriptquelle."
            )
        try:
            self.response.validate()
        except ProtocolValidationError as exc:
            raise ProtocolGenerationError(
                f"Die Mock-Antwort ist strukturell ungültig: {exc}"
            ) from exc
        return self.response
