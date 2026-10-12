# Changelog

## 0.7.0 – 2026-10-12

- Das Aktualisierungsintervall des Planty-Snapshots lässt sich in den Optionen der Integration zwischen 1 Minute und 24 Stunden einstellen. Standard sind 15 Minuten.

## Unreleased

- Ergänzt den GitHub-Actions-Workflow für Tests, Coverage-Bericht und SonarQube-Analyse.

## 0.6.1 – 2026-10-12

- Gemeinsame Aufgaben behalten Sortenkennungen auch bei vorübergehend fehlenden Pflanzen im Snapshot; zusätzliche Tests sichern die Dashboard-Attribute ab.

## 0.6.0 – 2026-10-12

- Pflanzensensoren und Pflanzortlisten geben `variety_group_id` und `variety_group_size` aus dem Planty-Snapshot weiter. Dashboard-Karten können Sorten damit gemeinsam anzeigen.
- Gemeinsame Aufgaben zeigen `plant_ids`, Sorten und verfügbare Pflanzen-Entitäts-IDs in `plants`. Der Name der nächsten Aufgabe nennt die Sortenanzahl.

## 0.5.0 – 2026-10-12

- Zeigt die Pflanze bei der nächsten Aufgabe direkt an und stellt deren Home-Assistant-Entität für Dashboards und Automationen bereit.

## 0.4.1 – 2026-10-12

- Behebt die Home-Assistant-Metadatenvalidierung und verwendet gültige, übersetzbare Pflanzort-Typen.

## 0.4.0 – 2026-10-12

- Ergänzt übersetzte und eindeutige Sensoren mit Detaildaten je Garten, Pflanzort, Pflanze und Pflegeaufgabe.
- Ergänzt Kennzahlen zu Pflanzorten und heute fälligen Aufgaben sowie Kontextattribute zu Phasen, Standorten und Aufgaben.
- Verwendet die von Home Assistant unterstützten Übersetzungsdateien für benutzerdefinierte Integrationen.

## 0.3.0 – 2026-10-12

- Ergänzt HACS-Metadaten, Branding, Validierung und Installationshinweise für benutzerdefinierte Repositories.

## 0.2.0 – 2026-10-12

- Ergänzt Einrichtung, API-Client, Snapshot-Koordination und Sensoren für Gärten und Pflegeaufgaben.

## 0.1.0 – 2026-10-12

- Legt die Repository-Grundlagen für die Planty-Home-Assistant-Integration an.
