# Audio-Protocol

Praxisnahes Konzept für professionelle KI-Protokolle aus Audioaufnahmen mit Fokus auf:

- **Audioaufnahme → Transkription → Diarization → strukturiertes Protokoll → QA/Export**
- **DSGVO, Offline-Verarbeitung, deutsche Sprache**
- **modularer Aufbau statt proprietärer „Black-Box“-Recorder**

---

## 1) Vergleich: Eigenes Codex-Projekt/Agenten-Workflow vs. Open Source

### A. Eigenes Codex-/Agenten-Workflow (empfohlen für dieses Repo)

**Zielbild:** Ein modularer, lokal betreibbarer Pipeline-Ansatz, bei dem jeder Schritt austauschbar ist.

1. **Ingest/Audio-Normalisierung**
   - Eingang: WAV/MP3/M4A vom Recorder
   - Optional: `ffmpeg`-Normalisierung (mono, 16 kHz für ASR)
2. **ASR (Whisper/WhisperX)**
   - robuste deutsche Transkription
   - Wort-/Segment-Zeitstempel
3. **Sprechererkennung (Diarization)**
   - pyannote-basierte Sprechersegmente
4. **Strukturierte Protokollerstellung**
   - Template-basiert (TOPs, Beschlüsse, Aufgaben, Fristen, Owner)
5. **Qualitätssicherung**
   - Confidence-/Längen-Checks, „unklare Passagen“-Liste, manuelle Freigabe
6. **Export**
   - Markdown, DOCX, JSON, SRT/VTT

**Vorteile:** maximale Kontrolle, lokal/offline möglich, DSGVO-freundlich, anpassbar an Teamprozesse.

### B. Relevante Open-Source-Projekte auf GitHub

| Projekt | Fokus | Stärken im Ziel-Workflow | Lizenz |
|---|---|---|---|
| [momente-organisieren/protokolla](https://github.com/momente-organisieren/protokolla) | End-to-End Web-App (lokal) | WhisperX + Diarization + Zusammenfassungen + Export | MIT |
| [kaixxx/noScribe](https://github.com/kaixxx/noScribe) | Desktop-Transkription | Lokal, Sprechertrennung, Editor, mehrsprachig inkl. Deutsch | GPL-3.0 |
| [m-bain/whisperX](https://github.com/m-bain/whisperX) | ASR-Backend/Toolkit | schnelle Batch-Transkription, Wort-Alignment, Diarization-Anbindung | BSD-2-Clause |
| [pyannote/pyannote-audio](https://github.com/pyannote/pyannote-audio) | Diarization-Baustein | De-facto-Standard für Speaker Diarization | MIT |
| [ggml-org/whisper.cpp](https://github.com/ggml-org/whisper.cpp) | Lokale ASR-Inferenz (C/C++) | sehr effizient/offline, gut für ressourcenschwache Systeme | MIT |
| [openai/whisper](https://github.com/openai/whisper) | Basismodell ASR | stabile Referenz für multilinguales STT | MIT |

**Einordnung:**  
- Für **schnellen Start**: `protokolla` oder `noScribe`.  
- Für **eigene professionelle Pipeline**: `whisperX + pyannote + eigene Protokoll-Templates + QA-Schicht`.

---

## 2) Konkrete modulare Empfehlung (Praxis-Workflow)

### Empfohlene Referenz-Architektur

1. **Aufnahme**
   - Recorder mit gutem Stereo-Rohsignal (WAV bevorzugt)
2. **Datenübertragung**
   - USB-C oder microSD, keine Cloud-Zwangssynchronisation
3. **Vorverarbeitung**
   - Lautheit/Normalisierung, optional VAD
4. **Transkription**
   - WhisperX (deutsche Meetings: `medium` oder `large-v3`)
5. **Diarization**
   - pyannote (`min/max speakers` passend setzen)
6. **Strukturierung**
   - Lokales LLM (z. B. Ollama) mit fixen Prompt-Templates:
     - Zusammenfassung
     - Beschlüsse
     - Aufgaben (Owner, Deadline, Priorität)
7. **QA-Gate**
   - Menschliche Freigabe + automatische Checks
8. **Export**
   - Markdown/DOCX für Protokoll, JSON für Archiv/Weiterverarbeitung

### Qualitätsregeln (minimal, aber wirksam)

- Unklare Stellen markieren (`[UNSICHER]`) statt halluzinieren.
- Namen/Entscheidungen nur übernehmen, wenn im Audio erkennbar.
- Action-Items nur mit explizitem Sprecherbezug.
- Endprotokoll immer manuell abnehmen (Vier-Augen-Prinzip bei kritischen Meetings).

---

## 3) Datenschutz / DSGVO / Offline

- **Rechtsgrundlage & Information:** Vor Aufnahme transparent informieren und Einwilligungen/Regeln klären.
- **Datenminimierung:** Audio nur so lange wie nötig speichern; Transkript ggf. bevorzugen.
- **Speicherbegrenzung:** Löschfristen pro Meeting-Typ definieren.
- **Lokale Verarbeitung:** ASR/Diarization/LLM on-prem oder auf dedizierten EU-Systemen.
- **Zugriffsschutz:** verschlüsselte Datenträger, rollenbasierter Zugriff, Audit-Log.
- **Keine proprietäre Recorder-Cloud als Pflichtpfad**, wenn sensible Inhalte verarbeitet werden.

---

## 4) Hardware-Empfehlungen (Sprache/Meetings, KI-geeignet)

> Preisstände sind Richtwerte (DE/EU, Stand 2026-08) und schwanken je nach Shop/Verfügbarkeit.

| Gerät | Typische Preisspanne | Warum geeignet für KI-Workflow | Bezugsquellen (Beispiele) |
|---|---:|---|---|
| **Zoom H1essential** | ca. **96–109 €** | 32-bit float, gute Roh-Audioqualität, USB-C, microSD | Thomann, Idealo, Geizhals, Amazon |
| **Tascam DR-05X** | ca. **131 € neu** (gebraucht oft günstiger) | bewährte Sprach-/Interviewqualität, manuelle Pegelkontrolle, microSD/USB | Fachhandel (z. B. Toneart), eBay/Kleinanzeigen |
| **Sony ICD-UX570** | ca. **88–110 €** | kompakt, sehr gut für Sprache, einfache Dateiübertragung | Amazon, MediaMarkt/Saturn |
| **Philips DVT4110** | ca. **88–112 €** | solide Meeting-Aufnahmen, unkomplizierte Handhabung | MediaMarkt, Amazon, OTTO, Galaxus |

### Kaufkriterien (wichtig)

- Aufnahmeformat: **WAV/PCM bevorzugen**
- Schnittstelle: **USB-C** oder zuverlässige **microSD**
- Rauschverhalten im Meetingraum (Praxisprobe!)
- Kein Vendor-Lock-in durch verpflichtende Cloud-App

---

## 5) Kurzfazit (konkrete Empfehlung)

Für ein professionelles, bezahlbares und DSGVO-freundliches Setup:

1. **Hardware:** `Zoom H1essential` (Preis/Leistung) oder `Tascam DR-05X` (robuste Praxiswahl).  
2. **Pipeline:** `WhisperX + pyannote + lokales LLM + manuelles QA-Gate`.  
3. **Betriebsmodell:** lokal/offline-first, klare Lösch- und Zugriffskonzepte.  
4. **Output-Standard:** Protokoll als Markdown/DOCX + JSON-Ablage für Nachvollziehbarkeit.

Damit entsteht ein modulares System, das heute produktiv nutzbar ist und sich später ohne Komplettumbau erweitern lässt.

---

## Quellen (Auswahl)

- GitHub Repositories/Lizenzen:  
  - https://github.com/openai/whisper  
  - https://github.com/ggml-org/whisper.cpp  
  - https://github.com/m-bain/whisperX  
  - https://github.com/pyannote/pyannote-audio  
  - https://github.com/kaixxx/noScribe  
  - https://github.com/momente-organisieren/protokolla
- Preis-/Produktübersichten (DE/EU):  
  - https://www.thomann.de/de/zoom_h1essential.htm  
  - https://www.idealo.de/preisvergleich/OffersOfProduct/204404406_-h1essential-zoom.html  
  - https://geizhals.de/zoom-h1essential-v213379.html  
  - https://www.mediamarkt.de/de/product/_philips-voicetracer-audiorecorder-dvt4110-diktie-94856569.html  
  - https://www.amazon.de/Zoom-H1essential-32-Bit-Recorder-schwarz/dp/B0CSL4PXDV  