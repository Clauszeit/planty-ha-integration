"""Load pure integration modules without a Home Assistant runtime."""

from __future__ import annotations

import sys
import types
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path


def prepare_imports() -> None:
    """Provide the small platform declarations required by pure unit tests."""
    root = Path(__file__).resolve().parents[1]
    homeassistant_path = root / "custom_components" / "planty"
    if "homeassistant.const" not in sys.modules:
        homeassistant = types.ModuleType("homeassistant")
        homeassistant.__path__ = []
        const = types.ModuleType("homeassistant.const")
        const.Platform = types.SimpleNamespace(SENSOR="sensor")
        sys.modules.setdefault("homeassistant", homeassistant)
        sys.modules["homeassistant.const"] = const
    if "aiohttp" not in sys.modules:
        try:
            import aiohttp  # noqa: F401
        except ImportError:
            aiohttp = types.ModuleType("aiohttp")
            aiohttp.ClientError = type("ClientError", (Exception,), {})
            aiohttp.ContentTypeError = type("ContentTypeError", (aiohttp.ClientError,), {})
            aiohttp.ClientTimeout = lambda **kwargs: kwargs
            sys.modules["aiohttp"] = aiohttp
    components = sys.modules.setdefault("custom_components", types.ModuleType("custom_components"))
    components.__path__ = [str(root / "custom_components")]
    integration = types.ModuleType("custom_components.planty")
    integration.__path__ = [str(homeassistant_path)]
    sys.modules["custom_components.planty"] = integration


def prepare_sensor_imports() -> None:
    """Provide lightweight Home Assistant entities for sensor behavior tests."""
    prepare_imports()
    sensor_module = types.ModuleType("homeassistant.components.sensor")

    class SensorEntity:
        """Minimal sensor entity stand-in."""

    class SensorDeviceClass:
        DATE = "date"
        ENUM = "enum"

    @dataclass
    class SensorEntityDescription:
        key: str
        translation_key: str | None = None
        device_class: str | None = None
        options: tuple[str, ...] | None = None
        icon: str | None = None

    sensor_module.SensorEntity = SensorEntity
    sensor_module.SensorDeviceClass = SensorDeviceClass
    sensor_module.SensorEntityDescription = SensorEntityDescription
    sys.modules["homeassistant.components"] = types.ModuleType("homeassistant.components")
    sys.modules["homeassistant.components.sensor"] = sensor_module

    config_entries = types.ModuleType("homeassistant.config_entries")

    class ConfigEntry:
        def __init__(self, entry_id="entry", title="Planty account"):
            self.entry_id = entry_id
            self.title = title

        def async_on_unload(self, _unload):
            return None

    config_entries.ConfigEntry = ConfigEntry
    sys.modules["homeassistant.config_entries"] = config_entries

    core = types.ModuleType("homeassistant.core")
    core.HomeAssistant = type("HomeAssistant", (), {})
    sys.modules["homeassistant.core"] = core

    device_registry = types.ModuleType("homeassistant.helpers.device_registry")
    device_registry.DeviceInfo = dict
    sys.modules["homeassistant.helpers.device_registry"] = device_registry

    entity_platform = types.ModuleType("homeassistant.helpers.entity_platform")
    entity_platform.AddEntitiesCallback = type("AddEntitiesCallback", (), {})
    sys.modules["homeassistant.helpers.entity_platform"] = entity_platform
    helpers = types.ModuleType("homeassistant.helpers")
    helpers.__path__ = []
    sys.modules["homeassistant.helpers"] = helpers

    entity_registry = types.ModuleType("homeassistant.helpers.entity_registry")
    entity_registry.async_get = lambda hass: hass.entity_registry
    helpers.entity_registry = entity_registry
    sys.modules["homeassistant.helpers.entity_registry"] = entity_registry

    update_coordinator = types.ModuleType("homeassistant.helpers.update_coordinator")

    class CoordinatorEntity:
        def __init__(self, coordinator):
            self.coordinator = coordinator

        def _handle_coordinator_update(self):
            return None

    update_coordinator.CoordinatorEntity = CoordinatorEntity
    sys.modules["homeassistant.helpers.update_coordinator"] = update_coordinator

    dt_module = types.ModuleType("homeassistant.util.dt")
    dt_module.now = lambda: datetime(2026, 10, 12, tzinfo=timezone.utc)
    homeassistant_util = types.ModuleType("homeassistant.util")
    homeassistant_util.dt = dt_module
    sys.modules["homeassistant.util"] = homeassistant_util
    sys.modules["homeassistant.util.dt"] = dt_module

    coordinator = types.ModuleType("custom_components.planty.coordinator")
    coordinator.PlantyDataUpdateCoordinator = type("PlantyDataUpdateCoordinator", (), {})
    sys.modules["custom_components.planty.coordinator"] = coordinator
