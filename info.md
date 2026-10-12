# Planty

Planty is a Home Assistant integration for the self-hosted Planty gardening app. It provides account summaries and named sensors for each accessible garden, growing place, plant, and care task. Task sensors include the related plant name and, when available, its Home Assistant entity ID.

## Quick setup

1. In Planty, create a **Read-only-Token** under **Settings → Home Assistant**.
2. In HACS, add `https://github.com/Clauszeit/planty-ha-integration` as a custom **Integration** repository, install **Planty**, then restart Home Assistant.
3. Add **Planty** under **Settings → Devices & services → Add integration**.
4. Enter the Planty origin reachable from Home Assistant (for example `https://planty.example.org`) and the token. Do not append `/api` or another path.
5. Select the generated sensors in dashboards or automations. Data refreshes every 15 minutes.

The configured address must route `/api/auth/me` and `/api/snapshot` to Planty's API. With the standard Docker setup, use the public or local reverse-proxy address; API port `8000` is internal and not published by default. See the [README setup guide](https://github.com/Clauszeit/planty-ha-integration#voraussetzungen-und-verbindung) for port examples, every sensor and attribute, dashboard and automation examples, security notes, and troubleshooting.
