"""Constants for the Planty integration."""

from datetime import timedelta
from typing import Any, Mapping

from homeassistant.const import Platform

DOMAIN = "planty"
CONF_URL = "url"
CONF_TOKEN = "token"
CONF_SCAN_INTERVAL = "scan_interval"
PLATFORMS = (Platform.SENSOR,)
DEFAULT_SCAN_INTERVAL_MINUTES = 15
MIN_SCAN_INTERVAL_MINUTES = 1
MAX_SCAN_INTERVAL_MINUTES = 1440
DEFAULT_SCAN_INTERVAL = timedelta(minutes=DEFAULT_SCAN_INTERVAL_MINUTES)
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


def scan_interval_from_options(options: Mapping[str, Any]) -> timedelta:
    """Return a valid coordinator interval from config entry options."""
    try:
        minutes = int(options.get(CONF_SCAN_INTERVAL, DEFAULT_SCAN_INTERVAL_MINUTES))
    except (TypeError, ValueError):
        minutes = DEFAULT_SCAN_INTERVAL_MINUTES
    if not MIN_SCAN_INTERVAL_MINUTES <= minutes <= MAX_SCAN_INTERVAL_MINUTES:
        minutes = DEFAULT_SCAN_INTERVAL_MINUTES
    return timedelta(minutes=minutes)
