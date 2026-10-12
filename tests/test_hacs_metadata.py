"""Validate Home Assistant and HACS repository metadata."""

import json
import unittest
from pathlib import Path


REPOSITORY_ROOT = Path(__file__).resolve().parents[1]


class HacsMetadataTest(unittest.TestCase):
    """Keep the metadata needed for HACS installation complete and aligned."""

    def test_hacs_manifest_and_info_are_present(self):
        hacs_manifest = json.loads((REPOSITORY_ROOT / "hacs.json").read_text())
        info_file = REPOSITORY_ROOT / "info.md"
        brand_icon = REPOSITORY_ROOT / "custom_components/planty/brand/icon.png"

        self.assertEqual(hacs_manifest["name"], "Planty")
        self.assertTrue(info_file.is_file())
        self.assertIn("Read-only-Token", info_file.read_text())
        self.assertTrue(brand_icon.is_file())

    def test_home_assistant_manifest_has_hacs_required_fields(self):
        manifest = json.loads(
            (REPOSITORY_ROOT / "custom_components/planty/manifest.json").read_text()
        )
        required_fields = {"domain", "documentation", "issue_tracker", "codeowners", "name", "version"}

        self.assertTrue(required_fields.issubset(manifest))
        self.assertEqual(manifest["domain"], "planty")
        self.assertEqual(manifest["version"], (REPOSITORY_ROOT / "VERSION").read_text().strip())
