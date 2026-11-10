# KI und Literatur – Begleitmaterialien zum Changchun-Aufsatz

Lokales Publikationssupplement zum Manuskriptstand v7, vorbereitet am 10. November 2026. Noch nicht auf GitHub veröffentlicht. Enthalten sind die zwei finalen Abbildungen, ausgewählte Analyse- und Korpusmetadaten, historische Kategorien/Familien und überprüfbare quantitative Auswertungen.

## Schnellstart

Python 3.11 oder neuer. Die quantitative Neuberechnung benötigt nur die Standardbibliothek:

```sh
python3 scripts/reproduce.py
```

Für Abbildungen und alle Tests:

```sh
python3 -m venv .venv
. .venv/bin/activate
python -m pip install -r requirements.txt
python figures/figure_1/build_sankey.py
python figures/figure_2/build_figure.py
python -m unittest discover -s tests -v
```

Zusätzlich muss `pdftoppm` aus Poppler auf dem Suchpfad liegen (macOS: `brew install poppler`; Debian/Ubuntu: Paket `poppler-utils`). Die Auswertung und das Zeichnen benötigen keine API und keine Netzwerkverbindung. Die Erstinstallation der Abhängigkeiten benötigt gegebenenfalls Netzwerkzugang. Die Tests prüfen Rechenergebnisse, Fallzahlen, Zuordnungen, Flussbilanzen und zentrale PDF-Eigenschaften. Sie ersetzen keine unabhängige qualitative Kodierung.

## Orientierung

- `figures/figure_1/`: Auswahlwege; PDF/SVG/PNG, Quellskript, Metadaten und Lesetext, 120 × 178 mm.
- `figures/figure_2/`: Synthese zur Autorschaft; dieselben Formate, 120 × 160 mm.
- `data/`: fallbezogene Wortzählungen, Quellenverzeichnis, historische Kategorien und Familien, Referenzaggregate.
- `scripts/`: reproduzierbare Auswertung und Berechnung relativer Häufigkeiten.
- `results/`: neu berechnete Ergebnisse.
- `tests/`: automatisierte Konsistenzprüfungen.
- `docs/Fussnoten.md`: einsetzbare KI- und Repository-Fußnoten.
- `docs/KI_und_Pruefumfang.md`: Nachweisstand und persönliche Kontrolle.
- `docs/Daten_und_Grenzen.md`: Datenwörterbuch und Grenzen der Reproduzierbarkeit.
- `VALIDIERUNG.md`: tatsächlich durchgeführte lokale Prüfungen.

Die 49 deutschen Artikelkörper ergeben 12.925 bzw. 30.923 Tokens in den beiden Portalen. Die zwölf chinesischen Familien umfassen 32 Texte; bei BookTok sind 22 von 23 deutschen A-Fällen und alle elf englischen A-Fälle einer Hauptfamilie zugeordnet. Die Familienzahlen der Arenen sind kein Maß ihrer relativen Diskursvielfalt.

## Veröffentlichung und Nachnutzung

Für den Upload einen leeren GitHub-Bestand verwenden und diesen Ordner übernehmen; keine übergeordneten Projektordner oder privaten Archive hochladen. `docs/Fussnoten.md` nach dem Upload um URL und Commit/Tag ergänzen. Ein GitHub-Konto, Remote oder DOI wurde nicht angelegt. Für einen stabilen Nachweis empfiehlt sich ein Release zur eingereichten Manuskriptfassung.

Daten, Dokumentation, Lesetexte und Abbildungen stehen unter CC BY 4.0, die Python-Skripte und Tests unter der MIT License. Details: `LICENSE` und `RIGHTS.md`. Die Schrift Bitstream Vera folgt FONT_LICENSE.txt. Fremde Artikelvolltexte sind nicht enthalten; deren Rechte bleiben bei den Rechteinhabern.

Zitation: siehe `CITATION.cff`. Autor: Christoph auf der Horst, Arbeitsstelle Entwicklung moderner Fremdsprachenmethodik und -didaktik, insbesondere Fremdsprachen, Heinrich-Heine-Universität Düsseldorf.
