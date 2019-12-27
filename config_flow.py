"""Config flow for the Atag component."""
import logging
from pyatag import AtagDataStore, AtagException, discover_atag
import asyncio
from async_timeout import timeout

import voluptuous as vol

from homeassistant.helpers.dispatcher import async_dispatcher_connect

from homeassistant import config_entries
from homeassistant.helpers import config_validation as cv, config_entry_flow
from homeassistant.const import (
    CONF_DEVICE,
    CONF_EMAIL,
    CONF_HOST,
    CONF_PORT,
    CONF_SENSORS,
    CONF_SCAN_INTERVAL,
)
from homeassistant.core import callback, HomeAssistant

from .const import *

# from .const import (
#    DOMAIN,
#    DEFAULT_SENSORS,
#    DEFAULT_SCAN_INTERVAL,
# )

_LOGGER = logging.getLogger(__name__)

DATA_SCHEMA = {vol.Optional(CONF_HOST): str, vol.Optional(CONF_EMAIL): str}

FULL_SCHEMA = vol.Schema(
    {
        DOMAIN: vol.Schema(
            {
                vol.Optional(CONF_HOST): cv.string,
                vol.Optional(CONF_EMAIL): cv.string,
                vol.Optional(CONF_PORT): cv.port,
                vol.Optional(
                    CONF_SCAN_INTERVAL, default=DEFAULT_SCAN_INTERVAL
                ): cv.positive_int,
                vol.Optional(CONF_SENSORS, default=DEFAULT_SENSORS): vol.All(
                    cv.ensure_list, [vol.In(DEFAULT_SENSORS)]
                ),
            }
        )
    },
    extra=vol.ALLOW_EXTRA,
)


@callback
def configured_hosts(hass: HomeAssistant):
    """Return a set of the configured hosts."""
    return set(
        (entry.data[CONF_DEVICE], entry.data[CONF_HOST])
        for entry in hass.config_entries.async_entries(DOMAIN)
    )


async def _async_has_devices(hass):
    try:
        devices = await discover_atag()
    except AtagException:
        return False
    return len(devices)


config_entry_flow.register_discovery_flow(
    DOMAIN, "atag", _async_has_devices, config_entries.CONN_CLASS_LOCAL_POLL
)
