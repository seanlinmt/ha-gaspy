"""Gaspy API"""

import logging
import requests

_LOGGER = logging.getLogger(__name__)


class GaspyApi:
    """Interface to Gaspy API."""

    def __init__(self, username, password, distance, latitude, longitude):
        self._username = username
        self._password = password
        self._distance = distance
        self._latitude = latitude
        self._longitude = longitude
        self._session = requests.Session()
        self._url_base = "https://gaspy.nz/api/v1/"

    def get_prices(self):
        """Get fuel prices."""
        headers = {"user-agent": "okhttp/3.10.0"}
        data = {
            "device_type": "A",
            "distance": self._distance,
            "fuel_type_id": 3,
            "is_mock_location": "false",
            "latitude": self._latitude,
            "longitude": self._longitude,
            "order_by": "price",
            "start": "0",
        }
        response = self._session.post(
            self._url_base + "FuelPrice/searchFuelPrices", headers=headers, data=data
        )

        if response.status_code == requests.codes.ok:
            data = response.json()
            if not data:
                _LOGGER.warning("Fetched prices successfully, but did not find any")
            return data

        _LOGGER.error("Failed to fetch prices")
        return {"data": []}

    def login(self):
        """Login to the Gaspy API."""
        result = False

        # Initialise the cookie jar
        headers = {"user-agent": "okhttp/3.10.0"}
        init_result = self._session.get(self._url_base + "Public/init", headers=headers)

        if init_result.status_code == requests.codes.ok:
            # Attempt to login
            data = {"email": self._username, "password": self._password}
            login_result = self._session.post(
                self._url_base + "Public/login", headers=headers, data=data
            )

            if login_result.status_code == requests.codes.ok:
                _LOGGER.debug("Successfully logged in")
                # self.get_prices()
                result = True
            else:
                _LOGGER.error("login failed: %s", 2)
        else:
            _LOGGER.error("login failed: %s", 1)
        return result
