"""Config flow for Gaspy integration."""

import logging
import voluptuous as vol

from homeassistant import config_entries, core, exceptions
from homeassistant.const import (
    CONF_USERNAME,
    CONF_PASSWORD,
    CONF_LATITUDE,
    CONF_LONGITUDE,
)
from .const import DOMAIN, CONF_DISTANCE
from .api import GaspyApi

_LOGGER = logging.getLogger(__name__)

DATA_SCHEMA = vol.Schema(
    {
        vol.Required(CONF_USERNAME): str,
        vol.Required(CONF_PASSWORD): str,
        vol.Required(CONF_DISTANCE, default=15): int,
        vol.Required(CONF_LATITUDE): float,
        vol.Required(CONF_LONGITUDE): float,
    }
)


async def validate_input(hass: core.HomeAssistant, data):
    """Validate the user input allows us to connect.

    Data has the keys from DATA_SCHEMA with values provided by the user.
    """
    api = GaspyApi(
        data[CONF_USERNAME],
        data[CONF_PASSWORD],
        data[CONF_DISTANCE],
        data[CONF_LATITUDE],
        data[CONF_LONGITUDE],
    )

    result = await api.login()

    if not result:
        raise InvalidAuth

    return {"title": "Gaspy"}


class GaspyConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle a config flow for Gaspy."""

    VERSION = 1

    async def async_step_user(self, user_input=None):
        """Handle the initial step."""
        errors = {}
        if user_input is not None:
            try:
                info = await validate_input(self.hass, user_input)

                return self.async_create_entry(title=info["title"], data=user_input)
            except InvalidAuth:
                errors["base"] = "invalid_auth"
            except Exception:  # pylint: disable=broad-except
                _LOGGER.exception("Unexpected exception")
                errors["base"] = "unknown"

        return self.async_show_form(
            step_id="user", data_schema=DATA_SCHEMA, errors=errors
        )


class InvalidAuth(exceptions.HomeAssistantError):
    """Error to indicate there is invalid auth."""
