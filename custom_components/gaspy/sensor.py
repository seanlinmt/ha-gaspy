"""Gaspy sensors."""

from datetime import timedelta
import logging

import voluptuous as vol

from homeassistant.components.sensor import PLATFORM_SCHEMA as SENSOR_PLATFORM_SCHEMA
import homeassistant.helpers.config_validation as cv
from homeassistant.helpers.entity import Entity

from .api import GaspyApi
from .const import (
    CONF_DISTANCE,
    CONF_LATITUDE,
    CONF_LONGITUDE,
    CONF_PASSWORD,
    CONF_USERNAME,
    DOMAIN,
    SENSOR_NAME,
)

_LOGGER = logging.getLogger(__name__)

SENSOR_PLATFORM_SCHEMA = SENSOR_PLATFORM_SCHEMA.extend(
    {
        vol.Required(CONF_USERNAME): cv.string,
        vol.Required(CONF_PASSWORD): cv.string,
        vol.Required(CONF_DISTANCE): vol.All(
            vol.Coerce(float), vol.Range(min=1.0, max=100.0)
        ),
        vol.Required(CONF_LATITUDE): cv.string,
        vol.Required(CONF_LONGITUDE): cv.string,
    }
)

SCAN_INTERVAL = timedelta(minutes=60)


async def async_setup_platform(hass, config, async_add_entities, discovery_info=None):
    username = config.get(CONF_USERNAME)
    password = config.get(CONF_PASSWORD)
    distance = config.get(CONF_DISTANCE)
    latitude = config.get(CONF_LATITUDE)
    longitude = config.get(CONF_LONGITUDE)

    api = GaspyApi(username, password, distance, latitude, longitude)

    _LOGGER.debug("Setting up sensor(s)")

    sensors = []
    sensors.append(GaspyFuelPriceSensor(SENSOR_NAME, api))
    async_add_entities(sensors, True)


async def async_setup_entry(hass, entry, async_add_entities):
    """Set up Gaspy from a config entry."""
    config = entry.data
    username = config.get(CONF_USERNAME)
    password = config.get(CONF_PASSWORD)
    distance = config.get(CONF_DISTANCE)
    latitude = config.get(CONF_LATITUDE)
    longitude = config.get(CONF_LONGITUDE)

    api = GaspyApi(username, password, distance, latitude, longitude)

    _LOGGER.debug("Setting up sensor(s) from config entry")

    sensors = []
    sensors.append(GaspyFuelPriceSensor(SENSOR_NAME, api))
    async_add_entities(sensors, True)


class GaspyFuelPriceSensor(Entity):
    """Representation of a Gaspy Sensor."""

    def __init__(self, name, api):
        self._name = name
        self._icon = "mdi:gas-station"
        self._state = ""
        self._state_attributes = {}
        self._state_class = "measurement"
        self._unit_of_measurement = "$"
        self._unit_of_measurement = "$"
        self._unique_id = f"{DOMAIN}_{api._latitude}_{api._longitude}"
        self._api = api

    @property
    def name(self):
        """Return the name of the sensor."""
        return self._name

    @property
    def icon(self):
        """Icon to use in the frontend, if any."""
        return self._icon

    @property
    def state(self):
        """Return the state of the device."""
        return self._state

    @property
    def state_class(self):
        """Return the state class of the device."""
        return self._state_class

    @property
    def extra_state_attributes(self):
        """Return the state attributes of the sensor."""
        return self._state_attributes

    @property
    def unit_of_measurement(self):
        """Return the unit of measurement."""
        return self._unit_of_measurement

    @property
    def unique_id(self):
        """Return the unique id."""
        return self._unique_id

    def update(self):
        """Update the sensor."""
        _LOGGER.debug("Checking login validity")
        if self._api.is_logged_in or self._api.login():
            # Get todays date
            _LOGGER.debug("Fetching prices")
            response = self._api.get_prices()
            if response["data"]:
                _LOGGER.debug(response["data"])
                for station in response["data"]:
                    # Avoid updating the price (state) if the price is still the same
                    # or we will get duplicate notifications
                    if self._state == float(station["current_price"]) / 100:
                        break

                    self._state = float(station["current_price"]) / 100

                    self._state_attributes["Fuel Type Name"] = station["fuel_type_name"]
                    self._state_attributes["Station Name"] = station["station_name"]
                    self._state_attributes["Distance"] = station["distance"]
                    self._state_attributes["Last Updated"] = station["date_updated"]

                    # Because we are ordering by lowest price in the API call,
                    # to get the lowest price we only ever need the first result
                    break
            else:
                self._state = "None"
                _LOGGER.debug("Found no prices on refresh")
        else:
            _LOGGER.error("Unable to log in")
