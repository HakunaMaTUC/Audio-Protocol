# MVP 1 – Lokale Transkription

MVP 1 verarbeitet eine WAV- oder MP3-Datei lokal mit `faster-whisper` und
schreibt ein JSON- sowie ein Markdown-Transkript. Sprechererkennung,
Protokollerstellung und ein LLM sind noch nicht Bestandteil dieses Meilensteins.

## Windows-Einrichtung

Im Repository-Ordner ein PowerShell-Terminal öffnen:

```powershell
py -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
python -m pip install -e ".[test]"
```

Die Projektabhängigkeiten begrenzen PyAV bewusst auf eine kompatible Version
unter 19. Dadurch wird ein bekannter Konflikt zwischen aktuellen PyAV-
Versionen und veröffentlichten `faster-whisper`-Versionen vermieden. Bei einer
bereits eingerichteten Umgebung kann die Korrektur direkt angewendet werden:

```powershell
python -m pip install --upgrade "av<19"
python -m pip install -e ".[test]"
```

Falls PowerShell die Aktivierung wegen der lokalen Ausführungsrichtlinie
blockiert, kann sie für das aktuelle Terminal erlaubt werden:

```powershell
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
.\.venv\Scripts\Activate.ps1
```

Die Modell-Dateien werden beim ersten Einsatz heruntergeladen, sofern sie noch
nicht im lokalen Cache vorhanden sind. Dieser Download ist kein Upload der
eigenen Audiodatei. Die eigentliche Transkription läuft lokal.

## Tests

```powershell
python -m pytest
```

Die Tests verwenden keine privaten Aufnahmen und laden kein Whisper-Modell
herunter. Der Transkriptionsaufruf wird in den Tests simuliert.

## Transkription starten

Mit der Standardkonfiguration (`small`, CPU, INT8):

```powershell
python -m audio_protocols "C:\Pfad\zur\aufnahme.wav"
```

Oder über den installierten Konsolenbefehl:

```powershell
audio-protocols "C:\Pfad\zur\aufnahme.mp3"
```

Ein anderes faster-whisper-Modell kann ohne Quellcodeänderung gewählt werden:

```powershell
python -m audio_protocols "C:\Pfad\zur\aufnahme.wav" --model medium
```

Die Standardeinstellungen sind:

- `--model small`
- `--device cpu`
- `--compute-type int8`
- automatische Spracherkennung
- Transkription ohne Übersetzung

Weitere Optionen:

```powershell
python -m audio_protocols --help
```

Während der Verarbeitung werden regelmäßig die bereits eingelesenen Segmente
und die zuletzt erreichte Audioposition angezeigt. Bei langen Aufnahmen kann
die CPU-Transkription trotzdem mehrere Minuten dauern; die Ausgabedateien
werden erst nach erfolgreichem Abschluss geschrieben.

## Ausgaben

Standardmäßig werden beide Dateien unter `outputs/transcripts/` abgelegt:

```text
outputs/transcripts/
├── aufnahme.json
└── aufnahme.md
```

Das Verzeichnis ist durch `.gitignore` vom öffentlichen Repository
ausgeschlossen. Bereits vorhandene Ausgaben werden nicht ohne ausdrückliche
Option überschrieben:

```powershell
python -m audio_protocols "C:\Pfad\zur\aufnahme.wav" --overwrite
```

Das JSON enthält den Dateinamen, das Modell und – soweit von
`faster-whisper` geliefert – erkannte Sprache, Spracherkennungswahrscheinlichkeit,
Dauer sowie Start, Ende und Text jedes Segments. Nicht verfügbare optionale
Metadaten werden nicht erfunden.

## Sprache und gemischte Aufnahmen

Es wird keine feste Sprache erzwungen. `faster-whisper` erhält standardmäßig
`language=None` und `task="transcribe"`; dadurch wird die erkannte Sprache
beibehalten und nicht automatisch ins Deutsche oder Englische übersetzt.

Für die Entwicklung sollten kurze, unkritische Testaufnahmen getrennt geprüft
werden:

1. überwiegend deutsch;
2. überwiegend englisch;
3. Deutsch-Englisch-Wechsel mit Fachbegriffen.

MVP 1 speichert die von `faster-whisper` gelieferte erkannte Sprache als
Transkript-Metadatum. Eine verlässliche Spracherkennung für jeden einzelnen
Abschnitt ist mit diesem ersten Adapter noch nicht zugesichert und bleibt eine
offene Test- und Architekturfrage.

## Bekannte Grenzen

- Sprecher werden nicht unterschieden.
- Es werden keine Protokolle, Zusammenfassungen oder Aufgaben erzeugt.
- Die Qualität hängt stark von Aufnahme, Mikrofon, Dialekt, Fachbegriffen und
  Sprachwechseln ab.
- Größere Modelle können auf einer CPU deutlich länger laufen und mehr
  Arbeitsspeicher benötigen. Die passende Modellgröße wird auf dem Notebook
  gemessen, nicht pauschal behauptet.
- Die Lizenz- und Modellbedingungen werden vor einer produktiven Nutzung
  gesondert geprüft.
