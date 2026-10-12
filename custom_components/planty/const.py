"""Constants for the Planty integration."""

from datetime import timedelta

from homeassistant.const import Platform

DOMAIN = "planty"
CONF_URL = "url"
CONF_TOKEN = "token"
PLATFORMS = (Platform.SENSOR,)
DEFAULT_SCAN_INTERVAL = timedelta(minutes=15)
REQUEST_TIMEOUT_SECONDS = 10
API_SNAPSHOT_PATH = "/api/snapshot"
API_PROFILE_PATH = "/api/auth/me"
REQUIRED_SNAPSHOT_KEYS = ("gardens", "places", "plants", "tasks")
TASK_OPEN_STATUS = "open"
PLANT_COMPLETED_PHASE = "completed"
PLACE_KIND_OPTIONS = ("beet", "topf", "kuebel", "balkonkasten", "einzelpflanze", "sonstiges")
PLACE_KIND_VALUES = {
    "Beet": "beet",
    "Topf": "topf",
    "Kübel": "kuebel",
    "Balkonkasten": "balkonkasten",
    "Einzelpflanze": "einzelpflanze",
    "Sonstiges": "sonstiges",
}
