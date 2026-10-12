"""Planty account summaries and garden detail sensors."""

from __future__ import annotations

from datetime import date

from homeassistant.components.sensor import SensorDeviceClass, SensorEntity, SensorEntityDescription
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.device_registry import DeviceInfo
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity
from homeassistant.util import dt as dt_util

from .const import DOMAIN
from .coordinator import PlantyDataUpdateCoordinator
from .data import (
    count_overdue_tasks,
    count_tasks_due_today,
    get_active_gardens,
    get_active_plants,
    get_active_places,
    get_next_task,
    get_open_tasks,
    get_overdue_tasks,
    get_record_by_id,
    get_records_for_garden,
)


PLANT_PHASES = (
    "sow_pending",
    "raising",
    "plant_pending",
    "planted",
    "uprooted",
    "overwintering",
    "completed",
    "unknown",
)
PLACE_KINDS = ("Beet", "Topf", "Kübel", "Balkonkasten", "Einzelpflanze", "Sonstiges")
DETAIL_ATTRIBUTE_KEYS = (
    "name",
    "variety",
    "scientific_name",
    "quantity",
    "phase",
    "season",
    "season_year",
    "permanent",
    "winter_at_location",
    "start_date",
    "purchased_date",
    "seed_date",
    "start_comment",
    "source",
    "notes",
)
TASK_ATTRIBUTE_KEYS = (
    "title",
    "kind",
    "status",
    "time",
    "repeat_days",
    "repeat_end",
    "last_done",
    "fertilizer_product",
    "dosage",
    "notes",
)


SENSOR_DESCRIPTIONS = (
    SensorEntityDescription(key="garden_count", translation_key="garden_count", icon="mdi:flower-tulip"),
    SensorEntityDescription(key="place_count", translation_key="place_count", icon="mdi:map-marker-multiple"),
    SensorEntityDescription(key="plant_count", translation_key="plant_count", icon="mdi:sprout"),
    SensorEntityDescription(key="open_task_count", translation_key="open_task_count", icon="mdi:format-list-checks"),
    SensorEntityDescription(
        key="due_today_task_count",
        translation_key="due_today_task_count",
        icon="mdi:calendar-today",
    ),
    SensorEntityDescription(
        key="overdue_task_count",
        translation_key="overdue_task_count",
        icon="mdi:calendar-alert",
    ),
    SensorEntityDescription(
        key="next_task_due",
        translation_key="next_task_due",
        device_class=SensorDeviceClass.DATE,
        icon="mdi:calendar-clock",
    ),
    SensorEntityDescription(
        key="next_task_name",
        translation_key="next_task_name",
        icon="mdi:calendar-check",
    ),
)
GARDEN_DESCRIPTION = SensorEntityDescription(
    key="garden_overview", translation_key="garden_overview", icon="mdi:flower-tulip"
)
PLACE_DESCRIPTION = SensorEntityDescription(
    key="place_kind",
    translation_key="place_kind",
    device_class=SensorDeviceClass.ENUM,
    options=PLACE_KINDS,
    icon="mdi:map-marker",
)
PLANT_DESCRIPTION = SensorEntityDescription(
    key="plant_phase",
    translation_key="plant_phase",
    device_class=SensorDeviceClass.ENUM,
    options=PLANT_PHASES,
    icon="mdi:sprout",
)
TASK_DESCRIPTION = SensorEntityDescription(
    key="task_due",
    translation_key="task_due",
    device_class=SensorDeviceClass.DATE,
    icon="mdi:calendar-check",
)


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up summary sensors and discover garden records as they appear."""
    coordinator: PlantyDataUpdateCoordinator = hass.data[DOMAIN][entry.entry_id]
    entities: list[SensorEntity] = [
        PlantySummarySensor(coordinator, entry, description)
        for description in SENSOR_DESCRIPTIONS
    ]
    known_unique_ids: set[str] = set()
    entities.extend(_collect_detail_entities(coordinator, entry, known_unique_ids))
    async_add_entities(entities)

    def add_new_detail_entities() -> None:
        """Add entities for records created after initial setup."""
        new_entities = _collect_detail_entities(coordinator, entry, known_unique_ids)
        if new_entities:
            async_add_entities(new_entities)

    entry.async_on_unload(coordinator.async_add_listener(add_new_detail_entities))


def _collect_detail_entities(coordinator, entry, known_unique_ids: set[str]) -> list[SensorEntity]:
    """Create entities for every newly visible garden and garden resource."""
    snapshot = coordinator.data or {}
    entities = []
    for garden in get_active_gardens(snapshot):
        garden_id = garden.get("id")
        if isinstance(garden_id, str) and garden_id:
            entities.extend(
                _collect_garden_entities(coordinator, entry, snapshot, garden_id, known_unique_ids)
            )
    return entities


def _collect_garden_entities(coordinator, entry, snapshot, garden_id, known_unique_ids):
    """Create one garden sensor and new detail sensors for a garden."""
    entities = [PlantyGardenSensor(coordinator, entry, garden_id)]
    for collection, entity_class in DETAIL_SENSOR_TYPES:
        for record in get_records_for_garden(snapshot, collection, garden_id):
            record_id = record.get("id")
            if isinstance(record_id, str) and record_id:
                entities.append(entity_class(coordinator, entry, garden_id, record_id))
    return [
        entity for entity in entities
        if _remember_entity(entity, known_unique_ids)
    ]


def _remember_entity(entity: SensorEntity, known_unique_ids: set[str]) -> bool:
    """Return whether this entity has not been added before."""
    if entity.unique_id in known_unique_ids:
        return False
    known_unique_ids.add(entity.unique_id)
    return True


def _account_device_info(entry: ConfigEntry) -> DeviceInfo:
    """Build the parent device for the connected Planty account."""
    return DeviceInfo(
        identifiers={(DOMAIN, entry.entry_id)},
        name=entry.title,
        manufacturer="Planty",
        model="Planty account",
    )


def _garden_device_info(entry: ConfigEntry, garden: dict) -> DeviceInfo:
    """Attach individual records to a named Planty garden device."""
    garden_id = garden["id"]
    return DeviceInfo(
        identifiers={(DOMAIN, f"{entry.entry_id}_{garden_id}")},
        name=garden.get("name") or "Planty garden",
        manufacturer="Planty",
        model="Garden",
        via_device=(DOMAIN, entry.entry_id),
    )


def _details(record: dict, keys: tuple[str, ...]) -> dict:
    """Return present, meaningful detail fields without leaking image payloads."""
    return {
        key: record[key]
        for key in keys
        if key in record and record[key] not in (None, "")
    }


def _task_attributes(snapshot: dict, task: dict) -> dict:
    """Collect related garden, plant and place names for a task."""
    attributes = _details(task, TASK_ATTRIBUTE_KEYS)
    attributes["task_id"] = task.get("id")
    if task.get("due_date"):
        attributes["due_date"] = task["due_date"]
    garden = get_record_by_id(snapshot, "gardens", task.get("garden_id"))
    plant = get_record_by_id(snapshot, "plants", task.get("plant_id"))
    place = get_record_by_id(snapshot, "places", task.get("place_id"))
    if garden and garden.get("name"):
        attributes["garden"] = garden["name"]
    if plant and plant.get("name"):
        attributes["plant"] = plant["name"]
    if place and place.get("name"):
        attributes["place"] = place["name"]
    return attributes


class PlantyCoordinatorSensor(CoordinatorEntity, SensorEntity):
    """Base for Planty sensors that update with the shared snapshot."""

    _attr_has_entity_name = True

    def __init__(
        self,
        coordinator: PlantyDataUpdateCoordinator,
        entry: ConfigEntry,
        description: SensorEntityDescription,
        unique_id: str,
        garden_id: str | None = None,
    ) -> None:
        super().__init__(coordinator)
        self.entity_description = description
        self._attr_unique_id = unique_id
        self._garden_id = garden_id
        self._attr_device_info = _account_device_info(entry)
        if garden_id is not None:
            garden = get_record_by_id(coordinator.data or {}, "gardens", garden_id)
            if garden:
                self._attr_device_info = _garden_device_info(entry, garden)

    def _update_translation_placeholders(self) -> None:
        """Update dynamic names when Planty records are renamed."""

    def _handle_coordinator_update(self) -> None:
        self._update_translation_placeholders()
        super()._handle_coordinator_update()

    def _garden(self) -> dict | None:
        """Return the sensor's garden from the latest snapshot."""
        if self._garden_id is None:
            return None
        return get_record_by_id(self.coordinator.data or {}, "gardens", self._garden_id)

    def _record(self, collection: str, record_id: str) -> dict | None:
        """Return a resource record from the latest snapshot."""
        return get_record_by_id(self.coordinator.data or {}, collection, record_id)

    def _is_record_available(self, collection: str, record_id: str) -> bool:
        """Hide archived or removed resources while keeping their history."""
        record = self._record(collection, record_id)
        garden = self._garden()
        return bool(
            self.coordinator.last_update_success
            and record
            and not record.get("archived")
            and garden
            and not garden.get("archived")
        )


class PlantySummarySensor(PlantyCoordinatorSensor):
    """Expose account-wide counts and the next task."""

    def __init__(
        self,
        coordinator: PlantyDataUpdateCoordinator,
        entry: ConfigEntry,
        description: SensorEntityDescription,
    ) -> None:
        super().__init__(coordinator, entry, description, f"{entry.entry_id}_{description.key}")

    @property
    def native_value(self) -> int | date | str | None:
        """Calculate one account count, task date or title."""
        snapshot = self.coordinator.data
        if not snapshot:
            return None
        today = dt_util.now().date()
        values = {
            "garden_count": len(get_active_gardens(snapshot)),
            "place_count": len(get_active_places(snapshot)),
            "plant_count": len(get_active_plants(snapshot)),
            "open_task_count": len(get_open_tasks(snapshot)),
            "due_today_task_count": count_tasks_due_today(snapshot, today),
            "overdue_task_count": count_overdue_tasks(snapshot, today),
        }
        if self.entity_description.key in values:
            return values[self.entity_description.key]
        task = get_next_task(snapshot)
        if self.entity_description.key == "next_task_name":
            return task.get("title") if task else None
        due_date = task.get("due_date") if task else None
        return date.fromisoformat(due_date) if due_date else None

    @property
    def extra_state_attributes(self) -> dict | None:
        """Expose useful context alongside account-wide sensor values."""
        snapshot = self.coordinator.data
        if not snapshot:
            return None
        key = self.entity_description.key
        today = dt_util.now().date()
        if key == "plant_count":
            phases = {}
            for plant in get_active_plants(snapshot):
                phase = plant.get("phase", "unknown")
                phases[phase if phase in PLANT_PHASES else "unknown"] = (
                    phases.get(phase if phase in PLANT_PHASES else "unknown", 0) + 1
                )
            return {"plants_by_phase": phases}
        if key == "open_task_count":
            return {
                "due_today": count_tasks_due_today(snapshot, today),
                "overdue": count_overdue_tasks(snapshot, today),
            }
        if key == "overdue_task_count":
            return {
                "overdue_tasks": [
                    _task_attributes(snapshot, task)
                    for task in get_overdue_tasks(snapshot, today)[:10]
                ]
            }
        if key in {"next_task_due", "next_task_name"}:
            task = get_next_task(snapshot)
            return _task_attributes(snapshot, task) if task else None
        return None


class PlantyGardenSensor(PlantyCoordinatorSensor):
    """Expose each accessible garden as a named Home Assistant device."""

    def __init__(self, coordinator, entry, garden_id: str) -> None:
        super().__init__(
            coordinator,
            entry,
            GARDEN_DESCRIPTION,
            f"{entry.entry_id}_garden_{garden_id}_overview",
            garden_id,
        )

    @property
    def native_value(self) -> str | None:
        """Return the current garden name."""
        garden = self._garden()
        return garden.get("name") if garden else None

    @property
    def available(self) -> bool:
        """Return whether this garden is currently accessible and active."""
        garden = self._garden()
        return bool(self.coordinator.last_update_success and garden and not garden.get("archived"))

    @property
    def extra_state_attributes(self) -> dict | None:
        """Describe the garden, access role and current contents."""
        garden = self._garden()
        snapshot = self.coordinator.data or {}
        if not garden or garden.get("archived"):
            return None
        garden_id = garden.get("id")
        plants = get_records_for_garden(snapshot, "plants", garden_id)
        active_plants = [
            plant for plant in plants if plant.get("phase") != "completed"
        ]
        tasks = get_records_for_garden(snapshot, "tasks", garden_id)
        open_tasks = [task for task in tasks if task.get("status", "open") == "open"]
        today = dt_util.now().date()
        overdue = [
            task for task in open_tasks
            if isinstance(task.get("due_date"), str)
            and _is_overdue(task["due_date"], today)
        ]
        attributes = _details(garden, ("description", "access", "owner_username", "plan_width_m"))
        attributes.update(
            {
                "place_count": len(get_records_for_garden(snapshot, "places", garden_id)),
                "active_plant_count": len(active_plants),
                "open_task_count": len(open_tasks),
                "due_today_task_count": sum(
                    1 for task in open_tasks if task.get("due_date") == today.isoformat()
                ),
                "overdue_task_count": len(overdue),
            }
        )
        next_task = _get_next_task_for_records(open_tasks)
        if next_task:
            attributes["next_task"] = next_task.get("title")
            attributes["next_task_due"] = next_task.get("due_date")
        return attributes


class PlantyPlaceSensor(PlantyCoordinatorSensor):
    """Expose growing-place properties and the plants located there."""

    def __init__(self, coordinator, entry, garden_id: str, place_id: str) -> None:
        super().__init__(
            coordinator,
            entry,
            PLACE_DESCRIPTION,
            f"{entry.entry_id}_place_{place_id}_kind",
            garden_id,
        )
        self._place_id = place_id
        self._update_translation_placeholders()

    def _place(self) -> dict | None:
        return self._record("places", self._place_id)

    def _update_translation_placeholders(self) -> None:
        place = self._place()
        place_name = (place or {}).get("name") or ""
        place_kind = (place or {}).get("kind") or ""
        self._attr_translation_placeholders = {"place": f"{place_name} · {place_kind}".strip(" ·")}

    @property
    def native_value(self) -> str | None:
        """Return the growing-place type for its enum state."""
        place = self._place()
        if not place:
            return None
        place_kind = place.get("kind", "Sonstiges")
        return place_kind if place_kind in PLACE_KINDS else "Sonstiges"

    @property
    def available(self) -> bool:
        return self._is_record_available("places", self._place_id)

    @property
    def extra_state_attributes(self) -> dict | None:
        """Expose location, growing conditions and plants assigned to this place."""
        place = self._place()
        snapshot = self.coordinator.data or {}
        if not place:
            return None
        attributes = _details(place, ("location", "light", "area", "soil", "notes"))
        garden = self._garden()
        if garden and garden.get("name"):
            attributes["garden"] = garden["name"]
        plants = [
            plant for plant in get_records_for_garden(snapshot, "plants", self._garden_id)
            if self._place_id in {plant.get("place_id"), plant.get("planned_place_id")}
        ]
        attributes["plants"] = [
            {
                "name": plant.get("name"),
                "variety": plant.get("variety"),
                "quantity": plant.get("quantity", 1),
                "phase": plant.get("phase"),
            }
            for plant in plants
        ]
        return attributes


class PlantyPlantSensor(PlantyCoordinatorSensor):
    """Expose an individual plant's phase and cultivation details."""

    def __init__(self, coordinator, entry, garden_id: str, plant_id: str) -> None:
        super().__init__(
            coordinator,
            entry,
            PLANT_DESCRIPTION,
            f"{entry.entry_id}_plant_{plant_id}_phase",
            garden_id,
        )
        self._plant_id = plant_id
        self._update_translation_placeholders()

    def _plant(self) -> dict | None:
        return self._record("plants", self._plant_id)

    def _update_translation_placeholders(self) -> None:
        plant = self._plant() or {}
        name = plant.get("name") or "Plant"
        variety = plant.get("variety")
        label = f"{name} ({variety})" if variety else name
        self._attr_translation_placeholders = {"plant": label[:120]}

    @property
    def native_value(self) -> str | None:
        """Return the phase key, translated by Home Assistant."""
        plant = self._plant()
        if not plant:
            return None
        phase = plant.get("phase", "unknown")
        return phase if phase in PLANT_PHASES else "unknown"

    @property
    def available(self) -> bool:
        return self._is_record_available("plants", self._plant_id)

    @property
    def extra_state_attributes(self) -> dict | None:
        """Expose growing dates, amount, season and current location."""
        plant = self._plant()
        snapshot = self.coordinator.data or {}
        if not plant:
            return None
        attributes = _details(plant, DETAIL_ATTRIBUTE_KEYS)
        garden = self._garden()
        if garden and garden.get("name"):
            attributes["garden"] = garden["name"]
        for field, label in (("place_id", "place"), ("planned_place_id", "planned_place")):
            place = get_record_by_id(snapshot, "places", plant.get(field))
            if place and place.get("name"):
                attributes[label] = place["name"]
        actions = plant.get("recent_actions")
        if isinstance(actions, list):
            attributes["recent_actions"] = actions[:5]
        return attributes


class PlantyTaskSensor(PlantyCoordinatorSensor):
    """Expose the due date and full useful context for each task."""

    def __init__(self, coordinator, entry, garden_id: str, task_id: str) -> None:
        super().__init__(
            coordinator,
            entry,
            TASK_DESCRIPTION,
            f"{entry.entry_id}_task_{task_id}_due",
            garden_id,
        )
        self._task_id = task_id
        self._update_translation_placeholders()

    def _task(self) -> dict | None:
        return self._record("tasks", self._task_id)

    def _update_translation_placeholders(self) -> None:
        task = self._task() or {}
        title = task.get("title") or task.get("kind") or "Task"
        due_date = task.get("due_date") or ""
        plant = get_record_by_id(
            self.coordinator.data or {}, "plants", task.get("plant_id")
        )
        plant_name = (plant or {}).get("name")
        detail = f" · {plant_name}" if plant_name else ""
        self._attr_translation_placeholders = {
            "task": f"{title}{detail} · {due_date}".strip(" ·")[:160]
        }

    @property
    def native_value(self) -> date | None:
        """Return the task due date when the API supplied a valid ISO date."""
        task = self._task()
        due_date = (task or {}).get("due_date")
        if not isinstance(due_date, str):
            return None
        try:
            return date.fromisoformat(due_date)
        except ValueError:
            return None

    @property
    def available(self) -> bool:
        return self._is_record_available("tasks", self._task_id)

    @property
    def extra_state_attributes(self) -> dict | None:
        """Expose status, repetition, notes and related plant/place for the task."""
        task = self._task()
        if not task:
            return None
        return _task_attributes(self.coordinator.data or {}, task)


DETAIL_SENSOR_TYPES = (
    ("places", PlantyPlaceSensor),
    ("plants", PlantyPlantSensor),
    ("tasks", PlantyTaskSensor),
)


def _is_overdue(value: str, today: date) -> bool:
    """Check a date string without failing on malformed remote data."""
    try:
        return date.fromisoformat(value) < today
    except ValueError:
        return False


def _get_next_task_for_records(tasks: list[dict]) -> dict | None:
    """Return the earliest open garden task with a valid due date."""
    candidates = []
    for task in tasks:
        due_date = task.get("due_date")
        if not isinstance(due_date, str):
            continue
        try:
            date.fromisoformat(due_date)
        except ValueError:
            continue
        candidates.append(task)
    return min(candidates, key=lambda task: task["due_date"]) if candidates else None
