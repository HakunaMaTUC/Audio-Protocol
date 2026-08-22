# Audio-Protocol

Agentic toolkit for converting laboratory discussion transcripts into a strict, auditable protocol format.

## Features

- Strict protocol schema with required fields
- Multi-agent pipeline:
  1. transcription cleanup
  2. information extraction
  3. protocol writing
  4. verification
- Critical-number traceability (value, unit, speaker, timestamp, source quote, confidence)
- Domain memory layer (glossary + recurring entities)
- Human-in-the-loop review flow
- Searchable SQLite storage and QA retrieval with citations
- Quality metrics utilities (precision, recall, completeness, correction rate)

## Quick start

```bash
python -m audio_protocol.analyze \
  --transcript /absolute/path/to/transcript.txt \
  --project "Catalyst Study" \
  --protocol-out /absolute/path/to/protocol.json \
  --db /absolute/path/to/protocols.db \
  --memory /absolute/path/to/domain_memory.json
```

Run with interactive review:

```bash
python -m audio_protocol.analyze \
  --transcript /absolute/path/to/transcript.txt \
  --project "Catalyst Study" \
  --review
```

Ask a follow-up question:

```bash
python -m audio_protocol.query \
  --db /absolute/path/to/protocols.db \
  --question "What concentration did we agree on last Tuesday?"
```

## Transcript input format

Preferred line format:

```text
[00:01:12] Alice: We agreed on 2.5 mg/mL for sample A.
```

If timestamps are missing, the cleanup agent auto-generates them.