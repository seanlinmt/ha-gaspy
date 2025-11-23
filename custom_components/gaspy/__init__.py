"""Support for Gaspy sensors"""

from homeassistant import config_entries, core


async def async_setup(hass: core.HomeAssistant, config: dict) -> bool:
    """Set up the Gaspy component."""
    return True


async def async_setup_entry(
    hass: core.HomeAssistant, entry: config_entries.ConfigEntry
) -> bool:
    """Set up Gaspy from a config entry."""
    await hass.config_entries.async_forward_entry_setups(entry, ["sensor"])

    return True


async def async_unload_entry(
    hass: core.HomeAssistant, entry: config_entries.ConfigEntry
) -> bool:
    """Unload a config entry."""
    return await hass.config_entries.async_forward_entry_unload(entry, "sensor")
