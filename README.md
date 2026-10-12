# Planty Home Assistant Integration

Dieses Repository enthält eine Home-Assistant-Integration für die selbst gehostete Garten-PWA Planty. Ziel ist, ausgewählte Planty-Daten und Aufgaben in Home Assistant verfügbar zu machen.

Die Integration ruft den für das konfigurierte Planty-Konto freigegebenen Snapshot ab. Sie stellt Konto-Kennzahlen für Gärten, Pflanzorte, aktive Pflanzen, offene, heute fällige und überfällige Aufgaben sowie die nächste Aufgabe bereit. Zusätzlich wird für jeden Garten, Pflanzort, jede Pflanze und jede Pflegeaufgabe ein eigener Sensor angelegt. Die Detail-Sensoren enthalten verfügbare Angaben wie Beschreibung und Zugriffsrolle, Standortbedingungen, Sorte und Wachstumsphase, Pflanz- und Aussaatdaten, Aufgabenstatus, Wiederholung, Düngemittel und verknüpfte Pflanze oder Pflanzort. Die Einrichtung prüft Serveradresse und Read-only-Token.

Die Sensoren werden in Home Assistant mit deutschen oder englischen, übersetzten Namen angezeigt. Garten- und Pflanzennamen sind Bestandteil der Geräte- beziehungsweise Sensorbezeichnung; Details stehen zusätzlich als Attribute zur Verfügung. Der Sensor **Nächste Aufgabe** ergänzt den Pflanzennamen direkt im Zustand. Auf einzelnen Aufgaben- und Aufgabenübersichtssensoren stehen `plant`, `plant_id` und – sofern die Pflanzenentität in Home Assistant registriert ist – `plant_entity_id` bereit. So kann die zugehörige Pflanzenentität in Dashboards und Automationen referenziert werden. Änderungen an Planty-Datensätzen werden spätestens mit dem nächsten Abruf (alle 15 Minuten) übernommen.

## Installation über HACS

Füge in HACS über das Drei-Punkte-Menü **Benutzerdefinierte Repositories** dieses Repository als Typ **Integration** hinzu:

`https://github.com/Clauszeit/planty-ha-integration`

Suche danach in HACS nach **Planty**, lade die Integration herunter und starte Home Assistant neu. Öffne anschließend **Einstellungen → Geräte & Dienste → Integration hinzufügen**, suche nach **Planty** und gib die Planty-Serveradresse ohne Pfad sowie ein Read-only-Token ein. Das Repository muss für HACS öffentlich erreichbar sein.

Erstelle das Token zuvor in Planty unter **Einstellungen → Home Assistant**. Es wird dort nur einmal angezeigt und kann jederzeit widerrufen werden.

## Manuelle Installation

Die Integration liegt unter `custom_components/planty/`. Kopiere diesen Ordner in das `custom_components`-Verzeichnis deiner Home-Assistant-Konfiguration und starte Home Assistant neu. Füge Planty anschließend unter **Einstellungen → Geräte & Dienste** hinzu.

Verwende eine HTTPS-Adresse oder ein vertrauenswürdiges, isoliertes internes Netz. Das Token gewährt ausschließlich lesenden Zugriff auf `/api/auth/me` und `/api/snapshot`; Planty filtert den Snapshot weiterhin nach Eigentum und Freigaben des zugehörigen Kontos. Home Assistant fragt alle 15 Minuten nach einem neuen Snapshot.

Installiere für den lokalen Testlauf zunächst `coverage` mit `python -m pip install coverage`. Danach führt `bash scripts/test.sh` die Integrationstests aus und erzeugt `coverage/sonar-coverage.xml`. Der GitHub-Actions-Workflow führt diesen Schritt bei Pushes auf `main` und Pull Requests gegen `main` vor der SonarQube-Analyse aus. Hinterlege dafür die Repository-Secrets `SONAR_TOKEN` und `SONAR_HOST_URL`. Bei SonarQube Cloud kann `SONAR_HOST_URL` auf die Cloud-Instanz-URL gesetzt werden.

## Projektdateien

- `VERSION` ist die maßgebliche Projektversion.
- `CHANGELOG.md` dokumentiert Änderungen je Version.
- `AGENTS.md` enthält die verbindlichen Beitrags- und Sicherheitsregeln.

## Lizenz

Planty Home Assistant Integration steht unter der GNU Affero General Public License v3.0 (AGPL-3.0-only). Den vollständigen Lizenztext findest du in [`LICENSE`](LICENSE). Die AGPL erlaubt auch kommerzielle Nutzung und enthält zusätzliche Quellcode-Angebotspflichten für geänderte Software, mit der Nutzer über ein Netzwerk interagieren.
