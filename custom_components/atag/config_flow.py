"""Config flow for the Atag component."""
import logging
from pyatag.errors import AtagException
from pyatag.gateway import AtagDataStore
import voluptuous as vol

from homeassistant import config_entries
from homeassistant.helpers import config_validation as cv
from homeassistant.const import (
    CONF_DEVICE,
    CONF_EMAIL,
    CONF_HOST,
    CONF_PORT,
    CONF_SENSORS,
    CONF_SCAN_INTERVAL,
)
from homeassistant.core import callback, HomeAssistant

from .const import (
    DOMAIN,
    DEFAULT_PORT,
    DEFAULT_SENSORS,
    DEFAULT_SCAN_INTERVAL,
)

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


class AtagConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Config flow for Atag."""

    VERSION = 1
    CONNECTION_CLASS = config_entries.CONN_CLASS_LOCAL_POLL

    async def async_step_user(self, user_input=None):
        """Handle a flow initialized by the user."""

        if self._async_current_entries():
            return self.async_abort(reason="already_configured")

        if not user_input:
            return await self._show_form()

        host = user_input[CONF_HOST]
        email = user_input.get(CONF_EMAIL, None)
        port = user_input.get(CONF_PORT, DEFAULT_PORT)
        scan_interval = user_input.get(CONF_SCAN_INTERVAL, DEFAULT_SCAN_INTERVAL)
        sensors = user_input.get(CONF_SENSORS, DEFAULT_SENSORS)

        try:
            atag = AtagDataStore(host=host, port=port, mail=email)
            await atag.async_check_pair_status()
            await atag.async_close()

        except AtagException:
            return self._show_form({"base": "connection_error"})

        if atag.device in configured_hosts(self.hass):
            return self._show_form({"base": "identifier_exists"})

        return self.async_create_entry(
            title=atag.device,
            data={
                CONF_DEVICE: atag.device,
                CONF_HOST: host,
                CONF_PORT: port,
                CONF_EMAIL: email,
                CONF_SCAN_INTERVAL: scan_interval,
                CONF_SENSORS: sensors,
            },
        )

    @callback
    async def _show_form(self, errors=None):
        """Show the form to the user."""
        return self.async_show_form(
            step_id="user",
            data_schema=vol.Schema(DATA_SCHEMA),
            errors=errors if errors else {},
        )

    async def async_step_import(self, import_config):
        """Import a config entry from configuration.yaml."""
        if self._async_current_entries():
            return self.async_abort(reason="already_configured")

        return await self.async_step_user(import_config)
