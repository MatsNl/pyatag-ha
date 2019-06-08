"""Integrate ATAG One in Homeassistant."""
from datetime import datetime, timedelta, timezone
import json
import logging
import voluptuous as vol

import homeassistant.helpers.config_validation as cv
from homeassistant.helpers.discovery import async_load_platform
from homeassistant.helpers.dispatcher import async_dispatcher_send
from homeassistant.helpers.event import async_track_time_interval
from homeassistant.const import (CONF_HOST, CONF_PORT, CONF_EMAIL, CONF_SCAN_INTERVAL,
                                 CONF_SENSORS, EVENT_HOMEASSISTANT_STOP)
from homeassistant.core import callback, asyncio

from .const import (DOMAIN, ATAG_HANDLE, SIGNAL_UPDATE_ATAG,
                    DATA_LISTENER, DEFAULT_PORT, DEFAULT_SENSORS,
                    CONF_INTERFACE, DEFAULT_INTERFACE)

VERSION = '0.2.4'

DEFAULT_SCAN_INTERVAL = 30
_LOGGER = logging.getLogger(__name__)

CONFIG_SCHEMA = vol.Schema({
    DOMAIN: vol.Schema({
        vol.Optional(CONF_HOST): cv.string,
        vol.Optional(CONF_EMAIL): cv.string,
        vol.Optional(CONF_PORT, default=DEFAULT_PORT): cv.port,
        vol.Optional(CONF_INTERFACE): cv.string,
        vol.Optional(CONF_SCAN_INTERVAL, default=DEFAULT_SCAN_INTERVAL):
            cv.time_period_seconds,
        vol.Optional(CONF_SENSORS, default=DEFAULT_SENSORS):
            vol.All(cv.ensure_list, [vol.In(DEFAULT_SENSORS)]),
    }),
}, extra=vol.ALLOW_EXTRA)

async def async_setup(hass, config):
    """Iniatilize ATAG Component"""
    conf = config[DOMAIN]
    hass.data[DOMAIN] = {}
    host = conf.get(CONF_HOST)
    email = conf.get(CONF_EMAIL)
    interface = conf.get(CONF_INTERFACE)
    port = conf.get(CONF_PORT)
    scan_interval = conf.get(CONF_SCAN_INTERVAL)
    sensors = conf.get(CONF_SENSORS)
    httpsession = hass.helpers.aiohttp_client.async_get_clientsession()

    _LOGGER.debug('Initializing ATAG...')
    from pyatag.gateway import AtagDataStore
    atagunit = AtagDataStore(
        host=host, port=port, mail=email, interface=interface, session=httpsession)

    hass.data[DOMAIN][ATAG_HANDLE] = atagunit
    _LOGGER.debug('Datastore initialized')
    for platform in ('sensor', 'climate'):
        hass.async_create_task(
            async_load_platform(hass, platform, DOMAIN, {
                                'sensors': sensors}, config)
        )

    async def async_hub_refresh(event_time):  # pylint: disable=unused-argument
        """Call Atag to refresh information."""
        #_LOGGER.debug("Updating Atag component")
        await hass.data[DOMAIN][ATAG_HANDLE].async_update()
        async_dispatcher_send(hass, SIGNAL_UPDATE_ATAG)

    async def async_close_atag(event):  # pylint: disable=unused-argument
        """Close Atag connection on HA Stop."""
        await hass.data[DOMAIN][ATAG_HANDLE].async_close()

    hass.services.async_register(DOMAIN, 'update', async_hub_refresh)
    hass.bus.async_listen_once(EVENT_HOMEASSISTANT_STOP, async_close_atag)

    hass.data[DOMAIN][DATA_LISTENER] = async_track_time_interval(
        hass, async_hub_refresh, scan_interval)
    return True
