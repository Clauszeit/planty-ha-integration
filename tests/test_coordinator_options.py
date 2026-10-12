"""Tests for configurable Planty snapshot polling."""

import unittest
from datetime import timedelta

from _support import prepare_imports

prepare_imports()

from custom_components.planty.const import scan_interval_from_options


class CoordinatorOptionsTest(unittest.TestCase):
    """Keep default and configured polling intervals predictable."""

    def test_default_interval_matches_existing_behavior(self):
        self.assertEqual(scan_interval_from_options({}), timedelta(minutes=15))

    def test_configured_interval_is_applied_in_minutes(self):
        self.assertEqual(scan_interval_from_options({"scan_interval": 30}), timedelta(minutes=30))

    def test_invalid_interval_falls_back_to_default(self):
        for value in ("invalid", None, 0, -1, 1441):
            with self.subTest(value=value):
                self.assertEqual(
                    scan_interval_from_options({"scan_interval": value}),
                    timedelta(minutes=15),
                )
