# Planty Home Assistant Integration

Dieses Repository enthält eine Home-Assistant-Integration für die selbst gehostete Garten-PWA Planty. Ziel ist, ausgewählte Planty-Daten und Aufgaben in Home Assistant verfügbar zu machen.

Die Integration wird schrittweise aufgebaut. Verbindliche API-Endpunkte, Authentifizierung, unterstützte Entitäten und Konfigurationsoptionen werden vor ihrer Implementierung anhand des Planty-API-Vertrags festgelegt und hier dokumentiert.

## Entwicklung

Die Integration wird als benutzerdefinierte Home-Assistant-Integration unter `custom_components/planty/` bereitgestellt. Lokale Zugangsdaten, Home-Assistant-Speicherdateien und Entwicklungsartefakte gehören nicht ins Repository.

## Projektdateien

- `VERSION` ist die maßgebliche Projektversion.
- `CHANGELOG.md` dokumentiert Änderungen je Version.
- `AGENTS.md` enthält die verbindlichen Beitrags- und Sicherheitsregeln.
