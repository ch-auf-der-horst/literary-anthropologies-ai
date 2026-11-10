# Lokale Validierung – 10. November 2026

Geprüft wurde dieses Publikationssupplement, nicht die unabhängige wissenschaftliche Gültigkeit aller Kodierungen.

- Neuberechnung aller 84 Wortformvergleiche: 14 Formen × drei Auswahlvarianten × zwei Textfassungen; Häufigkeiten, Nenner, Dokumentstreuung, Normalisierung und G² stimmen mit dem archivierten Prüfbericht überein.
- 49 eindeutige Artikel pro Textfassung; Entfernung der englischen Modellgeschichte verändert den Nenner um genau 1.217 Tokens. Keine Richtungswechsel gegenüber der historischen Referenz.
- Familienzuordnungen: 32 eindeutige chinesische Fälle in zwölf Familien; 23 deutsche BookTok-A-Fälle einschließlich eines nicht zugeordneten Falls sowie elf englische A-Fälle. Erneut ausgezählte Häufigkeiten stimmen mit dem Familienprüfbericht überein.
- Alle Mengenflüsse der ersten Abbildung bilanziert; PDF-Seitenmaße und zentrale Beschriftungen beider Abbildungen geprüft.
- Beide Abbildungen aus einer separaten Kopie unter einem anderen Pfad vollständig neu erzeugt. Die erzeugten PNGs sind pixelidentisch zu den gelieferten finalen Fassungen. Die Auswertung erzeugt dort dieselben Ergebnisdateien.
- Sieben automatisierte Tests erfolgreich; mathematische Randfälle eingeschlossen.
- Textdateien auf lokale Benutzerpfade und verbreitete Schlüssel-/Private-Key-Muster geprüft; keine Treffer. Keine vollständigen Artikel, Captions oder Transkripte übernommen. Das ist eine gezielte Prüfung, kein umfassendes Geheimnis- oder Rechteaudit.

Die Pfadprüfung erfolgte in einer frischen Verzeichniskopie mit der vorhandenen Python-Umgebung, nicht in einer neu installierten Umgebung und nicht auf GitHub Actions. Verwendet: Python 3.12.14, ReportLab 4.4.9, Pillow 13.0.0 und pypdf 6.21.4; zusätzlich Poppler/pdftoppm. Die Python-Paketstände sind in requirements.txt festgehalten.

Grenzen: Der Tokenisierungsschritt benötigt nicht veröffentlichte Volltexte. Der zusätzliche Metadaten-Stresstest ist nur aggregiert dokumentiert. Historische KI-Läufe und interpretative Kategorienbildung werden nicht erneut ausgeführt. Die vollständigen offenen Kodiertabellen und das Retrievalarchiv sind nicht enthalten. Es wurde kein GitHub-Remote angelegt. Eigene Inhalte stehen unter CC BY 4.0 (Daten, Dokumentation, Abbildungen) bzw. MIT (Skripte); siehe LICENSE.
