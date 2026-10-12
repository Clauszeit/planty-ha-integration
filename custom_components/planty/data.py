"""Pure snapshot calculations used by Planty sensors."""

from __future__ import annotations

from datetime import date

from .const import PLANT_COMPLETED_PHASE, TASK_OPEN_STATUS


def get_open_tasks(snapshot: dict) -> list[dict]:
    """Return active, open tasks with a mapping-shaped record."""
    return [
        task for task in snapshot.get("tasks", [])
        if isinstance(task, dict)
        and task.get("status", TASK_OPEN_STATUS) == TASK_OPEN_STATUS
        and not task.get("archived")
    ]


def get_active_gardens(snapshot: dict) -> list[dict]:
    """Return non-archived gardens."""
    return [
        garden for garden in snapshot.get("gardens", [])
        if isinstance(garden, dict) and not garden.get("archived")
    ]


def get_active_plants(snapshot: dict) -> list[dict]:
    """Return plants that are neither archived nor completed."""
    return [
        plant for plant in snapshot.get("plants", [])
        if isinstance(plant, dict)
        and not plant.get("archived")
        and plant.get("phase") != PLANT_COMPLETED_PHASE
    ]


def is_iso_date(value: object) -> bool:
    """Return whether a value is a valid ISO calendar date."""
    if not isinstance(value, str):
        return False
    try:
        date.fromisoformat(value)
    except ValueError:
        return False
    return True


def get_next_task(snapshot: dict) -> dict | None:
    """Return the task with the earliest valid due date."""
    candidates = [
        task for task in get_open_tasks(snapshot) if is_iso_date(task.get("due_date"))
    ]
    return min(candidates, key=lambda task: task["due_date"]) if candidates else None


def count_overdue_tasks(snapshot: dict, today: date) -> int:
    """Count open tasks whose due date is before the local day."""
    return sum(
        1 for task in get_open_tasks(snapshot)
        if is_iso_date(task.get("due_date")) and date.fromisoformat(task["due_date"]) < today
    )
