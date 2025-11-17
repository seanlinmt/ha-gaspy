"""Gaspy sensors"""
from __future__ import annotations

from homeassistant.components.sensor import (
    SensorDeviceClass,
    SensorEntity,
    SensorStateClass,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import (
    CoordinatorEntity,
)

from .const import (
    DOMAIN,
    NAME
)

from .coordinator import GaspyDataUpdateCoordinator

async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up the Gaspy sensor."""
    coordinator = hass.data[DOMAIN][entry.entry_id]
    async_add_entities(
        [
            GaspyFuelPriceSensor(coordinator, entry),
        ]
    )


class GaspyFuelPriceSensor(CoordinatorEntity, SensorEntity):
    """Gaspy Fuel Price Sensor."""

    _attr_has_entity_name = True

    def __init__(
        self,
        coordinator: GaspyDataUpdateCoordinator,
        entry: ConfigEntry,
    ) -> None:
        """Initialize the sensor."""
        super().__init__(coordinator)
        self._entry = entry
        self._attr_device_class = SensorDeviceClass.MONETARY
        self._attr_state_class = SensorStateClass.MEASUREMENT
        self._attr_native_unit_of_measurement = '$'
        self._attr_unique_id = f"{entry.entry_id}_fuel_price"
        self._attr_name = f"{NAME} Fuel Price"
        self._attr_icon = "mdi:gas-station"

    @property
    def native_value(self):
        """Return the state of the sensor."""
        if self.coordinator.data and self.coordinator.data.get('data'):
            lowest_price_station = min(self.coordinator.data['data'], key=lambda x: x['current_price'])
            return float(lowest_price_station['current_price']) / 100
        return None

    @property
    def extra_state_attributes(self):
        """Return the state attributes of the sensor."""
        if self.coordinator.data and self.coordinator.data.get('data'):
            lowest_price_station = min(self.coordinator.data['data'], key=lambda x: x['current_price'])
            return {
                'Fuel Type Name': lowest_price_station['fuel_type_name'],
                'Station Name': lowest_price_station['station_name'],
                'Distance': lowest_price_station['distance'],
                'Last Updated': lowest_price_station['date_updated']
            }
        return {}
