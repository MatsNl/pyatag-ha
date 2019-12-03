"""Config flow for the Atag component."""
import logging
from pyatag.gateway import AtagDataStore
from requests.exceptions import ConnectTimeout, HTTPError
import voluptuous as vol

from homeassistant import config_entries
from homeassistant.helpers.aiohttp_client import async_get_clientsession
from homeassistant.const import (
    CONF_EMAIL,
    CONF_HOST,
    CONF_PORT,
    CONF_SENSORS,
    CONF_SCAN_INTERVAL,
)
from homeassistant.core import callback

from .const import (
    DEVICEID,
    DOMAIN,
    CONF_INTERFACE,
    DEFAULT_PORT,
    DEFAULT_SENSORS,
    DEFAULT_SCAN_INTERVAL,
)  # pylint: disable=W0611

_LOGGER = logging.getLogger(__name__)


@callback
def configured_hosts(hass):
    """Return a set of the configured hosts."""
    return set(
        (entry.data[DEVICEID], entry.data[CONF_HOST])
        for entry in hass.config_entries.async_entries(DOMAIN)
    )


@config_entries.HANDLERS.register(DOMAIN)
class AtagFlowHandler(config_entries.ConfigFlow):
    """Config flow for Atag."""

    VERSION = 1
    CONNECTION_CLASS = config_entries.CONN_CLASS_LOCAL_POLL

    def __init__(self):
        """Initialize."""
        self.data_schema = {vol.Optional(CONF_HOST): str, vol.Optional(CONF_EMAIL): str}

    async def async_step_user(self, user_input=None):
        """Handle a flow initialized by the user."""

        if self._async_current_entries():
            return self.async_abort(reason="single_instance_allowed")

        if not user_input:
            return await self._show_form()

        _LOGGER.debug("Configuring atag with config: %s", str(user_input))
        host = user_input[CONF_HOST]
        email = user_input[CONF_EMAIL]
        port = user_input.get(CONF_PORT, DEFAULT_PORT)
        interface = user_input.get(CONF_INTERFACE)
        scan_interval = user_input.get(CONF_SCAN_INTERVAL, DEFAULT_SCAN_INTERVAL)
        sensors = user_input.get(CONF_SENSORS, DEFAULT_SENSORS)

        session = async_get_clientsession(self.hass)
        try:
            _LOGGER.debug("Testing connection..")
            atag = AtagDataStore(session, host, port, email, None)
            await atag.async_update()

        except (ConnectTimeout, HTTPError) as ex:
            _LOGGER.error("Unable to connect to Atag: %s", str(ex))
            return self._show_form({"base": "connection_error"})

        if atag.sensordata[DEVICEID] in configured_hosts(self.hass):
            _LOGGER.error(
                "Device %s already added to Homeassistant",
                str(atag.sensordata[DEVICEID]),
            )
            return self._show_form({"base": "identifier_exists"})

        return self.async_create_entry(
            title=atag.sensordata[DEVICEID],
            data={
                DEVICEID: atag.sensordata[DEVICEID],
                CONF_HOST: host,
                CONF_PORT: port,
                CONF_EMAIL: email,
                CONF_INTERFACE: interface,
                CONF_SCAN_INTERVAL: scan_interval,
                CONF_SENSORS: sensors,
            },
        )

    @callback
    async def _show_form(self, errors=None):
        """Show the form to the user."""
        return self.async_show_form(
            step_id="user",
            data_schema=vol.Schema(self.data_schema),
            errors=errors if errors else {},
        )

    async def async_step_import(self, import_config):
        """Import a config entry from configuration.yaml."""
        if self._async_current_entries():
            return self.async_abort(reason="single_instance_allowed")

        return await self.async_step_user(import_config)
