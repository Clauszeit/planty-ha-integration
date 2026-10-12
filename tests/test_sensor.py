"""Regression tests for detailed Planty sensor values and names."""

import unittest
from types import SimpleNamespace

from _support import prepare_sensor_imports

prepare_sensor_imports()

from homeassistant.config_entries import ConfigEntry

from custom_components.planty.sensor import (
    PlantyGardenSensor,
    PlantyPlaceSensor,
    PlantyPlantSensor,
    PlantySummarySensor,
    PlantyTaskSensor,
    SENSOR_DESCRIPTIONS,
)


class SensorDetailTest(unittest.TestCase):
    """Ensure entities expose distinct labels and useful linked data."""

    def setUp(self):
        self.snapshot = {
            "gardens": [{"id": "garden-1", "name": "Hinterer Garten", "description": "Am Zaun", "access": "owner"}],
            "places": [{
                "id": "place-1", "garden_id": "garden-1", "name": "Hochbeet Nord",
                "kind": "Beet", "location": "Nordseite", "light": "Sonne", "area": 3.5,
            }],
            "plants": [{
                "id": "plant-1", "garden_id": "garden-1", "place_id": "place-1",
                "name": "Tomate", "variety": "Black Cherry", "quantity": 2,
                "phase": "planted", "scientific_name": "Solanum lycopersicum",
            }],
            "tasks": [{
                "id": "task-1", "garden_id": "garden-1", "place_id": "place-1",
                "plant_id": "plant-1", "title": "Tomaten düngen", "kind": "Düngen",
                "due_date": "2026-10-12", "status": "open", "fertilizer_product": "Kompost",
            }],
        }
        self.coordinator = type("Coordinator", (), {
            "data": self.snapshot,
            "last_update_success": True,
        })()
        self.entry = ConfigEntry()

    @staticmethod
    def _hass_with_plant_entity():
        """Return a Home Assistant stub with a registered Planty plant sensor."""
        return SimpleNamespace(
            entity_registry=SimpleNamespace(
                async_get_entity_id=lambda platform, domain, unique_id: (
                    "sensor.tomate_wachstumsphase"
                    if (platform, domain, unique_id)
                    == ("sensor", "planty", "entry_plant_plant-1_phase")
                    else None
                )
            )
        )

    def test_summary_exposes_counts_for_places_and_due_today(self):
        values = {
            description.key: PlantySummarySensor(self.coordinator, self.entry, description).native_value
            for description in SENSOR_DESCRIPTIONS
        }
        self.assertEqual(values["garden_count"], 1)
        self.assertEqual(values["place_count"], 1)
        self.assertEqual(values["plant_count"], 1)
        self.assertEqual(values["due_today_task_count"], 1)
        self.assertEqual(values["next_task_name"], "Tomaten düngen · Tomate")
        next_task = PlantySummarySensor(
            self.coordinator,
            self.entry,
            next(
                description
                for description in SENSOR_DESCRIPTIONS
                if description.key == "next_task_name"
            ),
        )
        next_task.hass = self._hass_with_plant_entity()
        self.assertEqual(
            next_task.extra_state_attributes["plant_entity_id"],
            "sensor.tomate_wachstumsphase",
        )

    def test_detail_entities_have_distinct_dynamic_names_and_attributes(self):
        garden = PlantyGardenSensor(self.coordinator, self.entry, "garden-1")
        place = PlantyPlaceSensor(self.coordinator, self.entry, "garden-1", "place-1")
        plant = PlantyPlantSensor(self.coordinator, self.entry, "garden-1", "plant-1")
        task = PlantyTaskSensor(self.coordinator, self.entry, "garden-1", "task-1")
        task.hass = self._hass_with_plant_entity()

        self.assertEqual(garden.native_value, "Hinterer Garten")
        self.assertEqual(garden.extra_state_attributes["active_plant_count"], 1)
        self.assertEqual(place.native_value, "beet")
        self.assertEqual(place.extra_state_attributes["light"], "Sonne")
        self.assertEqual(plant.native_value, "planted")
        self.assertEqual(plant.extra_state_attributes["variety"], "Black Cherry")
        self.assertEqual(task.native_value.isoformat(), "2026-10-12")
        self.assertEqual(task.extra_state_attributes["plant"], "Tomate")
        self.assertEqual(task.extra_state_attributes["plant_id"], "plant-1")
        self.assertEqual(
            task.extra_state_attributes["plant_entity_id"],
            "sensor.tomate_wachstumsphase",
        )
        self.assertEqual(task.extra_state_attributes["fertilizer_product"], "Kompost")
        self.assertEqual(place._attr_translation_placeholders["place"], "Hochbeet Nord")
        self.assertEqual(place.extra_state_attributes["kind"], "Beet")
        self.assertEqual(plant._attr_translation_placeholders["plant"], "Tomate (Black Cherry)")
        self.assertIn("Tomaten düngen", task._attr_translation_placeholders["task"])
        self.snapshot["plants"][0]["name"] = "Cocktailtomate"
        plant._handle_coordinator_update()
        self.assertEqual(plant._attr_translation_placeholders["plant"], "Cocktailtomate (Black Cherry)")

    def test_variety_group_and_shared_task_are_exposed_for_dashboards(self):
        first = self.snapshot["plants"][0]
        first.update(name="Knoblauch", variety="Ljubascha", variety_group_id="group-1", variety_group_size=2)
        self.snapshot["plants"].append({**first, "id": "plant-2", "variety": "Garcua"})
        task_data = self.snapshot["tasks"][0]
        task_data.pop("plant_id")
        task_data["plant_ids"] = ["plant-1", "plant-2"]
        plant = PlantyPlantSensor(self.coordinator, self.entry, "garden-1", "plant-1")
        place = PlantyPlaceSensor(self.coordinator, self.entry, "garden-1", "place-1")
        task = PlantyTaskSensor(self.coordinator, self.entry, "garden-1", "task-1")
        task.hass = self._hass_with_plant_entity()
        self.assertEqual(plant.extra_state_attributes["variety_group_id"], "group-1")
        self.assertEqual(plant.extra_state_attributes["variety_group_size"], 2)
        self.assertEqual(place.extra_state_attributes["plants"][1]["variety_group_id"], "group-1")
        attributes = task.extra_state_attributes
        self.assertEqual(attributes["plant_ids"], ["plant-1", "plant-2"])
        self.assertEqual([record["variety"] for record in attributes["plants"]], ["Ljubascha", "Garcua"])
        self.assertEqual(attributes["plants"][0]["entity_id"], "sensor.tomate_wachstumsphase")
        self.assertEqual(attributes["variety_group_id"], "group-1")
        self.assertIn("2 Sorten", task._attr_translation_placeholders["task"])

    def test_shared_task_keeps_ids_when_a_variety_is_missing(self):
        task_data = self.snapshot["tasks"][0]
        task_data.pop("plant_id")
        task_data["plant_ids"] = ["missing", "plant-1"]
        task = PlantyTaskSensor(self.coordinator, self.entry, "garden-1", "task-1")
        attributes = task.extra_state_attributes
        self.assertEqual(attributes["plant_ids"], ["missing", "plant-1"])
        self.assertEqual([item["plant_id"] for item in attributes["plants"]], ["plant-1"])
        self.assertNotIn("plant", attributes)
        self.assertNotIn("variety_group_id", attributes)
        self.assertNotIn("2 Sorten", task._attr_translation_placeholders["task"])

    def test_shared_task_without_entity_registry_keeps_varieties(self):
        task_data = self.snapshot["tasks"][0]
        task_data.pop("plant_id")
        task_data["plant_ids"] = ["plant-1", "plant-2"]
        self.snapshot["plants"].append({**self.snapshot["plants"][0], "id": "plant-2", "variety": "Roma"})
        task = PlantyTaskSensor(self.coordinator, self.entry, "garden-1", "task-1")
        attributes = task.extra_state_attributes
        self.assertEqual([item["variety"] for item in attributes["plants"]], ["Black Cherry", "Roma"])
        self.assertTrue(all(item["entity_id"] is None for item in attributes["plants"]))
        self.assertEqual(attributes["plant"], "Tomate")
        self.assertNotIn("variety_group_id", attributes)

    def test_place_kind_is_mapped_to_a_translatable_option(self):
        self.snapshot["places"][0]["kind"] = "unsupported kind"
        place = PlantyPlaceSensor(self.coordinator, self.entry, "garden-1", "place-1")

        self.assertEqual(place.native_value, "sonstiges")

    def test_task_without_registered_plant_keeps_task_context(self):
        task = PlantyTaskSensor(self.coordinator, self.entry, "garden-1", "task-1")

        self.assertIsNone(task._plant_entity_id(None))
        self.assertIsNone(task._plant_entity_id("plant-1"))
        attributes = task.extra_state_attributes
        self.assertEqual(attributes["plant"], "Tomate")
        self.assertNotIn("plant_entity_id", attributes)

        self.snapshot["plants"] = []
        summary = PlantySummarySensor(
            self.coordinator,
            self.entry,
            next(
                description
                for description in SENSOR_DESCRIPTIONS
                if description.key == "next_task_name"
            ),
        )
        self.assertEqual(summary.native_value, "Tomaten düngen")

        self.snapshot["tasks"] = []
        self.assertIsNone(summary.native_value)


if __name__ == "__main__":
    unittest.main()
