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
