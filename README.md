# Audio-Protocols

**Ein modulares, lokal ausführbares System zur Transkription von Audioaufnahmen und zur Erstellung strukturierter Protokolle.**

## Projektidee

Audio-Protocols soll gesprochene Inhalte in nachvollziehbare, strukturierte und überprüfbare Dokumente überführen. Der Schwerpunkt liegt auf einer modularen Verarbeitungskette: von der Audioaufnahme über die Transkription bis hin zu unterschiedlichen Protokollformaten.

Das Projekt wird zunächst für den Betrieb auf einem handelsüblichen Notebook entwickelt. Langfristig soll es sich auch auf eigener Hardware als lokaler Dienst betreiben lassen.

## Grundprinzipien

- **Local-first:** Audioverarbeitung und spätere Protokollerstellung sollen möglichst lokal erfolgen.
- **Datenschutz:** Aufnahmen und daraus erzeugte Inhalte sollen nicht ohne ausdrückliche Entscheidung an externe Dienste übermittelt werden.
- **Modularität:** Einzelne Komponenten sollen austauschbar bleiben, beispielsweise Transkriptionsmodelle und Sprachmodelle.
- **Nachvollziehbarkeit:** Ergebnisse sollen lesbar, überprüfbar und bei Bedarf manuell korrigierbar sein.
- **Ressourcenschonung:** Die Entwicklung orientiert sich zunächst an vorhandener Hardware und einem möglichst kostengünstigen Betrieb.

## Vorgesehene Protokolltypen

Das System ist auf drei fachlich unterschiedliche Protokollarten ausgerichtet:

### Ergebnisprotokoll

Hält die verbindlichen Ergebnisse einer Besprechung fest. Im Mittelpunkt stehen Entscheidungen, Maßnahmen mit Verantwortlichkeiten und Fristen sowie noch offene Punkte. Wiederholungen und nicht beschlussrelevante Diskussionen werden nicht übernommen.

### Verlaufsprotokoll

Dokumentiert den Diskussionsverlauf thematisch gegliedert und in seiner zeitlichen beziehungsweise logischen Reihenfolge. Es hält Positionen, Gegenargumente, Begründungen, Konsens und verbleibende Kontroversen fest. Vertagte Punkte bleiben mit ihrem letzten Diskussionsstand nachvollziehbar.

### Technisches Prüf- und Befundprotokoll (Labor & Baustelle)

Strukturiert technische Prüfungen und Befunde. Prüfgegenstand und Randbedingungen werden ebenso erfasst wie objektive Beobachtungen und Messwerte, genannte Anforderungen sowie die Bewertung möglicher Abweichungen. Erforderliche Folgemaßnahmen werden getrennt dokumentiert; Unsicherheiten und Einschätzungen bleiben als solche erkennbar.

## Technischer Ansatz

Die Verarbeitung ist als Pipeline vorgesehen:

1. Audiodatei einlesen und prüfen
2. Audiosignal bei Bedarf vorbereiten
3. Audio lokal transkribieren und Zeitstempel erzeugen
4. Optional Sprecher unterscheiden
5. Inhalte anhand des gewählten Protokolltyps strukturieren
6. Ergebnisse prüfen und in geeignete Formate exportieren

Als Ausgangsbasis sind Python und `faster-whisper` für die lokale Transkription vorgesehen. Für strukturierte Ergebnisse sind zunächst Markdown und JSON geplant. Weitere Komponenten sollen erst ergänzt werden, wenn sie für den jeweiligen Entwicklungsschritt benötigt werden.

## Entwicklungsstand

Der erste Entwicklungsschritt, MVP 1, umfasst eine lokal ausführbare Python-
Kommandozeile für WAV- und MP3-Dateien. Sie verwendet `faster-whisper` mit
CPU/INT8 als Standard, erkennt die Sprache automatisch und erzeugt JSON- sowie
Markdown-Ausgaben mit Zeitstempeln. Die Einrichtung und Bedienung ist in
[`docs/MVP1.md`](docs/MVP1.md) beschrieben.

Sprechererkennung, die automatische Erstellung der drei Protokolltypen und
weitere Exportformate sind nachgelagerte Ausbaustufen.

## Datenschutz und Umgang mit Daten

Audioaufnahmen, Transkripte und erzeugte Protokolle können vertrauliche Inhalte enthalten. Solche Dateien sollten lokal gespeichert und nicht in das öffentliche Git-Repository aufgenommen werden. Vor der Verarbeitung sind gegebenenfalls die erforderlichen Einwilligungen und organisatorischen Vorgaben zu klären.

Die lokale Verarbeitung von Audiodaten bedeutet nicht zwangsläufig, dass auch die Beschaffung von Software oder Modellgewichten offline erfolgt: Ein erstmaliger Download kann eine Internetverbindung benötigen.

## Hintergrund und verwendete Projekte

Das Projekt orientiert sich unter anderem an folgenden Open-Source-Projekten:

- [faster-whisper](https://github.com/SYSTRAN/faster-whisper) – effiziente Whisper-Transkription
- [WhisperX](https://github.com/m-bain/whisperX) – Transkription mit zusätzlichen Funktionen wie Alignment und Sprecherzuordnung
- [pyannote.audio](https://github.com/pyannote/pyannote-audio) – Werkzeuge zur Analyse und Sprecher-Diarisierung
- [whisper.cpp](https://github.com/ggml-org/whisper.cpp) – Whisper-Inferenz in C/C++ mit Fokus auf effiziente lokale Ausführung

Die Nennung dient der technischen Orientierung und stellt keine Aussage dar, dass diese Komponenten bereits integriert sind. Lizenzen, Hardwareanforderungen und Nutzungsbedingungen werden vor einer Integration geprüft.
