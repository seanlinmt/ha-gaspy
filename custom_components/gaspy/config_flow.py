"""Config flow for Gaspy."""
from __future__ import annotations
import logging
from typing import Any

import voluptuous as vol

from homeassistant import config_entries
from homeassistant.helpers import config_entry_oauth2_flow
from homeassistant.helpers.aiohttp_client import async_get_clientsession

from homeassistant.const import (
    CONF_LATITUDE,
    CONF_LONGITUDE,
)

from .const import DOMAIN, CONF_DISTANCE, OAUTH2_SCOPES


_LOGGER = logging.getLogger(__name__)


def validate_latitude(value):
    """Validate latitude is between -90 and 90."""
    try:
        lat = float(value)
        return -90 <= lat <= 90
    except (ValueError, TypeError):
        return False


def validate_longitude(value):
    """Validate longitude is between -180 and 180."""
    try:
        lon = float(value)
        return -180 <= lon <= 180
    except (ValueError, TypeError):
        return False


class ConfigFlow(
    config_entry_oauth2_flow.AbstractOAuth2FlowHandler, domain=DOMAIN
):
    """Handle a config flow for Gaspy."""

    DOMAIN = DOMAIN
    VERSION = 1

    def __init__(self) -> None:
        """Initialize the config flow."""
        super().__init__()
        self.data = {}

    @property
    def logger(self) -> logging.Logger:
        """Return logger."""
        return _LOGGER

    @property
    def extra_authorize_data(self) -> dict[str, Any]:
        """Extra data that needs to be appended to the authorize url."""
        return {"scope": " ".join(OAUTH2_SCOPES)}

    async def async_oauth_create_entry(self, data: dict) -> FlowResult:
        """Create an entry for the flow, or update existing entry."""
        session = async_get_clientsession(self.hass)
        headers = {
            "Authorization": f"Bearer {data['token']['access_token']}"
        }
        try:
            async with session.get("https://www.googleapis.com/oauth2/v2/userinfo", headers=headers) as resp:
                resp.raise_for_status()
                user_info = await resp.json()
                email = user_info["email"]
        except Exception as e:
            _LOGGER.error("Failed to get user info: %s", e)
            return self.async_abort(reason="oauth_error")

        await self.async_set_unique_id(email)
        self._abort_if_unique_id_configured()

        self.data = data
        self.data["email"] = email

        return await self.async_step_location()

    async def async_step_location(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        """Handle the location step."""
        if user_input is None:
            return self.async_show_form(
                step_id="location",
                data_schema=vol.Schema(
                    {
                        vol.Required(CONF_DISTANCE, default=10): vol.All(
                            vol.Coerce(float), vol.Range(min=1.0, max=100.0)
                        ),
                        vol.Required(CONF_LATITUDE): vol.All(str, validate_latitude),
                        vol.Required(CONF_LONGITUDE): vol.All(str, validate_longitude),
                    }
                ),
            )

        self.data.update(user_input)
        return self.async_create_entry(title=self.data["email"], data=self.data)
