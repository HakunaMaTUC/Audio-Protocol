"""Validierung von Audioeingaben und Ausgabezielen."""

from pathlib import Path


SUPPORTED_AUDIO_SUFFIXES = {".wav", ".mp3"}


class AudioInputError(ValueError):
    """Verständlicher Fehler für ungültige Audioeingaben."""


class OutputExistsError(FileExistsError):
    """Ausgabedateien existieren bereits und würden überschrieben."""


def validate_audio_path(value: str | Path) -> Path:
    """Prüft Existenz, Dateityp und unterstützte Endung einer Audiodatei."""

    path = Path(value).expanduser()
    if not path.exists():
        raise AudioInputError(f"Audiodatei nicht gefunden: {path}")
    if not path.is_file():
        raise AudioInputError(f"Der Pfad ist keine Datei: {path}")
    if path.suffix.lower() not in SUPPORTED_AUDIO_SUFFIXES:
        supported = ", ".join(sorted(SUPPORTED_AUDIO_SUFFIXES))
        raise AudioInputError(
            f"Nicht unterstütztes Audioformat '{path.suffix}'. "
            f"Unterstützt werden: {supported}"
        )
    return path.resolve()


def output_paths(audio_path: Path, output_dir: str | Path) -> tuple[Path, Path]:
    """Erzeugt die vorhersehbaren JSON- und Markdown-Zielpfade."""

    directory = Path(output_dir).expanduser()
    stem = audio_path.stem
    return directory / f"{stem}.json", directory / f"{stem}.md"


def ensure_output_paths_available(
    paths: tuple[Path, Path], *, overwrite: bool = False
) -> None:
    """Verhindert versehentliches Überschreiben bestehender Ergebnisse."""

    if overwrite:
        return
    existing = [str(path) for path in paths if path.exists()]
    if existing:
        joined = ", ".join(existing)
        raise OutputExistsError(
            f"Ausgabedatei(en) existieren bereits: {joined}. "
            "Nutze --overwrite nur, wenn du sie bewusst ersetzen möchtest."
        )
