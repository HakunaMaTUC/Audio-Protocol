"""Kommandozeilenschnittstelle für MVP 1."""

import argparse
from pathlib import Path
from typing import Sequence

from .outputs import format_timestamp, write_outputs
from .transcriber import TranscriptionError, transcribe_audio
from .validation import (
    AudioInputError,
    OutputExistsError,
    ensure_output_paths_available,
    output_paths,
    validate_audio_path,
)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="audio-protocols",
        description="Lokale Transkription einer WAV- oder MP3-Datei.",
    )
    parser.add_argument("audio_file", help="Pfad zur WAV- oder MP3-Datei")
    parser.add_argument(
        "--model",
        default="small",
        help="faster-whisper-Modell (Standard: small)",
    )
    parser.add_argument(
        "--output-dir",
        default="outputs/transcripts",
        help="Ausgabeverzeichnis (Standard: outputs/transcripts)",
    )
    parser.add_argument(
        "--model-cache-dir",
        type=Path,
        default=None,
        help="Optionales Verzeichnis für heruntergeladene Modell-Dateien",
    )
    parser.add_argument(
        "--device",
        default="cpu",
        help="Rechengerät (Standard: cpu)",
    )
    parser.add_argument(
        "--compute-type",
        default="int8",
        help="Quantisierung für faster-whisper (Standard: int8)",
    )
    parser.add_argument(
        "--overwrite",
        action="store_true",
        help="Vorhandene JSON-/Markdown-Ausgaben bewusst überschreiben",
    )
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    args = build_parser().parse_args(argv)

    try:
        audio_path = validate_audio_path(args.audio_file)
        paths = output_paths(audio_path, args.output_dir)
        ensure_output_paths_available(paths, overwrite=args.overwrite)

        print(f"Eingabe: {audio_path}")
        print(
            f"Transkription: Modell={args.model}, "
            f"device={args.device}, compute_type={args.compute_type}"
        )
        print(
            "Sprache: automatisch erkennen, Originalsprache beibehalten "
            "(keine Übersetzung)"
        )
        print("Modell wird geladen; beim ersten Einsatz kann ein Download erfolgen ...")

        def report_progress(segment_count: int, audio_seconds: float) -> None:
            print(
                f"\rFortschritt: {segment_count} Segmente, "
                f"Audio bis {format_timestamp(audio_seconds)}",
                end="",
                flush=True,
            )

        transcript = transcribe_audio(
            audio_path,
            model_name=args.model,
            device=args.device,
            compute_type=args.compute_type,
            model_cache_dir=args.model_cache_dir,
            progress_callback=report_progress,
        )
        if transcript.segments:
            print()
        json_path, markdown_path = write_outputs(
            transcript,
            audio_path,
            args.output_dir,
            overwrite=args.overwrite,
        )
    except (AudioInputError, OutputExistsError, TranscriptionError) as exc:
        print(f"Fehler: {exc}")
        return 2

    print(f"JSON gespeichert: {json_path}")
    print(f"Markdown gespeichert: {markdown_path}")
    return 0
