# Planty Home Assistant Integration

Dieses Repository enthält eine Home-Assistant-Integration für die selbst gehostete Garten-PWA Planty. Ziel ist, ausgewählte Planty-Daten und Aufgaben in Home Assistant verfügbar zu machen.

Die Integration ruft den für das konfigurierte Planty-Konto freigegebenen Snapshot ab und stellt Sensoren für Gärten, aktive Pflanzen, offene Aufgaben, überfällige Aufgaben und den nächsten Aufgabentermin bereit. Die Einrichtung prüft Serveradresse und Read-only-Token.

## Entwicklung

Die Integration wird als benutzerdefinierte Home-Assistant-Integration unter `custom_components/planty/` bereitgestellt. Installiere den Ordner `custom_components/planty` in dein Home-Assistant-Konfigurationsverzeichnis und starte Home Assistant neu. Erstelle in Planty unter **Einstellungen → Home Assistant** ein Read-only-Token und füge in Home Assistant die Planty-Serveradresse ohne Pfad sowie das Token hinzu. Das Token wird in Planty nur einmal angezeigt und kann dort jederzeit widerrufen werden.

Verwende eine HTTPS-Adresse oder ein vertrauenswürdiges, isoliertes internes Netz. Das Token gewährt ausschließlich lesenden Zugriff auf `/api/auth/me` und `/api/snapshot`; Planty filtert den Snapshot weiterhin nach Eigentum und Freigaben des zugehörigen Kontos. Home Assistant fragt alle 15 Minuten nach einem neuen Snapshot.

Installiere für den lokalen Testlauf zunächst `coverage` mit `python -m pip install coverage`. Danach führt `bash scripts/test.sh` die Integrationstests aus und erzeugt `coverage/sonar-coverage.xml`. Der GitHub-Actions-Workflow führt diesen Schritt bei Pushes auf `main` und Pull Requests gegen `main` vor der SonarQube-Analyse aus. Hinterlege dafür die Repository-Secrets `SONAR_TOKEN` und `SONAR_HOST_URL`. Bei SonarQube Cloud kann `SONAR_HOST_URL` auf die Cloud-Instanz-URL gesetzt werden.

## Projektdateien

- `VERSION` ist die maßgebliche Projektversion.
- `CHANGELOG.md` dokumentiert Änderungen je Version.
- `AGENTS.md` enthält die verbindlichen Beitrags- und Sicherheitsregeln.
