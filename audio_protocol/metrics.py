from __future__ import annotations


def precision_recall(predicted: set[str], expected: set[str]) -> tuple[float, float]:
    if not predicted:
        return 0.0, 0.0
    true_pos = len(predicted.intersection(expected))
    precision = true_pos / len(predicted)
    recall = true_pos / len(expected) if expected else 0.0
    return precision, recall


def completeness_rate(populated_fields: int, required_fields: int) -> float:
    if required_fields == 0:
        return 1.0
    return populated_fields / required_fields


def correction_rate(corrections: int, reviewed_items: int) -> float:
    if reviewed_items == 0:
        return 0.0
    return corrections / reviewed_items

