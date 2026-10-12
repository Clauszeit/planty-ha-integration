"""Coordinated Planty snapshot polling."""

from __future__ import annotations

import logging

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.exceptions import ConfigEntryAuthFailed
from homeassistant.helpers.aiohttp_client import async_get_clientsession
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed

from .api import PlantyApi, PlantyApiError, PlantyAuthenticationError
from .const import CONF_TOKEN, CONF_URL, DOMAIN, scan_interval_from_options

LOGGER = logging.getLogger(__name__)


class PlantyDataUpdateCoordinator(DataUpdateCoordinator[dict]):
    """Fetch one authorized Planty snapshot for all entities."""

    def __init__(self, hass: HomeAssistant, entry: ConfigEntry) -> None:
        self.api = PlantyApi(
            async_get_clientsession(hass), entry.data[CONF_URL], entry.data[CONF_TOKEN]
        )
        super().__init__(
            hass,
            logger=LOGGER,
            name=DOMAIN,
            update_interval=scan_interval_from_options(entry.options),
        )

    async def _async_update_data(self) -> dict:
        """Fetch a snapshot and convert transport failures for Home Assistant."""
        try:
            return await self.api.async_get_snapshot()
        except PlantyAuthenticationError as error:
            raise ConfigEntryAuthFailed(str(error)) from error
        except PlantyApiError as error:
            raise UpdateFailed(str(error)) from error
