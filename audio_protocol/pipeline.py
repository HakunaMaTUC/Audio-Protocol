from __future__ import annotations

import re
from dataclasses import dataclass
from datetime import date

from .memory import DomainMemory
from .schema import (
    ActionItem,
    CriticalNumber,
    MeetingMetadata,
    MeetingProtocol,
    VerificationReport,
)

LINE_PATTERN = re.compile(
    r"^\s*(?:\[(?P<ts>\d{2}:\d{2}:\d{2})\]\s*)?(?P<speaker>[A-Za-z][\w\- ]{0,30}):\s*(?P<text>.+)$"
)
NUMBER_PATTERN = re.compile(r"(?P<value>\d+(?:\.\d+)?)\s*(?P<unit>[A-Za-z%µμ/]+)")
DATE_PATTERN = re.compile(r"\b(20\d{2}-\d{2}-\d{2})\b")


@dataclass
class TranscriptLine:
    timestamp: str
    speaker: str
    text: str


class TranscriptionCleanupAgent:
    def run(self, transcript: str) -> list[TranscriptLine]:
        cleaned: list[TranscriptLine] = []
        synthetic_second = 0
        for raw in transcript.splitlines():
            line = raw.strip()
            if not line:
                continue
            match = LINE_PATTERN.match(line)
            if not match:
                continue
            ts = match.group("ts") or f"00:00:{synthetic_second:02d}"
            cleaned.append(
                TranscriptLine(
                    timestamp=ts,
                    speaker=match.group("speaker").strip(),
                    text=match.group("text").strip(),
                )
            )
            synthetic_second = min(synthetic_second + 1, 59)
        return cleaned


class InformationExtractionAgent:
    def run(self, lines: list[TranscriptLine], memory: DomainMemory) -> dict:
        decisions: list[str] = []
        action_items: list[ActionItem] = []
        critical_numbers: list[CriticalNumber] = []
        open_questions: list[str] = []
        risks: list[str] = []

        for line in lines:
            lower = line.text.lower()
            if any(k in lower for k in ("agreed", "decided", "decision")):
                decisions.append(f"{line.speaker}: {line.text}")
            if "?" in line.text:
                open_questions.append(f"{line.speaker}: {line.text}")
            if any(k in lower for k in ("risk", "concern", "blocker", "issue")):
                risks.append(f"{line.speaker}: {line.text}")
            if any(k in lower for k in ("action", "todo", "follow up", "follow-up")):
                deadline = DATE_PATTERN.search(line.text)
                action_items.append(
                    ActionItem(
                        owner=line.speaker,
                        task=line.text,
                        deadline=deadline.group(1) if deadline else "",
                        source_quote=line.text,
                    )
                )

            for num_match in NUMBER_PATTERN.finditer(line.text):
                unit = num_match.group("unit")
                value = float(num_match.group("value"))
                confidence = 0.9 if unit in memory.glossary.values() else 0.75
                critical_numbers.append(
                    CriticalNumber(
                        value=value,
                        unit=unit,
                        context=line.text,
                        speaker=line.speaker,
                        timestamp=line.timestamp,
                        source_quote=line.text,
                        confidence=confidence,
                    )
                )

        participants = sorted(set(l.speaker for l in lines))
        return {
            "participants": participants,
            "decisions": decisions,
            "action_items": action_items,
            "critical_numbers": critical_numbers,
            "open_questions": open_questions,
            "risks": risks,
        }


class ProtocolWriterAgent:
    def run(self, extracted: dict, project: str, source_file: str) -> MeetingProtocol:
        metadata = MeetingMetadata(
            date=str(date.today()),
            project=project,
            participants=extracted["participants"],
            source_file=source_file,
        )
        return MeetingProtocol(
            metadata=metadata,
            key_decisions=extracted["decisions"],
            action_items=extracted["action_items"],
            critical_numbers=extracted["critical_numbers"],
            open_questions=extracted["open_questions"],
            risks=extracted["risks"],
        )


class VerificationAgent:
    def run(self, protocol: MeetingProtocol) -> VerificationReport:
        report = VerificationReport()
        if not protocol.key_decisions:
            report.missing_fields.append("key_decisions")
        if not protocol.action_items:
            report.missing_fields.append("action_items")
        if not protocol.critical_numbers:
            report.missing_fields.append("critical_numbers")
        low_conf = [cn for cn in protocol.critical_numbers if cn.confidence < 0.7]
        report.low_confidence_items.extend(
            [
                f"{cn.value} {cn.unit} ({cn.speaker} @ {cn.timestamp})"
                for cn in low_conf
            ]
        )
        seen: dict[tuple[str, str], float] = {}
        for cn in protocol.critical_numbers:
            key = (cn.context.lower(), cn.unit.lower())
            if key in seen and seen[key] != cn.value:
                report.conflicts.append(
                    f"Conflicting values for {cn.unit} in context '{cn.context}'"
                )
            seen[key] = cn.value
        return report


class Orchestrator:
    def __init__(self) -> None:
        self.cleanup_agent = TranscriptionCleanupAgent()
        self.extract_agent = InformationExtractionAgent()
        self.writer_agent = ProtocolWriterAgent()
        self.verify_agent = VerificationAgent()

    def run(self, transcript: str, project: str, source_file: str, memory: DomainMemory) -> MeetingProtocol:
        cleaned = self.cleanup_agent.run(transcript)
        extracted = self.extract_agent.run(cleaned, memory)
        protocol = self.writer_agent.run(extracted, project=project, source_file=source_file)
        protocol.verification = self.verify_agent.run(protocol)
        protocol.validate()
        return protocol

