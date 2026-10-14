"""Datenmodell und Strukturprüfung für Ergebnisprotokolle.

Dieses Modul enthält bewusst keine automatische inhaltliche Extraktion. Es
definiert nur die fachliche Zielstruktur für spätere Generatoren.
"""

from collections.abc import Mapping
from dataclasses import dataclass, field
from math import isfinite
from typing import Any, TypeAlias

SCHEMA_VERSION = "0.1"
PROTOCOL_TYPE = "ergebnisprotokoll"
# `confirmed` means that the source transcript explicitly confirms the item;
# it must not merely describe generator confidence.
DECISION_STATUSES = {"confirmed", "uncertain"}
ACTION_STATUSES = {"confirmed", "uncertain"}
DEADLINE_STATUSES = {"stated", "not_mentioned", "uncertain"}


class ProtocolValidationError(ValueError):
    """Fehler in der strukturellen Form eines Ergebnisprotokolls."""


@dataclass(frozen=True)
class EvidenceRange:
    """Zeitbereich einer belegenden Transkriptpassage.

    MVP 1 provides no stable segment IDs. Time ranges are therefore the
    smallest backwards-compatible evidence reference for now.
    """

    start_seconds: float
    end_seconds: float

    def __post_init__(self) -> None:
        start = float(self.start_seconds)
        end = float(self.end_seconds)
        if not isfinite(start) or not isfinite(end) or start < 0 or end < start:
            raise ProtocolValidationError(
                "Ein Evidenzbereich muss endliche Zeiten mit 0 <= Start <= Ende enthalten."
            )

    def to_dict(self) -> dict[str, float]:
        return {
            "start_seconds": float(self.start_seconds),
            "end_seconds": float(self.end_seconds),
        }


@dataclass(frozen=True)
class DecisionItem:
    """Eine bestätigte oder ausdrücklich unsichere Entscheidung.

    `confirmed` darf nur verwendet werden, wenn die Quelle die Entscheidung
    ausdrücklich bestätigt. Der Strukturvalidator kann diese Bedeutung nicht
    aus dem Text ableiten; das ist eine Verantwortung des Generators.
    """

    text: str
    status: str
    evidence: list[EvidenceRange]

    def to_dict(self) -> dict[str, Any]:
        return {
            "text": self.text,
            "status": self.status,
            "evidence": [item.to_dict() for item in self.evidence],
        }


@dataclass(frozen=True)
class ActionItem:
    """Eine Maßnahme mit bewusst expliziten unbekannten Angaben.

    Auch hier beschreibt `confirmed` eine belegte Aussage der Quelle und nicht
    bloß das Vertrauen des Generators in seine eigene Interpretation.
    """

    task: str
    responsible: str | None
    deadline: str | None
    deadline_status: str
    status: str
    evidence: list[EvidenceRange]

    def to_dict(self) -> dict[str, Any]:
        return {
            "task": self.task,
            "responsible": self.responsible,
            "deadline": self.deadline,
            "deadline_status": self.deadline_status,
            "status": self.status,
            "evidence": [item.to_dict() for item in self.evidence],
        }


@dataclass(frozen=True)
class OpenPointItem:
    """Ein noch nicht geklärter Punkt."""

    text: str
    status: str
    evidence: list[EvidenceRange]

    def to_dict(self) -> dict[str, Any]:
        return {
            "text": self.text,
            "status": self.status,
            "evidence": [item.to_dict() for item in self.evidence],
        }


@dataclass(frozen=True)
class QualityNote:
    """Qualitätsmeldung, optional mit zugehörigen Evidenzbereichen."""

    message: str
    evidence: list[EvidenceRange] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        result: dict[str, Any] = {"message": self.message}
        if self.evidence:
            result["evidence"] = [item.to_dict() for item in self.evidence]
        return result


QualityEntry: TypeAlias = str | QualityNote


@dataclass(frozen=True)
class ProtocolQuality:
    """Transparenzfelder für Unsicherheiten und nicht zuordenbare Angaben."""

    uncertainties: list[QualityEntry] = field(default_factory=list)
    unresolved_conflicts: list[QualityEntry] = field(default_factory=list)
    items_without_clear_owner: list[QualityEntry] = field(default_factory=list)

    def to_dict(self) -> dict[str, list[Any]]:
        return {
            "uncertainties": [self._entry_to_dict(item) for item in self.uncertainties],
            "unresolved_conflicts": [
                self._entry_to_dict(item) for item in self.unresolved_conflicts
            ],
            "items_without_clear_owner": [
                self._entry_to_dict(item) for item in self.items_without_clear_owner
            ],
        }

    @staticmethod
    def _entry_to_dict(entry: QualityEntry) -> Any:
        return entry if isinstance(entry, str) else entry.to_dict()


@dataclass(frozen=True)
class ResultProtocol:
    """Strukturierte Ergebnisprotokoll-Ausgabe ohne Generatorlogik."""

    source_file: str
    title: str | None
    decisions: list[DecisionItem] = field(default_factory=list)
    actions: list[ActionItem] = field(default_factory=list)
    open_points: list[OpenPointItem] = field(default_factory=list)
    quality: ProtocolQuality = field(default_factory=ProtocolQuality)
    schema_version: str = SCHEMA_VERSION
    protocol_type: str = PROTOCOL_TYPE

    def to_dict(self) -> dict[str, Any]:
        return {
            "schema_version": self.schema_version,
            "protocol_type": self.protocol_type,
            "source_file": self.source_file,
            "title": self.title,
            "decisions": [item.to_dict() for item in self.decisions],
            "actions": [item.to_dict() for item in self.actions],
            "open_points": [item.to_dict() for item in self.open_points],
            "quality": self.quality.to_dict(),
        }

    def validate(self) -> None:
        """Prüft die serialisierte Struktur gegen die MVP-2-Regeln."""

        validate_result_protocol(self.to_dict())


def _require_nonempty_text(value: object, field_name: str) -> None:
    if not isinstance(value, str) or not value.strip():
        raise ProtocolValidationError(f"{field_name} muss ein nichtleerer Text sein.")


def _validate_evidence(value: object, field_name: str) -> None:
    if not isinstance(value, list) or not value:
        raise ProtocolValidationError(
            f"{field_name} muss mindestens einen Evidenzbereich enthalten."
        )
    for index, evidence in enumerate(value):
        if not isinstance(evidence, Mapping):
            raise ProtocolValidationError(f"{field_name}[{index}] ist kein Objekt.")
        start = evidence.get("start_seconds")
        end = evidence.get("end_seconds")
        if not isinstance(start, (int, float)) or isinstance(start, bool):
            raise ProtocolValidationError(
                f"{field_name}[{index}].start_seconds ist ungültig."
            )
        if not isinstance(end, (int, float)) or isinstance(end, bool):
            raise ProtocolValidationError(
                f"{field_name}[{index}].end_seconds ist ungültig."
            )
        try:
            valid_range = EvidenceRange(float(start), float(end))
        except (TypeError, ValueError, ProtocolValidationError) as exc:
            raise ProtocolValidationError(
                f"{field_name}[{index}] enthält einen ungültigen Zeitbereich."
            ) from exc
        if valid_range.end_seconds < valid_range.start_seconds:
            raise ProtocolValidationError(
                f"{field_name}[{index}] endet vor seinem Beginn."
            )


def _validate_quality(value: object) -> None:
    if not isinstance(value, Mapping):
        raise ProtocolValidationError("quality muss ein Objekt sein.")
    for field_name in (
        "uncertainties",
        "unresolved_conflicts",
        "items_without_clear_owner",
    ):
        entries = value.get(field_name)
        if not isinstance(entries, list):
            raise ProtocolValidationError(f"quality.{field_name} muss eine Liste sein.")
        for index, entry in enumerate(entries):
            if isinstance(entry, str):
                _require_nonempty_text(entry, f"quality.{field_name}[{index}]")
                continue
            if not isinstance(entry, Mapping):
                raise ProtocolValidationError(
                    f"quality.{field_name}[{index}] muss Text oder ein Objekt sein."
                )
            _require_nonempty_text(
                entry.get("message"), f"quality.{field_name}[{index}].message"
            )
            if "evidence" in entry:
                _validate_evidence(
                    entry["evidence"], f"quality.{field_name}[{index}].evidence"
                )


def validate_result_protocol(payload: Mapping[str, Any]) -> None:
    """Validiert ein Ergebnisprotokoll nach der JSON-Serialisierung."""

    required = {
        "schema_version",
        "protocol_type",
        "source_file",
        "title",
        "decisions",
        "actions",
        "open_points",
        "quality",
    }
    missing = required.difference(payload)
    if missing:
        raise ProtocolValidationError(f"Fehlende Felder: {', '.join(sorted(missing))}.")
    if payload["schema_version"] != SCHEMA_VERSION:
        raise ProtocolValidationError("Nicht unterstützte schema_version.")
    if payload["protocol_type"] != PROTOCOL_TYPE:
        raise ProtocolValidationError("Nicht unterstützter protocol_type.")
    _require_nonempty_text(payload["source_file"], "source_file")
    if payload["title"] is not None and not isinstance(payload["title"], str):
        raise ProtocolValidationError("title muss Text oder null sein.")

    decisions = payload["decisions"]
    if not isinstance(decisions, list):
        raise ProtocolValidationError("decisions muss eine Liste sein.")
    for index, item in enumerate(decisions):
        if not isinstance(item, Mapping):
            raise ProtocolValidationError(f"decisions[{index}] ist kein Objekt.")
        _require_nonempty_text(item.get("text"), f"decisions[{index}].text")
        if item.get("status") not in DECISION_STATUSES:
            raise ProtocolValidationError(f"decisions[{index}].status ist ungültig.")
        _validate_evidence(item.get("evidence"), f"decisions[{index}].evidence")

    actions = payload["actions"]
    if not isinstance(actions, list):
        raise ProtocolValidationError("actions muss eine Liste sein.")
    for index, item in enumerate(actions):
        if not isinstance(item, Mapping):
            raise ProtocolValidationError(f"actions[{index}] ist kein Objekt.")
        _require_nonempty_text(item.get("task"), f"actions[{index}].task")
        for field_name in ("responsible", "deadline"):
            value = item.get(field_name)
            if value is not None and not isinstance(value, str):
                raise ProtocolValidationError(
                    f"actions[{index}].{field_name} muss Text oder null sein."
                )
        if item.get("deadline_status") not in DEADLINE_STATUSES:
            raise ProtocolValidationError(
                f"actions[{index}].deadline_status ist ungültig."
            )
        if item.get("status") not in ACTION_STATUSES:
            raise ProtocolValidationError(f"actions[{index}].status ist ungültig.")
        _validate_evidence(item.get("evidence"), f"actions[{index}].evidence")

    open_points = payload["open_points"]
    if not isinstance(open_points, list):
        raise ProtocolValidationError("open_points muss eine Liste sein.")
    for index, item in enumerate(open_points):
        if not isinstance(item, Mapping):
            raise ProtocolValidationError(f"open_points[{index}] ist kein Objekt.")
        _require_nonempty_text(item.get("text"), f"open_points[{index}].text")
        if item.get("status") != "open":
            raise ProtocolValidationError(
                f"open_points[{index}].status muss open sein."
            )
        _validate_evidence(item.get("evidence"), f"open_points[{index}].evidence")

    _validate_quality(payload["quality"])
