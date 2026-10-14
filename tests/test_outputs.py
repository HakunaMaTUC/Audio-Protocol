import json
from pathlib import Path

import pytest

from audio_protocols.models import Transcript, TranscriptSegment
from audio_protocols.outputs import format_timestamp, render_markdown, write_outputs
from audio_protocols.validation import OutputExistsError


def sample_transcript() -> Transcript:
    return Transcript(
        source_file="meeting.wav",
        model="small",
        language="de",
        language_probability=0.91,
        duration_seconds=12.5,
        segments=[
            TranscriptSegment(start=0.0, end=2.25, text=" Guten Morgen. "),
            TranscriptSegment(start=2.25, end=12.5, text="Das ist ein Test."),
        ],
    )


def test_timestamp_format() -> None:
    assert format_timestamp(0) == "00:00:00.000"
    assert format_timestamp(3723.456) == "01:02:03.456"


def test_json_and_markdown_outputs(tmp_path: Path) -> None:
    audio_path = tmp_path / "meeting.wav"
    audio_path.write_bytes(b"test")

    json_path, markdown_path = write_outputs(
        sample_transcript(), audio_path, tmp_path / "outputs"
    )

    payload = json.loads(json_path.read_text(encoding="utf-8"))
    markdown = markdown_path.read_text(encoding="utf-8")

    assert payload["source_file"] == "meeting.wav"
    assert payload["language"] == "de"
    assert payload["segments"][0]["start_seconds"] == 0.0
    assert payload["segments"][1]["end_seconds"] == 12.5
    assert "[00:00:00.000 – 00:00:02.250]" in markdown
    assert "Guten Morgen." in markdown


def test_missing_optional_metadata_is_omitted() -> None:
    transcript = Transcript(source_file="unknown.wav", model="small")

    payload = transcript.to_dict()

    assert "language" not in payload
    assert "language_probability" not in payload
    assert "duration_seconds" not in payload


def test_existing_outputs_are_not_overwritten_without_flag(tmp_path: Path) -> None:
    audio_path = tmp_path / "meeting.wav"
    output_dir = tmp_path / "outputs"
    audio_path.write_bytes(b"test")
    output_dir.mkdir()
    (output_dir / "meeting.json").write_text("original", encoding="utf-8")

    with pytest.raises(OutputExistsError):
        write_outputs(sample_transcript(), audio_path, output_dir)


def test_markdown_handles_empty_segments() -> None:
    transcript = Transcript(source_file="empty.wav", model="small")

    assert "Keine Transkriptsegmente" in render_markdown(transcript)
