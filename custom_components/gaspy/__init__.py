"""The Gaspy Fuel Price integration."""
from __future__ import annotations

import asyncio
import aiohttp
import logging

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.typing import ConfigType

from homeassistant.const import Platform
from homeassistant.helpers.aiohttp_client import async_create_clientsession
from homeassistant.exceptions import ConfigEntryNotReady
import async_timeout

from .api import GaspyApi

from .const import (
    DOMAIN,
    CONF_USERNAME,
    CONF_PASSWORD,
    CONF_DISTANCE,
    CONF_LATITUDE,
    CONF_LONGITUDE,
    PLATFORMS,
    STARTUP_MESSAGE
)

from .coordinator import GaspyDataUpdateCoordinator

_LOGGER = logging.getLogger(__name__)

async def async_setup(hass: HomeAssistant, config: ConfigType) -> bool:
    """Set up the Gaspy integration from yaml."""
    if DOMAIN not in config:
        return True

    # TODO: Setup yaml config flow

    return True

async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up Gaspy from a config entry."""
    if hass.data.get(DOMAIN) is None:
        hass.data.setdefault(DOMAIN, {})
        _LOGGER.info(STARTUP_MESSAGE)

    username = entry.data.get(CONF_USERNAME)
    password = entry.data.get(CONF_PASSWORD)
    distance = entry.data.get(CONF_DISTANCE)
    latitude = entry.data.get(CONF_LATITUDE)
    longitude = entry.data.get(CONF_LONGITUDE)

    session = async_create_clientsession(hass)
    api = GaspyApi(username, password, distance, latitude, longitude, session)

    try:
        async with async_timeout.timeout(10):
            if not await api.login():
                _LOGGER.error("Invalid credentials")
                return False
    except (
        asyncio.TimeoutError
    ) as err:
        raise ConfigEntryNotReady from err

    coordinator = GaspyDataUpdateCoordinator(hass, api=api)

    hass.data[DOMAIN][entry.entry_id] = coordinator

    await coordinator.async_config_entry_first_refresh()

    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)
    entry.async_on_unload(entry.add_update_listener(async_reload_entry))

    return True


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload a config entry."""
    if unload_ok := await hass.config_entries.async_unload_platforms(entry, PLATFORMS):
        hass.data[DOMAIN].pop(entry.entry_id)

    return unload_ok


async def async_reload_entry(hass: HomeAssistant, entry: ConfigEntry) -> None:
    """Reload config entry."""
    await async_unload_entry(hass, entry)
    await async_setup_entry(hass, entry)
