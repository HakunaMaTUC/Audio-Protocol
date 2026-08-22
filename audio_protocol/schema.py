from __future__ import annotations

from dataclasses import asdict, dataclass, field
from datetime import datetime
from typing import Any


@dataclass
class MeetingMetadata:
    date: str
    project: str
    participants: list[str] = field(default_factory=list)
    source_file: str = ""


@dataclass
class CriticalNumber:
    value: float
    unit: str
    context: str
    speaker: str
    timestamp: str
    source_quote: str
    confidence: float


@dataclass
class ActionItem:
    owner: str
    task: str
    deadline: str
    source_quote: str


@dataclass
class VerificationReport:
    missing_fields: list[str] = field(default_factory=list)
    conflicts: list[str] = field(default_factory=list)
    low_confidence_items: list[str] = field(default_factory=list)
    reviewed_by_human: bool = False


@dataclass
class MeetingProtocol:
    metadata: MeetingMetadata
    key_decisions: list[str] = field(default_factory=list)
    action_items: list[ActionItem] = field(default_factory=list)
    critical_numbers: list[CriticalNumber] = field(default_factory=list)
    open_questions: list[str] = field(default_factory=list)
    risks: list[str] = field(default_factory=list)
    verification: VerificationReport = field(default_factory=VerificationReport)

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)

    def validate(self) -> None:
        if not self.metadata.date:
            raise ValueError("metadata.date is required")
        datetime.strptime(self.metadata.date, "%Y-%m-%d")
        if not self.metadata.project:
            raise ValueError("metadata.project is required")
        for cn in self.critical_numbers:
            if not cn.unit:
                raise ValueError("critical number unit is required")
            if not cn.speaker or not cn.timestamp or not cn.source_quote:
                raise ValueError("critical number traceability fields are required")
            if not (0.0 <= cn.confidence <= 1.0):
                raise ValueError("confidence must be in [0.0, 1.0]")

