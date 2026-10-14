import pytest

from audio_protocols.models import Transcript, TranscriptSegment
from audio_protocols.protocol_generators import (
    MockResultProtocolGenerator,
    ProtocolGenerationError,
)
from audio_protocols.protocols import (
    ActionItem,
    DecisionItem,
    EvidenceRange,
    OpenPointItem,
    ProtocolQuality,
    ProtocolValidationError,
    QualityNote,
    ResultProtocol,
    validate_result_protocol,
)


def synthetic_transcript() -> Transcript:
    texts = [
        "Guten Morgen zusammen. Bevor wir anfangen, noch kurz zum Wetter.",
        "Wir beschließen, dass die neue Dokumentvorlage ab November verwendet wird.",
        "Also, die neue Vorlage soll ab November eingesetzt werden.",
        "Tobias erstellt die Vorlage bis zum 15. November.",
        "Lisa prüft anschließend die Inhalte. Einen genauen Termin haben wir dafür noch nicht.",
        "Nebenbei müssen wir irgendwann über das Sommerfest sprechen.",
        "Offen ist noch, wer die Kosten der zusätzlichen Lizenzen übernimmt.",
        "Zunächst war Montag für die Veröffentlichung vorgesehen.",
        "Nach Prüfung der Abhängigkeiten verschieben wir die Veröffentlichung auf Mittwoch.",
        "Ja, Mittwoch ist der bestätigte Termin.",
    ]
    return Transcript(
        source_file="synthetic-meeting.wav",
        model="test",
        segments=[
            TranscriptSegment(start=index * 10.0, end=index * 10.0 + 5.0, text=text)
            for index, text in enumerate(texts)
        ],
    )


def expected_result() -> ResultProtocol:
    return ResultProtocol(
        source_file="synthetic-meeting.wav",
        title="Synthetische Besprechung",
        decisions=[
            DecisionItem(
                text="Die neue Dokumentvorlage wird ab November verwendet.",
                status="confirmed",
                evidence=[EvidenceRange(10.0, 25.0)],
            ),
            DecisionItem(
                text="Die Veröffentlichung findet am Mittwoch statt.",
                status="confirmed",
                evidence=[EvidenceRange(80.0, 105.0)],
            ),
        ],
        actions=[
            ActionItem(
                task="Die Vorlage erstellen.",
                responsible="Tobias",
                deadline="15. November",
                deadline_status="stated",
                status="confirmed",
                evidence=[EvidenceRange(30.0, 35.0)],
            ),
            ActionItem(
                task="Die Inhalte prüfen.",
                responsible="Lisa",
                deadline=None,
                deadline_status="not_mentioned",
                status="confirmed",
                evidence=[EvidenceRange(40.0, 45.0)],
            ),
        ],
        open_points=[
            OpenPointItem(
                text="Die Zuständigkeit für die Kosten der zusätzlichen Lizenzen ist offen.",
                status="open",
                evidence=[EvidenceRange(60.0, 65.0)],
            )
        ],
        quality=ProtocolQuality(),
    )


def test_mock_generator_returns_valid_result_protocol() -> None:
    transcript = synthetic_transcript()
    result = MockResultProtocolGenerator(expected_result()).generate(transcript)

    payload = result.to_dict()
    validate_result_protocol(payload)

    assert len(payload["decisions"]) == 2
    assert len(payload["actions"]) == 2
    assert len(payload["open_points"]) == 1
    assert payload["actions"][1]["deadline"] is None
    assert payload["actions"][1]["deadline_status"] == "not_mentioned"
    assert payload["decisions"][1]["text"].endswith("Mittwoch statt.")


def test_synthetic_result_contains_evidence_and_excludes_irrelevant_text() -> None:
    payload = expected_result().to_dict()

    for category in ("decisions", "actions", "open_points"):
        assert all(item["evidence"] for item in payload[category])

    all_evidence = [
        evidence
        for category in ("decisions", "actions", "open_points")
        for item in payload[category]
        for evidence in item["evidence"]
    ]
    assert not any(evidence["start_seconds"] in {0.0, 50.0} for evidence in all_evidence)
    assert payload["decisions"][0]["text"] != (
        "Also, die neue Vorlage soll ab November eingesetzt werden."
    )


def test_schema_rejects_item_without_evidence() -> None:
    payload = expected_result().to_dict()
    payload["actions"][0]["evidence"] = []

    with pytest.raises(ProtocolValidationError, match="mindestens einen Evidenzbereich"):
        validate_result_protocol(payload)


@pytest.mark.parametrize(
    "evidence",
    [
        [{"start_seconds": -1.0, "end_seconds": 2.0}],
        [{"start_seconds": 4.0, "end_seconds": 3.0}],
        [{"start_seconds": "not-a-number", "end_seconds": 3.0}],
    ],
)
def test_schema_rejects_invalid_evidence_ranges(evidence) -> None:
    payload = expected_result().to_dict()
    payload["decisions"][0]["evidence"] = evidence

    with pytest.raises(ProtocolValidationError):
        validate_result_protocol(payload)


@pytest.mark.parametrize(
    "mutation, message",
    [
        (lambda payload: payload.pop("actions"), "Fehlende Felder"),
        (
            lambda payload: payload["decisions"][0].update(status="maybe"),
            "status ist ungültig",
        ),
        (
            lambda payload: payload["actions"][1].update(
                deadline="morgen", deadline_status="unknown"
            ),
            "deadline_status ist ungültig",
        ),
    ],
)
def test_schema_rejects_missing_fields_and_unknown_statuses(mutation, message) -> None:
    payload = expected_result().to_dict()
    mutation(payload)

    with pytest.raises(ProtocolValidationError, match=message):
        validate_result_protocol(payload)


def test_quality_notes_can_reference_conflicting_evidence() -> None:
    result = expected_result()
    result = ResultProtocol(
        source_file=result.source_file,
        title=result.title,
        decisions=result.decisions,
        actions=result.actions,
        open_points=result.open_points,
        quality=ProtocolQuality(
            unresolved_conflicts=[
                QualityNote(
                    message="Montag und Mittwoch wurden als Veröffentlichungstermin genannt.",
                    evidence=[EvidenceRange(70.0, 95.0)],
                )
            ]
        ),
    )

    payload = result.to_dict()
    validate_result_protocol(payload)
    assert payload["quality"]["unresolved_conflicts"][0]["evidence"]


def test_mock_generator_rejects_wrong_transcript_source() -> None:
    transcript = synthetic_transcript()
    other_transcript = Transcript(source_file="other.wav", model="test")

    generator = MockResultProtocolGenerator(expected_result())
    with pytest.raises(ProtocolGenerationError, match="Transkriptquelle"):
        generator.generate(other_transcript)

    assert transcript.source_file == "synthetic-meeting.wav"


def test_missing_owner_and_deadline_are_explicit_nulls() -> None:
    payload = expected_result().to_dict()
    payload["actions"][1]["responsible"] = None
    payload["actions"][1]["deadline"] = None
    payload["actions"][1]["deadline_status"] = "not_mentioned"

    validate_result_protocol(payload)

    assert payload["actions"][1]["responsible"] is None
    assert payload["actions"][1]["deadline"] is None
