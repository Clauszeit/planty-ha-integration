"""Regression tests for Planty snapshot summaries."""

import unittest
from datetime import date

from _support import prepare_imports

prepare_imports()

from custom_components.planty.data import (
    count_overdue_tasks,
    get_active_gardens,
    get_active_plants,
    get_next_task,
    get_open_tasks,
)


class SnapshotSummaryTest(unittest.TestCase):
    """Check visibility, completion and due-date rules for summaries."""

    def setUp(self):
        self.snapshot = {
            "gardens": [{"id": "g1"}, {"id": "g2", "archived": True}],
            "plants": [
                {"id": "p1", "phase": "planted"},
                {"id": "p2", "phase": "completed"},
                {"id": "p3", "phase": "planted", "archived": True},
            ],
            "tasks": [
                {"id": "t1", "status": "open", "due_date": "2026-10-11"},
                {"id": "t2", "status": "open", "due_date": "2026-10-12"},
                {"id": "t3", "status": "done", "due_date": "2026-10-01"},
                {"id": "t4", "status": "open", "due_date": "invalid"},
                {"id": "t5", "status": "open", "due_date": "2026-10-01", "archived": True},
            ],
        }

    def test_counts_exclude_archived_and_completed_items(self):
        self.assertEqual(len(get_active_gardens(self.snapshot)), 1)
        self.assertEqual(len(get_active_plants(self.snapshot)), 1)
        self.assertEqual([task["id"] for task in get_open_tasks(self.snapshot)], ["t1", "t2", "t4"])

    def test_next_and_overdue_tasks_ignore_closed_archived_and_invalid_dates(self):
        next_task = get_next_task(self.snapshot)
        self.assertEqual(next_task["id"], "t1")
        self.assertEqual(count_overdue_tasks(self.snapshot, date(2026, 10, 12)), 1)

    def test_missing_task_lists_are_empty(self):
        empty_snapshot = {}
        self.assertIsNone(get_next_task(empty_snapshot))
        self.assertEqual(count_overdue_tasks(empty_snapshot, date(2026, 10, 12)), 0)


if __name__ == "__main__":
    unittest.main()
