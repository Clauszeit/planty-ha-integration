"""Load pure integration modules without a Home Assistant runtime."""

from __future__ import annotations

import sys
import types
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
