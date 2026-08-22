from __future__ import annotations

import argparse
from datetime import date, timedelta

from .storage import ProtocolStore

WEEKDAYS = {
    "monday": 0,
    "tuesday": 1,
    "wednesday": 2,
    "thursday": 3,
    "friday": 4,
    "saturday": 5,
    "sunday": 6,
}


def _last_weekday(target: int) -> str:
    today = date.today()
    days_back = (today.weekday() - target) % 7 or 7
    return str(today - timedelta(days=days_back))


def main() -> None:
    parser = argparse.ArgumentParser(description="Query stored protocols with citations.")
    parser.add_argument("--db", required=True)
    parser.add_argument("--question", required=True)
    args = parser.parse_args()

    store = ProtocolStore(args.db)
    question = args.question.lower().strip()

    weekday_filter = None
    for day_name, day_value in WEEKDAYS.items():
        if f"last {day_name}" in question:
            weekday_filter = _last_weekday(day_value)
            break

    results = store.query_numbers(question=question.replace("last ", ""))
    if weekday_filter:
        results = [r for r in results if r["date"] == weekday_filter]

    if not results:
        print("No matching protocol evidence found.")
        return

    print("Evidence-backed results:")
    for r in results:
        print(
            f"- [{r['date']}] {r['project']}: {r['value']} {r['unit']} "
            f"(speaker={r['speaker']}, time={r['timestamp']}, confidence={r['confidence']:.2f})"
        )
        print(f"  citation: \"{r['source_quote']}\"")


if __name__ == "__main__":
    main()

