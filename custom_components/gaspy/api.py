"""Gaspy API"""

import logging
import socket
from typing import Dict, List

import aiohttp
from yarl import URL

_LOGGER = logging.getLogger(__name__)
_BASE_URL = "https://gaspy.nz/api/v1/"


class GaspyApi:
    """Interface to Gaspy API."""

    def __init__(self, username, password, distance, latitude, longitude):
        self._username = username
        self._password = password
        self._distance = distance
        self._latitude = latitude
        self._longitude = longitude
        self._session = None
        self._url_base = _BASE_URL
        self._base_url = URL(_BASE_URL)
        self._is_logged_in = False
        self._stored_cookies: List[Dict[str, str]] = []

    async def _get_session(self) -> aiohttp.ClientSession:
        if self._session is None or self._session.closed:
            _LOGGER.debug(
                "Creating new long-lived API session with IPv4-only connector."
            )
            connector = aiohttp.TCPConnector(family=socket.AF_INET)
            self._session = aiohttp.ClientSession(connector=connector)
            self._restore_cookies(self._session)
        return self._session

    async def close(self) -> None:
        if self._session and not self._session.closed:
            await self._session.close()
            _LOGGER.debug("Managed API session closed.")
            self._session = None
            self._is_logged_in = False

    @property
    def is_logged_in(self):
        """Return True if currently logged in."""
        return self._is_logged_in

    async def get_prices(self):
        """Get fuel prices."""
        session = await self._get_session()
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
        async with session.post(
            self._url_base + "FuelPrice/searchFuelPrices", headers=headers, data=data
        ) as response:
            if response.status == 200:
                data = await response.json()
                if not data:
                    _LOGGER.warning("Fetched prices successfully, but did not find any")
                return data

            _LOGGER.error("Failed to fetch prices")
            return {"data": []}

    async def login(self):
        """Login to the Gaspy API."""
        result = False
        session = await self._get_session()

        # Initialise the cookie jar
        headers = {"user-agent": "okhttp/3.10.0"}
        async with session.get(
            self._url_base + "Public/init", headers=headers
        ) as init_result:
            if init_result.status == 200:
                # Attempt to login
                data = {"email": self._username, "password": self._password}
                async with session.post(
                    self._url_base + "Public/login", headers=headers, data=data
                ) as login_result:
                    if login_result.status == 200:
                        _LOGGER.debug("Successfully logged in")
                        self._snapshot_cookies()
                        self._is_logged_in = True
                        result = True
                    else:
                        _LOGGER.error("login failed: %s", 2)
                        self._stored_cookies = []
            else:
                _LOGGER.error("login failed: %s", 1)
                self._stored_cookies = []
        return result

    def _snapshot_cookies(self) -> None:
        """Persist cookies received during login for later reuse."""
        if not self._session:
            return

        cookies = self._session.cookie_jar.filter_cookies(str(self._base_url))
        snapshot: List[Dict[str, str]] = []
        for key, morsel in cookies.items():
            snapshot.append(
                {
                    "key": key,
                    "value": morsel.value,
                    "domain": morsel["domain"] or self._base_url.host,
                    "path": morsel["path"] or "/",
                }
            )

        self._stored_cookies = snapshot
        if snapshot:
            _LOGGER.debug("Cached %s login cookies for reuse.", len(snapshot))

    def _restore_cookies(self, session: aiohttp.ClientSession) -> None:
        """Reapply stored cookies to a new session before use."""
        if not self._stored_cookies:
            return

        for cookie in self._stored_cookies:
            cookie_url = URL.build(
                scheme=self._base_url.scheme,
                host=cookie.get("domain") or self._base_url.host,
                path=cookie.get("path") or "/",
            )
            session.cookie_jar.update_cookies(
                {cookie["key"]: cookie["value"]}, response_url=cookie_url
            )

        _LOGGER.debug(
            "Restored %s cached cookies into a refreshed API session.",
            len(self._stored_cookies),
        )
