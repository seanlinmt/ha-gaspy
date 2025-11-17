"""Config flow for Gaspy."""
from __future__ import annotations
import logging
from typing import Any

import voluptuous as vol

from homeassistant import config_entries
from homeassistant.core import HomeAssistant
from homeassistant.data_entry_flow import FlowResult
from homeassistant.exceptions import HomeAssistantError

from homeassistant.const import (
    CONF_USERNAME,
    CONF_PASSWORD,
    CONF_LATITUDE,
    CONF_LONGITUDE,
)

from .const import DOMAIN, CONF_DISTANCE

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

STEP_USER_DATA_SCHEMA = vol.Schema(
    {
        vol.Required(CONF_USERNAME): str,
        vol.Required(CONF_PASSWORD): str,
        vol.Required(CONF_DISTANCE, default=10): vol.All(vol.Coerce(float), vol.Range(min=1.0, max=100.0)),
        vol.Required(CONF_LATITUDE): vol.All(str, validate_latitude),
        vol.Required(CONF_LONGITUDE): vol.All(str, validate_longitude)
    }
)

class ConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle a config flow for Gaspy."""

    VERSION = 1

    async def async_step_user(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        """Handle the initial step."""
        if user_input is None:
            return self.async_show_form(
                step_id="user", data_schema=STEP_USER_DATA_SCHEMA
            )

        await self.async_set_unique_id(user_input[CONF_USERNAME].lower())
        self._abort_if_unique_id_configured()

        return self.async_create_entry(title=user_input[CONF_USERNAME], data=user_input)
