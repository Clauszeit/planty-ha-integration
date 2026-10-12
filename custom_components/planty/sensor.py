"""Planty summary sensors."""

from __future__ import annotations

from datetime import date

from homeassistant.components.sensor import SensorDeviceClass, SensorEntity, SensorEntityDescription
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.device_registry import DeviceInfo
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.util import dt as dt_util

from .const import DOMAIN
from .coordinator import PlantyDataUpdateCoordinator
from .data import (
    count_overdue_tasks,
    get_active_gardens,
    get_active_plants,
    get_next_task,
    get_open_tasks,
)


SENSOR_DESCRIPTIONS = (
    SensorEntityDescription(key="garden_count", translation_key="garden_count", icon="mdi:flower-tulip"),
    SensorEntityDescription(key="plant_count", translation_key="plant_count", icon="mdi:sprout"),
    SensorEntityDescription(key="open_task_count", translation_key="open_task_count", icon="mdi:format-list-checks"),
    SensorEntityDescription(key="overdue_task_count", translation_key="overdue_task_count", icon="mdi:calendar-alert"),
    SensorEntityDescription(
        key="next_task_due",
        translation_key="next_task_due",
        device_class=SensorDeviceClass.DATE,
        icon="mdi:calendar-clock",
    ),
)


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up Planty summary sensors."""
    coordinator: PlantyDataUpdateCoordinator = hass.data[DOMAIN][entry.entry_id]
    async_add_entities(
        PlantySummarySensor(coordinator, entry, description)
        for description in SENSOR_DESCRIPTIONS
    )


class PlantySummarySensor(SensorEntity):
    """Expose one aggregate value derived from the authorized snapshot."""

    _attr_has_entity_name = True

    def __init__(
        self,
        coordinator: PlantyDataUpdateCoordinator,
        entry: ConfigEntry,
        description: SensorEntityDescription,
    ) -> None:
        self.coordinator = coordinator
        self.entity_description = description
        self._attr_unique_id = f"{entry.entry_id}_{description.key}"
        self._attr_device_info = DeviceInfo(
            identifiers={(DOMAIN, entry.entry_id)},
            manufacturer="Planty",
            model="Self-hosted garden",
        )

    @property
    def available(self) -> bool:
        """Return whether a current snapshot is available."""
        return self.coordinator.last_update_success

    @property
    def native_value(self) -> int | date | None:
        """Calculate a count or the next open task date."""
        snapshot = self.coordinator.data
        if not snapshot:
            return None
        gardens = get_active_gardens(snapshot)
        plants = get_active_plants(snapshot)
        open_tasks = get_open_tasks(snapshot)
        today = dt_util.now().date()
        if self.entity_description.key == "garden_count":
            return len(gardens)
        if self.entity_description.key == "plant_count":
            return len(plants)
        if self.entity_description.key == "open_task_count":
            return len(open_tasks)
        if self.entity_description.key == "overdue_task_count":
            return count_overdue_tasks(snapshot, today)
        task = get_next_task(snapshot)
        return date.fromisoformat(task["due_date"]) if task else None

    @property
    def extra_state_attributes(self) -> dict[str, str] | None:
        """Add a small description for the task shown by the due-date sensor."""
        if self.entity_description.key != "next_task_due" or not self.coordinator.data:
            return None
        task = get_next_task(self.coordinator.data)
        if not task:
            return None
        garden = next(
            (item for item in self.coordinator.data["gardens"] if item.get("id") == task.get("garden_id")),
            None,
        )
        attributes = {"task_id": task["id"], "title": task.get("title", "")}
        if task.get("kind"):
            attributes["kind"] = task["kind"]
        if garden and garden.get("name"):
            attributes["garden"] = garden["name"]
        return attributes
