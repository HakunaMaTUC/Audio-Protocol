from pathlib import Path

import pytest

from audio_protocols.validation import AudioInputError, validate_audio_path


def test_missing_audio_file_is_rejected(tmp_path: Path) -> None:
    with pytest.raises(AudioInputError, match="nicht gefunden"):
        validate_audio_path(tmp_path / "missing.wav")


def test_unsupported_audio_extension_is_rejected(tmp_path: Path) -> None:
    path = tmp_path / "notes.txt"
    path.write_text("not audio", encoding="utf-8")

    with pytest.raises(AudioInputError, match="Nicht unterstütztes Audioformat"):
        validate_audio_path(path)


def test_wav_and_mp3_extensions_are_supported(tmp_path: Path) -> None:
    wav = tmp_path / "sample.WAV"
    mp3 = tmp_path / "sample.mp3"
    wav.write_bytes(b"test")
    mp3.write_bytes(b"test")

    assert validate_audio_path(wav) == wav.resolve()
    assert validate_audio_path(mp3) == mp3.resolve()
