"""Constants for the Gaspy sensors"""
import logging
from typing import Final

from homeassistant.const import Platform

LOGGER: Final = logging.getLogger(__name__)

# Basic information about the integration
DOMAIN: Final = "gaspy"
NAME: Final = "Gaspy"
ISSUEURL: Final = "https://github.com/seanlinmt/hacs_gaspy/issues"

# Platforms
PLATFORMS: Final = [Platform.SENSOR]

# Configuration and options
CONF_USERNAME: Final = "username"
CONF_PASSWORD: Final = "password"
CONF_LATITUDE: Final = "latitude"
CONF_LONGITUDE: Final = "longitude"
CONF_DISTANCE: Final = "distance"

# Defaults
DEFAULT_NAME: Final = DOMAIN

STARTUP_MESSAGE: Final = f"""
-------------------------------------------------------------------
{NAME}
This is a custom component
If you have any issues with this you need to open an issue here:
{ISSUEURL}
-------------------------------------------------------------------
"""
