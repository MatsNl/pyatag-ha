"""Integrate ATAG One in Homeassistant."""
from datetime import datetime, timedelta, timezone
import logging
import voluptuous as vol
from pyatag.gateway import AtagDataStore
from pyatag.const import SENSOR_TYPES
from requests.exceptions import ConnectTimeout, HTTPError

from homeassistant.core import callback, asyncio
from homeassistant.config_entries import SOURCE_IMPORT
from homeassistant.helpers.entity import Entity
from homeassistant.exceptions import ConfigEntryNotReady
from homeassistant.helpers import config_validation as cv, device_registry as dr
from homeassistant.helpers.discovery import async_load_platform
from homeassistant.helpers.aiohttp_client import async_get_clientsession
from homeassistant.helpers.event import async_track_time_interval
from homeassistant.helpers.dispatcher import (
    async_dispatcher_send,
    async_dispatcher_connect,
)
from homeassistant.const import (
    CONF_HOST,
    CONF_PORT,
    CONF_EMAIL,
    CONF_SCAN_INTERVAL,
    CONF_SENSORS,
    EVENT_HOMEASSISTANT_STOP,
)

from .config_flow import configured_hosts, AtagFlowHandler  # noqa
from .const import (
    DEVICEID,
    DOMAIN,  # noqa
    DEFAULT_SCAN_INTERVAL,
    ATAG_HANDLE,
    SIGNAL_UPDATE_ATAG,
    DATA_LISTENER,
    DEFAULT_PORT,
    DEFAULT_SENSORS,
    CONF_INTERFACE,
    PROJECT_URL,
)

VERSION = "0.2.9.1"
PLATFORMS = ["sensor", "climate", "water_heater"]
_LOGGER = logging.getLogger(__name__)

CONFIG_SCHEMA = vol.Schema(
    {
        DOMAIN: vol.Schema(
            {
                vol.Optional(CONF_HOST): cv.string,
                vol.Optional(CONF_EMAIL): cv.string,
                vol.Optional(CONF_PORT, default=DEFAULT_PORT): cv.port,
                vol.Optional(CONF_INTERFACE): cv.string,
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


async def async_setup(hass, config):
    """Set up the Atag component."""

    if DOMAIN not in config:
        return True

    conf = config[DOMAIN]

    if any(conf[CONF_HOST] in host for host in configured_hosts(hass)):
        return True

    hass.async_create_task(
        hass.config_entries.flow.async_init(
            DOMAIN, context={"source": SOURCE_IMPORT}, data=conf
        )
    )

    return True


async def async_setup_entry(hass, entry):
    """Set up Atag integration from a config entry."""
    device = entry.data.get(DEVICEID)
    host = entry.data.get(CONF_HOST)
    _LOGGER.debug("Loading config entry for %s", (device, host))
    email = entry.data.get(CONF_EMAIL)
    interface = entry.data.get(CONF_INTERFACE)
    port = entry.data.get(CONF_PORT)
    session = async_get_clientsession(hass)
    try:
        atag = AtagDataStore(session, host, port, email, interface)
        if not await atag.async_check_pair_status():
            raise ConfigEntryNotReady
        await atag.async_update()
        if not atag.sensordata:
            raise ConfigEntryNotReady
    except (ConnectTimeout, HTTPError):
        raise ConfigEntryNotReady
    hass.data.setdefault(DOMAIN, {}).setdefault(ATAG_HANDLE, {})[entry.entry_id] = atag

    device_registry = await dr.async_get_registry(hass)
    device_registry.async_get_or_create(
        config_entry_id=entry.entry_id,
        identifiers={(DOMAIN, entry.data[DEVICEID], entry.data[CONF_HOST])},
        manufacturer=PROJECT_URL,
        name="Atag Thermostat",
        model="Atag One",
        sw_version=atag.sensordata["download_url"].split("/")[-1],
    )

    _LOGGER.debug("Adding platforms")
    for platform in PLATFORMS:
        hass.async_create_task(
            hass.config_entries.async_forward_entry_setup(entry, platform)
        )

    async def refresh(event_time):
        """Poll Atag for latest data"""
        _LOGGER.debug("Updating Atag data")
        await atag.async_update()
        async_dispatcher_send(hass, SIGNAL_UPDATE_ATAG)

    hass.data.setdefault(DOMAIN, {}).setdefault(DATA_LISTENER, {})[
        entry.entry_id
    ] = async_track_time_interval(
        hass, refresh, timedelta(seconds=DEFAULT_SCAN_INTERVAL)
    )

    #hass.services.async_register(DOMAIN, "update", refresh)
    return True


async def async_unload_entry(hass, entry):
    """Unload Atag config entry."""
    remove_listener = hass.data[DOMAIN][DATA_LISTENER].pop(entry.entry_id)
    remove_listener()
    unload_ok = all(
        await asyncio.gather(
            *[
                hass.config_entries.async_forward_entry_unload(entry, component)
                for component in PLATFORMS
            ]
        )
    )
    if unload_ok:
        hass.data[DOMAIN][ATAG_HANDLE].pop(entry.entry_id)
    # await hass.data[DOMAIN][ATAG_HANDLE][config_entry.entry_id].async_close()
    return unload_ok


class AtagEntity(Entity):
    """Defines a base Atag entity."""

    def __init__(self, atag: AtagDataStore, atagtype: str) -> None:
        """Initialize the Atag entity."""
        sensortype = SENSOR_TYPES.get(atagtype)
        if sensortype is not None:
            self._type = sensortype[0]
            self._unit = sensortype[1]
            self._icon = sensortype[2]
            self._datafield = sensortype[3]
            self._state = None
        else:
            self._type = atagtype

        self._name = " ".join([DOMAIN.title(), self._type])
        self.atag = atag
        self._unsub_dispatcher = None

    @property
    def device_info(self):
        """Return info for device registry"""
        device = self.atag.sensordata.get(DEVICEID)
        host = self.atag.host_config[CONF_HOST]
        version = self.atag.sensordata.get("download_url").split("/")[-1]
        return {
            "identifiers": {(DOMAIN, device, host)},
            "name": "Atag Thermostat",
            "model": "Atag One",
            "sw_version": version,
            "manufacturer": PROJECT_URL,
        }

    @property
    def name(self) -> str:
        """Return the name of the entity."""
        return self._name

    @property
    def icon(self) -> str:
        """Return the mdi icon of the entity."""
        if hasattr(self, '_icon'):
            return self._icon

    @property
    def should_poll(self) -> bool:
        """Return the polling requirement of the entity."""
        return False

    async def async_added_to_hass(self) -> None:
        """Connect to dispatcher listening for entity data notifications."""
        self._unsub_dispatcher = async_dispatcher_connect(
            self.hass, SIGNAL_UPDATE_ATAG, self._update_callback
        )

    async def async_will_remove_from_hass(self) -> None:
        """Disconnect from update signal."""
        self._unsub_dispatcher()

    @callback
    def _update_callback(self) -> None:
        """Schedule an immediate update of the entity."""
        self.async_schedule_update_ha_state(True)

    @property
    def unique_id(self):
        """Return a unique ID to use for this entity."""
        return '-'.join([DOMAIN.title(),self._type,self.atag.sensordata.get(DEVICEID)])
