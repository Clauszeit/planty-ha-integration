# Planty Home Assistant Integration

Diese Integration verbindet Home Assistant mit der selbst gehosteten Garten-App [Planty](https://github.com/Clauszeit/planty). Sie liest Gärten, Pflanzorte, Pflanzen und Pflegeaufgaben aus Planty und stellt sie als Home-Assistant-Sensoren bereit. Die Einrichtung erfolgt über die Home-Assistant-Oberfläche; YAML-Konfiguration ist nicht erforderlich.

> **Schnellstart:** In Planty unter **Einstellungen → Home Assistant** ein schreibgeschütztes Token erstellen. In Home Assistant die Integration **Planty** hinzufügen. Als URL den Planty-Ursprung eintragen, zum Beispiel `https://planty.example.org` – ohne `/api` und ohne weiteren Pfad. Anschließend die gewünschten Sensoren über den Entitätsauswahldialog einem Dashboard oder einer Automation hinzufügen.

## Inhalt

- [Voraussetzungen und Verbindung](#voraussetzungen-und-verbindung)
- [Installation mit HACS](#installation-mit-hacs)
- [Einrichtung](#einrichtung)
- [Sensoren und verfügbare Daten](#sensoren-und-verfügbare-daten)
- [Sensoren im Dashboard verwenden](#sensoren-im-dashboard-verwenden)
- [Pflanzen mit Aufgaben verknüpfen](#pflanzen-mit-aufgaben-verknüpfen)
- [Automationen erstellen](#automationen-erstellen)
- [Fehler beheben](#fehler-beheben)
- [Manuelle Installation](#manuelle-installation)
- [Entwicklung und Lizenz](#entwicklung-und-lizenz)

## Voraussetzungen und Verbindung

- Eine erreichbare Planty-Installation mit einem unter **Einstellungen → Home Assistant** erstellten Integrationstoken.
- Home Assistant muss den Planty-Server über HTTP oder HTTPS erreichen können. HTTPS wird empfohlen.
- Für die URL muss Plantys API unter den Pfaden `/api/auth/me` und `/api/snapshot` erreichbar sein. Die Integration fragt die API ab, nicht die HTML-Oberfläche.

Bei der üblichen Planty-Bereitstellung wird die API hinter derselben öffentlichen Adresse wie die Web-Oberfläche bereitgestellt. Trage dann genau diese Adresse ein, etwa `https://planty.example.org`. Der Reverse Proxy beziehungsweise Webserver leitet die `/api/`-Anfragen intern an den API-Dienst weiter. Die Integration verbindet sich dadurch zwar mit derselben Adresse wie die Web-Oberfläche, liest aber ausschließlich die API-Endpunkte.

In der mitgelieferten Docker-Konfiguration lauscht die API intern auf Port `8000`; dieser Port wird nicht nach außen veröffentlicht. Plantys Webserver ist standardmäßig intern auf Port `8080` erreichbar und leitet API-Aufrufe weiter. Der veröffentlichte Webserver-Port ist standardmäßig `8080`, bindet aber zunächst nur an `127.0.0.1`. Von einem anderen Gerät oder einem getrennten Home-Assistant-Container ist er daher nicht automatisch erreichbar. Nutze normalerweise den HTTPS-Hostnamen deines Reverse Proxys. Alternativ muss der Webserver-Port bewusst für Home Assistant erreichbar gemacht werden. Verwende den API-Port `8000` nur dann, wenn du ihn selbst erreichbar gemacht hast und dessen Zugriff absicherst.

Die URL muss ein Ursprung ohne Pfad sein:

| Erreichbarkeit von Home Assistant | URL in der Einrichtung |
| --- | --- |
| Öffentlicher oder interner Reverse Proxy mit HTTPS | `https://planty.example.org` |
| Planty-Webserver im lokalen Netz, wenn du die Bind-Adresse entsprechend freigegeben hast | `http://192.168.1.20:8080` |
| API direkt erreichbar und Port explizit freigegeben | `http://192.168.1.20:8000` |

Die IP-Adresse und der Port sind Beispiele. Keine Pfade wie `/api`, `/login` oder `/settings` und keinen abschließenden Slash ergänzen. Wenn Planty in einem Unterpfad veröffentlicht wird, muss der Proxy die API unter dem eigenen Ursprung bereitstellen, da diese Integration keine Unterpfade unterstützt.

Das Token ist auf lesenden Zugriff beschränkt. Es kann nur das Profil des Tokenkontos und dessen für dieses Konto sichtbaren Planty-Snapshot lesen. Plantys Eigentums- und Freigaberegeln gelten weiterhin. Home Assistant speichert das Token als Konfiguration des Eintrags. Lege es nicht in Dashboards, Automationen, Screenshots oder öffentliche Dateien. Bei Verdacht auf Offenlegung kannst du es in Planty widerrufen und in Home Assistant durch ein neues ersetzen.

## Installation mit HACS

1. Öffne HACS in Home Assistant.
2. Öffne das Drei-Punkte-Menü und wähle **Benutzerdefinierte Repositories**.
3. Füge `https://github.com/Clauszeit/planty-ha-integration` als Repository-Typ **Integration** hinzu.
4. Suche in HACS nach **Planty** und installiere die Integration.
5. Starte Home Assistant neu.
6. Fahre mit [Einrichtung](#einrichtung) fort.

Das Repository muss für HACS öffentlich erreichbar sein. Nach späteren Updates installierst du die neue Version in HACS und startest Home Assistant neu, falls HACS dazu auffordert. Die offizielle Anleitung steht in der [HACS-Dokumentation zur Repository-Installation](https://www.hacs.xyz/docs/faq/custom_repositories/).

## Einrichtung

### 1. Read-only-Token in Planty erstellen

Öffne Planty, gehe zu **Einstellungen → Home Assistant** und erstelle ein Integrationstoken. Kopiere es direkt, denn Planty zeigt den vollständigen Tokenwert nur bei der Erstellung. Für Home Assistant empfiehlt sich ein eigenes Token, das du bei Bedarf separat widerrufen kannst.

### 2. Integration in Home Assistant hinzufügen

1. Öffne **Einstellungen → Geräte & Dienste**.
2. Wähle **Integration hinzufügen** und suche nach **Planty**.
3. Gib die von Home Assistant erreichbare Planty-Serveradresse als Ursprung ein, beispielsweise `https://planty.example.org`.
4. Füge das Read-only-Token ein und bestätige.

Die Einrichtung prüft die Adresse und das Token sofort. Bei Erfolg erscheint ein Planty-Konto als Gerät. Gärten werden als eigene Geräte angelegt; ihre Pflanzorte, Pflanzen und Aufgaben sind diesem Gartengerät zugeordnet. Die Sensoren werden automatisch entdeckt, wenn neue Planty-Datensätze in einem zugänglichen Garten auftauchen. Archivierte oder nicht mehr freigegebene Datensätze werden nicht als verfügbar gemeldet.

### 3. Entitäten finden

Öffne **Einstellungen → Geräte & Dienste → Planty → Entitäten** oder öffne das gewünschte Gerät. Alternativ findest du sie unter **Entwicklerwerkzeuge → Zustände**. Nutze in Dashboards und Automationen den Entitätsauswahldialog, um die tatsächlich von Home Assistant vergebenen Entity-IDs auszuwählen. Entity-IDs können nach einer Umbenennung oder bei bereits vorhandenen Entitäten von den Beispielen abweichen.

## Sensoren und verfügbare Daten

Die Kontoübersicht liegt am Planty-Kontogerät. Für jeden zugänglichen Garten gibt es ein Gartengerät mit den darunter gruppierten Detail-Sensoren. Die Übersetzungen werden abhängig von der Home-Assistant-Sprache angezeigt; Sensorwerte für Pflanzorttyp und Pflanzenphase sind ebenfalls übersetzt.

| Sensor | Zustand | Zusätzliche Attribute |
| --- | --- | --- |
| **Gärten** | Anzahl aktiver Gärten | – |
| **Pflanzorte** | Anzahl aktiver Pflanzorte | – |
| **Aktive Pflanzen** | Anzahl aktiver Pflanzen | `plants_by_phase`: Anzahl nach Wachstumsphase |
| **Offene Aufgaben** | Anzahl offener Aufgaben | `due_today`, `overdue`: Teilmengen der offenen Aufgaben |
| **Heute fällige Aufgaben** | Anzahl heute fälliger Aufgaben | – |
| **Überfällige Aufgaben** | Anzahl überfälliger Aufgaben | `overdue_tasks`: bis zu zehn Aufgaben mit Titel, Fälligkeit und Pflanzen-/Gartenbezug |
| **Nächste Aufgabe** | Titel der nächsten Aufgabe, bei Pflanzenaufgaben ergänzt um den Pflanzennamen | Aufgabendetails und mögliche Verknüpfung zur Pflanzenentität |
| **Nächste Aufgabe fällig** | Fälligkeitsdatum der nächsten Aufgabe | Aufgabendetails und mögliche Verknüpfung zur Pflanzenentität |

Zusätzlich gibt es je Datensatz einen Detail-Sensor:

| Datensatz | Zustand | Attribute (sofern in Planty gepflegt) |
| --- | --- | --- |
| Garten | Gartenname | `description`, `access`, `owner_username`, `plan_width_m`, `place_count`, `active_plant_count`, `open_task_count`, `due_today_task_count`, `overdue_task_count`, `next_task`, `next_task_due` |
| Pflanzort | Typ, etwa Beet, Topf oder Kübel | `kind`, `location`, `light`, `area`, `soil`, `notes`, `garden`, `plants` mit Name, Sorte, Menge, Phase und Gruppenkennung |
| Pflanze | Wachstumsphase | `name`, `variety`, `variety_group_id`, `variety_group_size`, `scientific_name`, `quantity`, `phase`, `season`, `season_year`, `permanent`, `winter_at_location`, `start_date`, `purchased_date`, `seed_date`, `start_comment`, `source`, `notes`, `garden`, `place`, `planned_place`, bis zu fünf `recent_actions` |
| Aufgabe | Fälligkeitsdatum | `task_id`, `title`, `kind`, `status`, `time`, `repeat_days`, `repeat_end`, `last_done`, `fertilizer_product`, `dosage`, `notes`, `due_date`, `garden`, `plant`, `place`, `plant_id`, `plant_entity_id`; bei gemeinsamen Aufgaben auch `plant_ids`, `plants`, `variety_group_id` |

Attribute, die Planty nicht geliefert oder nicht gepflegt hat, können fehlen. Datumszustände sind Home-Assistant-Datumswerte. Pflanzenphasen erscheinen als übersetzter Zustand (zum Beispiel **Gepflanzt**); Pflanzorttypen ebenfalls (zum Beispiel **Beet**). In Vorlagen und Automationen solltest du bevorzugt Attribute wie `plant`, `place` und `garden` verwenden statt interne Datenbank-IDs. `plant_id` und `task_id` sind vor allem für stabile Verknüpfungen nützlich.

Ab Planty 0.46.0 tragen zusammengehörige Sorten dieselbe `variety_group_id` und `variety_group_size` als Sensorattribute. Die Kennung beschreibt die aktuelle Gruppierung nach Garten, Pflanzenname und Abschlussstatus; beim Umbenennen oder Abschließen kann sie wechseln. Eine gemeinsame Aufgabe enthält `plant_ids` und `plants` mit Sorte und, sofern registriert, `entity_id` je Pflanze. Ältere Planty-Versionen liefern diese zusätzlichen Attribute noch nicht.

Die Integration aktualisiert den gemeinsamen Planty-Snapshot alle **15 Minuten**. Änderungen an Namen, Aufgaben und Attributen werden daher spätestens beim nächsten erfolgreichen Abruf in Home Assistant sichtbar.

## Sensoren im Dashboard verwenden

Am einfachsten geht es ohne YAML:

1. Öffne ein Dashboard und wähle **Karte hinzufügen → Entitäten**.
2. Suche im Entitätsauswahldialog nach **Planty** oder dem gewünschten Garten-/Pflanzennamen.
3. Füge zum Beispiel **Nächste Aufgabe**, **Nächste Aufgabe fällig**, **Überfällige Aufgaben** und einzelne Pflanzensensoren hinzu.

Für eine Markdown-Karte kannst du den Entity-ID-Platzhalter durch den Sensor ersetzen, den du im Entitätsauswahldialog ausgewählt hast:

```yaml
type: markdown
content: >-
  **Nächste Aufgabe:** {{ states('sensor.HIER_ENTITY_ID_EINSETZEN') }}
  **Pflanze:** {{ state_attr('sensor.HIER_ENTITY_ID_EINSETZEN', 'plant') or 'Keine Pflanzenverknüpfung' }}
```

Ersetze beide Vorkommen des Platzhalters durch dieselbe tatsächliche Entity-ID des Sensors **Nächste Aufgabe**. Im visuellen Editor kannst du alternativ einen Markdown-Text mit Template-Unterstützung anlegen und den Zustand des Sensors auswählen.

## Pflanzen mit Aufgaben verknüpfen

Jeder Aufgabensensor zeigt bei zugeordneten Aufgaben `plant` mit dem Pflanzennamen und `plant_id` mit der Planty-ID. Wenn Home Assistant den zugehörigen Pflanzensensor bereits registriert hat, enthält das Attribut `plant_entity_id` zusätzlich dessen tatsächliche Entity-ID, zum Beispiel `sensor.planty_pflanze_tomate`. Diese Verknüpfung lässt sich in Templates auslesen:

```jinja
{{ state_attr('sensor.HIER_ENTITY_ID_DER_AUFGABE', 'plant_entity_id') }}
```

Die Pflanzenentität kann noch fehlen, wenn der Datensatz gerade neu angelegt wurde oder der Pflanzensensor nicht verfügbar ist. In diesem Fall bleibt `plant_entity_id` leer; der Pflanzenname und – falls vorhanden – `plant_id` werden weiterhin am Task bereitgestellt. Für eine Dashboard-Karte kannst du Aufgaben- und Pflanzensensor gemeinsam in einer Entities-Karte anzeigen. Wähle beide Entitäten im Dialog aus, damit Home Assistant die passenden IDs einsetzt.

## Automationen erstellen

Ein einfacher Start ist eine Automation, die reagiert, sobald mindestens eine Aufgabe überfällig ist. Wähle den **Überfällige Aufgaben**-Sensor über den Entitätsauswahldialog und passe den Benachrichtigungsdienst an deine Installation an:

```yaml
alias: Planty – überfällige Aufgaben melden
triggers:
  - trigger: numeric_state
    entity_id: sensor.HIER_ENTITY_ID_UEBERFAELLIGE_AUFGABEN
    above: 0
actions:
  - action: notify.notify
    data:
      title: Planty
      message: >-
        {{ states('sensor.HIER_ENTITY_ID_UEBERFAELLIGE_AUFGABEN') }} Aufgabe(n) sind überfällig.
        {% set tasks = state_attr('sensor.HIER_ENTITY_ID_UEBERFAELLIGE_AUFGABEN', 'overdue_tasks') or [] %}
        {% for task in tasks %}
        {{ task.title }}{% if task.plant is defined %} – {{ task.plant }}{% endif %}{% if task.due_date is defined %} (fällig {{ task.due_date }}){% endif %}{% if not loop.last %}; {% endif %}
        {% endfor %}
mode: single
```

Ersetze den Platzhalter in `entity_id` und im Template jeweils durch die Entity-ID des Sensors **Überfällige Aufgaben**. `notify.notify` ist der allgemeine Benachrichtigungsdienst; wenn deine Installation einen konkreten Dienst wie `notify.mobile_app_...` nutzt, wähle diesen im Automationseditor aus. Der Sensor zählt überfällige Aufgaben; die Attributliste enthält höchstens zehn Aufgaben. Mehr zu Triggern und YAML-Automationen steht in der [Home-Assistant-Dokumentation](https://www.home-assistant.io/docs/automation/yaml/).

Der numerische Trigger reagiert auf den Wechsel von `0` auf einen Wert größer `0`. Wenn der Sensor bereits beim Anlegen der Automation überfällige Aufgaben zählt, wird nicht sofort eine Benachrichtigung ausgelöst. In diesem Fall kannst du die Automation manuell ausführen oder einen zusätzlichen zeitgesteuerten Trigger ergänzen.

## Fehler beheben

| Anzeige oder Problem | Prüfung |
| --- | --- |
| **Server nicht erreichbar** | URL aus Sicht von Home Assistant prüfen. Hostname, HTTPS-Zertifikat und Port müssen erreichbar sein. Für die Standard-Docker-Bereitstellung ist `8000` ein interner API-Port; der Webserver-Port `8080` oder der vorgeschaltete HTTPS-Port ist normalerweise der richtige Zugang. |
| **Token ungültig oder widerrufen** | In Planty unter **Einstellungen → Home Assistant** prüfen, ob das Token noch aktiv ist. Ein neues Token erstellen und den Planty-Eintrag in Home Assistant neu authentifizieren. |
| **Unerwartete Antwort** | Prüfen, ob die URL auf Planty zeigt und der Proxy `/api/auth/me` und `/api/snapshot` an den API-Dienst weiterleitet. Nicht `/api` an die URL anhängen. |
| **Garten oder Datensensor fehlt** | In Planty mit demselben Konto anmelden und prüfen, ob der Garten zugänglich und nicht archiviert ist. Freigegebene Gärten erscheinen nur entsprechend den Planty-Berechtigungen. |
| **Änderung ist noch nicht sichtbar** | Bis zum nächsten Abruf warten (höchstens 15 Minuten) oder unter **Einstellungen → Geräte & Dienste → Planty** die Integration neu laden. |
| **Sensor nicht verfügbar** | Planty-API-Erreichbarkeit, Freigabe und Archivstatus prüfen. Nach einem Abruffehler kann die Integration die zuletzt empfangenen Daten behalten, meldet betroffene Detail-Sensoren aber als nicht verfügbar. |

Home-Assistant-Logs findest du unter **Einstellungen → System → Protokolle**. Suche dort nach `planty` und den Namen der betreffenden Entität oder Integration.

## Manuelle Installation

1. Lade dieses Repository herunter.
2. Kopiere `custom_components/planty/` in `<HA-Konfigurationsordner>/custom_components/planty/`.
3. Starte Home Assistant neu.
4. Füge **Planty** unter **Einstellungen → Geräte & Dienste → Integration hinzufügen** hinzu und folge der [Einrichtung](#einrichtung).

## Entwicklung und Lizenz

`VERSION` ist die maßgebliche Projektversion; Änderungen stehen in [`CHANGELOG.md`](CHANGELOG.md). Die Integrations-Tests laufen lokal nach Installation von `coverage` mit `bash scripts/test.sh`. Der GitHub-Actions-Workflow testet Änderungen und führt anschließend die SonarQube-Analyse aus; dafür sind die Repository-Secrets `SONAR_TOKEN` und `SONAR_HOST_URL` erforderlich.

Planty Home Assistant Integration steht unter der GNU Affero General Public License v3.0 (**AGPL-3.0-only**). Den vollständigen Text enthält [`LICENSE`](LICENSE). Die Lizenz erlaubt kommerzielle Nutzung und enthält zusätzliche Quellcode-Angebotspflichten für geänderte Software, mit der Nutzer über ein Netzwerk interagieren.
