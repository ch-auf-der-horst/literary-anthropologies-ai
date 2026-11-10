# Datenbeschreibung und Reichweite

## Zählung

`de_document_counts.csv` enthält 49 Artikel in zwei Fassungen: `adopted` entspricht den geprüften Artikelkörpern einschließlich der beiden übernommenen Schlussbestandteile; `without_english_story` entfernt zusätzlich 1.217 Tokens der englischen Modellgeschichte in DE-160. Pro Artikel stehen Portal, zwei Ausschlussmerkmale, Tokenumfang und Vorkommen von 14 Wortformen. `mixed` und `summary` markieren ganze Artikel für die beiden Auswahl-Sensitivitäten. Dokumentstreuung wird aus Vorkommen > 0 berechnet. Es gibt keine Lemmatisierung. `tokenization.json` beschreibt die ursprüngliche Zählregel.

Die öffentlichen Zähldaten ermöglichen die Wiederberechnung der Aggregation, Normalisierung und Dokumentstreuung. Die Extraktion und Tokenisierung der Originalartikel ist ohne das private Archiv nicht vollständig reproduzierbar. `de_selection.csv` dokumentiert die 55 KI-bezogenen Kandidaten, ihre Verwendung und Quellprüfsummen; frühere automatische Prüfvermerke werden nicht übernommen. `article_sources.csv` stellt Fallkennungen und Quellen der historischen deutschen und chinesischen Kodierbestände bereit. Online-Fassungen können vom archivierten Stand abweichen.

`expected_frequencies.json` ist die unveränderte aggregierte Referenz aus dem Artikelprüfbericht für die beiden veröffentlichten Varianten. `historical_and_stress_reference.json` bewahrt historische Vergleichswerte und den zusätzlichen Metadaten-Stresstest. Dieser Stresstest ist hier nur als aggregiertes Prüfergebnis enthalten, nicht aus eigenen fallbezogenen Eingaben reproduzierbar. Die historischen Daten werden nicht als aktuelle Hauptzählung ausgegeben.

## Kategorien und Familien

`family_assignments.json` enthält historische Hauptzuordnungen der 32 chinesischen Kerntexte, 23 deutschen und elf englischen BookTok-A-Fälle. Ein deutscher A-Fall hat keine Hauptzuordnung. Die Familienzählung ist eine Neuauszählung vorhandener Zuordnungen, keine Neukodierung. Die Definitionen und Familiennamen werden als historische Arbeitskategorien dokumentiert. Insbesondere pauschale Formulierungen in historischen Kurzthesen sind keine zusätzlich validierten Aussagen über nationale Diskurse. Die deutschen 30 + 29 Einträge sind historische, überlappende Auswahlstufen, nicht notwendig 59 eindeutige Texte. Die deutschen Kategorienbeschreibungen enthalten historische Falllisten, keine neue vollständige Zuordnung aller Erweiterungstexte.

## Abbildungen

Abbildung 1 dokumentiert Auswahlwege mit getrennten Nennern (DE 245, CN 962, BT 220). Dünne Verbindungen zur Verdichtung sind nicht mengenproportional. Abbildung 2 ist eine selektive interpretative Synthese, keine vollständige Taxonomie und keine Messung von Effektstärken. Lesetexte und Bildunterschriften liegen bei. Die Zuordnung der ausgewählten Fälle zur Synthese bleibt eine interpretative Leistung; das Nachzeichnen validiert sie nicht.

## Nicht enthalten

Keine fremden Volltexte, vollständigen Captions/Transkripte, Videos, API-Schlüssel, privaten Korrespondenzen oder Manuskriptentwürfe. Die historischen API-Läufe, komplette offene Kodiertabellen und sämtliche Retrievaldaten sind nicht Bestandteil dieses Pakets. Der Inhalt ist ein nachvollziehbares Publikationssupplement für die angegebenen Analyseschritte, kein vollständiges Forschungsarchiv.
