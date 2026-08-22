from __future__ import annotations

import json
from dataclasses import dataclass, field
from pathlib import Path


@dataclass
class DomainMemory:
    glossary: dict[str, str] = field(default_factory=dict)
    recurring_entities: dict[str, list[str]] = field(
        default_factory=lambda: {"projects": [], "samples": [], "team_members": []}
    )

    @classmethod
    def load(cls, path: str) -> "DomainMemory":
        file = Path(path)
        if not file.exists():
            return cls()
        data = json.loads(file.read_text(encoding="utf-8"))
        return cls(
            glossary=data.get("glossary", {}),
            recurring_entities=data.get(
                "recurring_entities",
                {"projects": [], "samples": [], "team_members": []},
            ),
        )

    def save(self, path: str) -> None:
        Path(path).write_text(
            json.dumps(
                {
                    "glossary": self.glossary,
                    "recurring_entities": self.recurring_entities,
                },
                indent=2,
            ),
            encoding="utf-8",
        )

