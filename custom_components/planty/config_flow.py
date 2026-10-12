"""Config flow for the Planty integration."""

from __future__ import annotations

import probatio

from homeassistant import config_entries
from homeassistant.helpers.aiohttp_client import async_get_clientsession
from homeassistant.helpers.selector import TextSelector, TextSelectorConfig, TextSelectorType

from .api import (
    PlantyApi,
    PlantyAuthenticationError,
    PlantyConnectionError,
    PlantyInvalidResponseError,
    normalize_base_url,
)
from .const import CONF_TOKEN, CONF_URL, DOMAIN


class PlantyConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Configure a Planty server and its read-only API token."""

    VERSION = 1

    async def async_step_user(self, user_input: dict | None = None):
        """Validate the Planty URL and token before creating the entry."""
        errors: dict[str, str] = {}
        if user_input is not None:
            try:
                url = normalize_base_url(user_input[CONF_URL])
            except (KeyError, ValueError):
                errors["base"] = "invalid_url"
            else:
                await self.async_set_unique_id(url)
                self._abort_if_unique_id_configured()
                client = PlantyApi(
                    async_get_clientsession(self.hass), url, user_input[CONF_TOKEN].strip()
                )
                try:
                    profile = await client.async_get_profile()
                except PlantyAuthenticationError:
                    errors["base"] = "invalid_auth"
                except PlantyConnectionError:
                    errors["base"] = "cannot_connect"
                except PlantyInvalidResponseError:
                    errors["base"] = "invalid_response"
                else:
                    return self.async_create_entry(
                        title=f"Planty ({profile['username']})",
                        data={CONF_URL: url, CONF_TOKEN: user_input[CONF_TOKEN].strip()},
                    )

        schema = probatio.Schema(
            {
                probatio.Required(CONF_URL): str,
                probatio.Required(probatio.Secret(CONF_TOKEN)): TextSelector(
                    TextSelectorConfig(
                        type=TextSelectorType.PASSWORD,
                        autocomplete="current-password",
                    )
                ),
            }
        )
        return self.async_show_form(step_id="user", data_schema=schema, errors=errors)

    async def async_step_reauth(self, _entry_data: dict):
        """Ask for a replacement token after the configured one was revoked."""
        return await self.async_step_reauth_confirm()

    async def async_step_reauth_confirm(self, user_input: dict | None = None):
        """Validate and save a replacement read-only token."""
        entry = self._get_reauth_entry()
        errors: dict[str, str] = {}
        if user_input is not None:
            token = user_input[CONF_TOKEN].strip()
            client = PlantyApi(
                async_get_clientsession(self.hass), entry.data[CONF_URL], token
            )
            try:
                await client.async_get_profile()
            except PlantyAuthenticationError:
                errors["base"] = "invalid_auth"
            except PlantyConnectionError:
                errors["base"] = "cannot_connect"
            except PlantyInvalidResponseError:
                errors["base"] = "invalid_response"
            else:
                return self.async_update_reload_and_abort(
                    entry,
                    data_updates={CONF_TOKEN: token},
                )

        schema = probatio.Schema(
            {
                probatio.Required(probatio.Secret(CONF_TOKEN)): TextSelector(
                    TextSelectorConfig(
                        type=TextSelectorType.PASSWORD,
                        autocomplete="current-password",
                    )
                )
            }
        )
        return self.async_show_form(
            step_id="reauth_confirm", data_schema=schema, errors=errors
        )
