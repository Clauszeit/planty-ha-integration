# Hinweise für Beiträge und Coding-Agenten

## Projektziel

Dieses Repository enthält eine Home-Assistant-Integration für Planty. Sie bindet ausschließlich dokumentierte Planty-API-Verträge an und stellt Garteninformationen und Aufgaben kontrolliert in Home Assistant bereit.

## Verbindliche Leitlinien

- Externe Garten-, Wetter- oder Pflanzenwissensquellen dürfen erst nach Prüfung von Abdeckung, Zugang, Limits und Nutzungsbedingungen angebunden werden. Keine Scraping-Laufzeitabhängigkeit und keine ungeprüften Drittanbieter-Endpunkte.
- Empfehlungen zu Aussaat, Pflanzung, Düngung oder Frostschutz müssen Herkunft, Zeitraum und Unsicherheit erkennen lassen. Keine standortunabhängigen Empfehlungen als garantiert darstellen.
- Erzeuge Erinnerungen für geplante und wiederkehrende Pflegeaufgaben. Dedupliziere unveränderte Erinnerungen und erhalte eine nachvollziehbare Erledigungs- und Änderungshistorie.
- Eine belastbare, deterministische Terminberechnung muss ohne LLM funktionieren. llama.cpp kann optional lokal für das Zusammenfassen eigener Gartennotizen oder geprüfter Quellen verwendet werden. Übermittle keine personenbezogenen Daten an ein Modell.
- Jeder Nutzer darf eigene oder ausdrücklich freigegebene Gärten und deren Inhalte gemäß seiner Rolle lesen und ändern. Nur der Gartenbesitzer verwaltet Freigaben und endgültiges Löschen; andere private Gärten bleiben unzugänglich.
- Secrets, private Konfiguration, Push-Schlüssel und Nutzerdaten dürfen nicht eingecheckt werden.
- Halte Dokumentation, Beispielkonfiguration und Changelog bei fachlichen Änderungen aktuell.
- Erhöhe bei entsprechenden Änderungen die zentrale Version in `VERSION` und aktualisiere sichtbare Versionsangaben sowie den Changelog. Vor `1.0.0` erhöhen neue Funktionen die mittlere Stelle (`0.x.0`), Fehlerkorrekturen die letzte Stelle (`0.0.x`); inkompatible Änderungen erfordern eine bewusste Versionsentscheidung. Git-Release-Tags müssen der `VERSION` entsprechen und `vX.Y.Z` verwenden.
- Prüfe vor und nach Änderungen SonarQube-Issues und Coverage-Anforderungen. Verwende wiederkehrende Befunde vorbeugend: wiederholte Literale als benannte Konstanten definieren, verschachtelte bedingte Ausdrücke in klare `if`/`elif`-Anweisungen auflösen und in Exception-Tests Argumente sowie Testdaten vor `assertRaises` vorbereiten.
- Führe SonarQube-Prüfungen ausdrücklich über die angebundenen SonarQube-MCP-Tools aus: vor Änderungen Quality Gate, offene Issues und Coverage abfragen; nach Änderungen erneut abfragen und geänderte Quell- und Testdateien bei Bedarf analysieren. Verlasse dich nicht allein auf CI, CLI-Scans oder lokale Coverage-Berichte. Falls das MCP keine Analyse des unveröffentlichten Arbeitsstands ermöglicht, kennzeichne Serverwerte als Stand der letzten Serveranalyse.
- Jede neue Funktion erhält Funktionstests und Regressionstests. Führe alle verfügbaren Tests lokal vor jedem Commit aus.
- `scripts/test.sh` ist der CI-Einstiegspunkt und erzeugt `coverage/sonar-coverage.xml`.

## Architekturgrenzen

- `custom_components/planty/`: Home-Assistant-Integration, Konfigurationsablauf, API-Adapter und Entitäten.
- `docs/`: API-Vertrag, Architektur, Einrichtung und Betrieb.
- Planty-API-Aufrufe bleiben hinter einem klaren Adapter. Speichere Quellenzeitpunkt und Abrufzeitpunkt getrennt, wenn externe Hinweise verwendet werden. Reagiere kontrolliert auf fehlende Daten, API-Ausfälle und Rate-Limits.

## Arbeitsweise

- Lies vor Änderungen vorhandene Projektdateien und bewahre Nutzerdaten.
- Verwende vorhandene Implementierungspläne verbindlich als Anforderungsgrundlage, wenn sie für diese Integration bestehen. Gleiche Planung und Umsetzung gegen Ziele, Abnahmekriterien und Abhängigkeiten ab; aktualisiere sie, wenn Anforderungen oder Entscheidungen geändert werden.
- Jeder Commit behandelt genau ein zusammengehöriges Thema. Nimm keine fremden oder bereits bestehenden Änderungen auf. Prüfe den Staging-Inhalt vor jedem Commit.
- Verwende für Git-Änderungen bevorzugt die Git-Integration im regulären Index. Wenn sie nicht verfügbar ist, frage erforderliche Git-Shell-Befehle über `require_escalated` mit klarer Freigabefrage an. Nutze keinen alternativen temporären Index.
- Prüfe Auswirkungen projektweit auf Planty-API-Verträge, Home-Assistant-Konfiguration, Persistenz, Betrieb und Dokumentation. Aktualisiere betroffene Bereiche gemeinsam und ergänze passende Tests.
- Führe vor jedem Commit alle verfügbaren lokalen Tests aus. Wenn ein Testsystem fehlt oder nicht ausführbar ist, halte das Hindernis fest.
- Prüfe GitHub Actions niemals selbst und verwende keinen direkten `gh`-Zugriff. Prüfe SonarQube nach Änderungen und Pushes ausschließlich über die angebundenen MCP-Tools.
- Nach einem Push wiederhole SonarQube-Abfragen, bis eine neuere Branch-Analyse den Push abbildet. Stimmen MCP-SHA und gepushter SHA nicht überein oder weist MCP keinen SHA aus, benenne die Einschränkung.
- Release-Build und Container-Veröffentlichung erfolgen bei Push über GitHub Actions auf dem selbst gehosteten Runner. Verwende weder GitHub Actions Artifact Storage noch andere limitierte Cloud-Speicher für Artefakte oder Caches. Lokale Runner-Caches sind zulässig.
- Führe keine destruktiven Änderungen aus und veröffentliche oder deploye nichts ohne ausdrücklichen Auftrag.
- Berichte klar, was implementiert wurde und welche Aspekte offen oder nicht verifiziert sind.
