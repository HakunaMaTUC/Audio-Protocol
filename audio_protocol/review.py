from __future__ import annotations

from .schema import MeetingProtocol


def review_protocol(protocol: MeetingProtocol) -> tuple[MeetingProtocol, int, int]:
    corrections = 0
    reviewed_items = 0

    for i, item in enumerate(protocol.critical_numbers, start=1):
        reviewed_items += 1
        print(
            f"[Critical #{i}] {item.value} {item.unit} | {item.speaker} @ {item.timestamp}\n"
            f"Quote: {item.source_quote}"
        )
        keep = input("Keep this value? [Y/n]: ").strip().lower()
        if keep == "n":
            new_val = input("New value: ").strip()
            new_unit = input("New unit: ").strip()
            if new_val:
                item.value = float(new_val)
            if new_unit:
                item.unit = new_unit
            corrections += 1

    for i, decision in enumerate(protocol.key_decisions, start=1):
        reviewed_items += 1
        print(f"[Decision #{i}] {decision}")
        keep = input("Keep this decision? [Y/n]: ").strip().lower()
        if keep == "n":
            replacement = input("Replacement decision: ").strip()
            if replacement:
                protocol.key_decisions[i - 1] = replacement
                corrections += 1

    protocol.verification.reviewed_by_human = True
    return protocol, corrections, reviewed_items

