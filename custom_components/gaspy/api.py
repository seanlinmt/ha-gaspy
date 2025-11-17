"""Gaspy API"""
import asyncio
import socket
from typing import Any, Dict, Optional, Union
import aiohttp
import async_timeout

from .const import LOGGER

class GaspyApiError(Exception):
    """Exception to indicate a general API error."""

class GaspyApiAuthenticationError(GaspyApiError):
    """Exception to indicate an authentication error."""

class GaspyApi:
    def __init__(self, username, password, distance, latitude, longitude, session: aiohttp.ClientSession):
        self._username = username
        self._password = password
        self._distance = distance
        self._latitude = latitude
        self._longitude = longitude
        self._session = session
        self._url_base = 'https://gaspy.nz/api/v1/'

    async def login(self) -> bool:
        """Login to the Gaspy API."""
        # Initialise the cookie jar
        headers = {
            "user-agent": "okhttp/3.10.0"
        }

        await self.async_request(
            "get",
            self._url_base + "Public/init",
            headers,
            None
        )

        data = {
            "email": self._username,
            "password": self._password
        }

        response = await self.async_request(
            "post",
            self._url_base + "Public/login",
            headers,
            data
        )

        return isinstance(response, dict) and "id" in response

    async def get_prices(self) -> Dict[str, Any]:
        """Get fuel prices from the API."""
        headers = {
            "user-agent": "okhttp/3.10.0"
        }
        data = {
            'device_type': 'A',
            'distance': self._distance,
            'fuel_type_id': 3,
            'is_mock_location': 'false',
            'latitude': self._latitude,
            'longitude': self._longitude,
            'order_by': 'price',
            'start': '0'
        }
        
        response = await self.async_request(
            "post",
            self._url_base + "FuelPrice/searchFuelPrices",
            headers,
            data
        )
        
        if not isinstance(response, dict) or not response.get('data'):
            LOGGER.warning('Fetched prices successfully, but did not find any')
            
        return response

    async def async_request(
        self, 
        method: str, 
        url: str, 
        headers: Dict[str, str], 
        data: Optional[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Make a request to the API."""
        try:
            async with async_timeout.timeout(10):
                response = await self._session.request(
                    method=method,
                    url=url,
                    headers=headers,
                    json=data,
                )
                if response.status in (401, 403):
                    raise GaspyApiAuthenticationError(
                        "Invalid credentials",
                    )
                response.raise_for_status()
                return await response.json()
        except asyncio.TimeoutError as exception:
            raise GaspyApiError(
                "Timeout error fetching information",
            ) from exception
        except (aiohttp.ClientError, socket.gaierror) as exception:
            raise GaspyApiError(
                "Error fetching information",
            ) from exception
        except Exception as exception:
            LOGGER.error(f"Something really wrong happened! - {exception}")
            raise exception from exception
