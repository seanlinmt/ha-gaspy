"""DataUpdateCoordinator for Gaspy."""
from __future__ import annotations

from datetime import timedelta

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.update_coordinator import (
    DataUpdateCoordinator,
    UpdateFailed,
)
from homeassistant.exceptions import ConfigEntryAuthFailed

from .api import (
    GaspyApi,
    GaspyApiAuthenticationError,
    GaspyApiError,
)
from .const import DOMAIN, LOGGER


class GaspyDataUpdateCoordinator(DataUpdateCoordinator):
    """Class to manage fetching data from the API."""

    config_entry: ConfigEntry

    def __init__(
        self,
        hass: HomeAssistant,
        api: GaspyApi,
    ) -> None:
        """Initialize."""
        self.api = api
        super().__init__(
            hass,
            LOGGER,
            name=DOMAIN,
            update_interval=timedelta(minutes=5),
        )

    async def _async_update_data(self):
        """Update data via library."""
        try:
            return await self.api.get_prices()
        except GaspyApiAuthenticationError as exception:
            raise ConfigEntryAuthFailed(exception) from exception
        except GaspyApiError as exception:
            raise UpdateFailed(exception) from exception
