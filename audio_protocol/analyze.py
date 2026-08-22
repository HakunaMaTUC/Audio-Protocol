from __future__ import annotations

import argparse
import json
from pathlib import Path

from .memory import DomainMemory
from .metrics import completeness_rate, correction_rate
from .pipeline import Orchestrator
from .review import review_protocol
from .storage import ProtocolStore


def _required_fields_count(protocol_dict: dict) -> tuple[int, int]:
    required = [
        "metadata",
        "key_decisions",
        "action_items",
        "critical_numbers",
        "open_questions",
        "risks",
        "verification",
    ]
    populated = sum(1 for f in required if protocol_dict.get(f) not in (None, [], {}))
    return populated, len(required)


def main() -> None:
    parser = argparse.ArgumentParser(description="Analyze lab transcript into strict protocol.")
    parser.add_argument("--transcript", required=True)
    parser.add_argument("--project", required=True)
    parser.add_argument("--protocol-out", default="protocol.json")
    parser.add_argument("--db", default="protocols.db")
    parser.add_argument("--memory", default="domain_memory.json")
    parser.add_argument("--review", action="store_true")
    args = parser.parse_args()

    transcript_path = Path(args.transcript)
    transcript_text = transcript_path.read_text(encoding="utf-8")
    memory = DomainMemory.load(args.memory)

    orchestrator = Orchestrator()
    protocol = orchestrator.run(
        transcript=transcript_text,
        project=args.project,
        source_file=str(transcript_path),
        memory=memory,
    )

    corrections = 0
    reviewed_items = 0
    if args.review:
        protocol, corrections, reviewed_items = review_protocol(protocol)

    protocol_dict = protocol.to_dict()
    Path(args.protocol_out).write_text(json.dumps(protocol_dict, indent=2), encoding="utf-8")

    store = ProtocolStore(args.db)
    protocol_id = store.save_protocol(protocol)

    memory.recurring_entities["projects"] = sorted(
        set(memory.recurring_entities.get("projects", []) + [args.project])
    )
    memory.recurring_entities["team_members"] = sorted(
        set(memory.recurring_entities.get("team_members", []) + protocol.metadata.participants)
    )
    memory.save(args.memory)

    populated, required = _required_fields_count(protocol_dict)
    completeness = completeness_rate(populated, required)
    review_correction_rate = correction_rate(corrections, reviewed_items)

    print(f"Saved protocol #{protocol_id} to {args.db}")
    print(f"Protocol JSON: {args.protocol_out}")
    print(f"Completeness rate: {completeness:.2%}")
    print(f"Review correction rate: {review_correction_rate:.2%}")
    if protocol.verification.low_confidence_items:
        print("Low-confidence extractions:")
        for item in protocol.verification.low_confidence_items:
            print(f"- {item}")


if __name__ == "__main__":
    main()

