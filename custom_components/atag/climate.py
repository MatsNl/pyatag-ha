"""Initialization of ATAG One climate platform."""
import logging
from homeassistant.components.climate.const import (
    STATE_AUTO, STATE_MANUAL, SUPPORT_TARGET_TEMPERATURE, SUPPORT_OPERATION_MODE)
#    , SUPPORT_TARGET_HUMIDITY_LOW,
#    SUPPORT_TARGET_HUMIDITY_HIGH)
from homeassistant.core import callback
from homeassistant.helpers.dispatcher import async_dispatcher_connect

from homeassistant.const import (TEMP_CELSIUS, ATTR_TEMPERATURE)

from homeassistant.components.climate import (ClimateDevice)
from homeassistant.components.climate.const import (ATTR_CURRENT_TEMPERATURE, ATTR_OPERATION_MODE,
                                                    DEFAULT_MAX_TEMP, DEFAULT_MIN_TEMP)

from homeassistant.util.temperature import convert as convert_temperature
from .const import (ATAG_HANDLE, DOMAIN, SIGNAL_UPDATE_ATAG)

SUPPORT_FLAGS = (SUPPORT_TARGET_TEMPERATURE | SUPPORT_OPERATION_MODE)  # |
#                 SUPPORT_TARGET_HUMIDITY_LOW | SUPPORT_TARGET_HUMIDITY_HIGH)

OPERATION_LIST = [STATE_MANUAL, STATE_AUTO]

_LOGGER = logging.getLogger(__name__)


async def async_setup_platform(hass, _config, async_add_devices,
                               _discovery_info=None):
    """Setup for the Atag One thermostat."""
    async_add_devices([AtagOneThermostat(hass)])


class AtagOneThermostat(ClimateDevice):  # pylint: disable=abstract-method
    """Representation of the ATAG One thermostat."""

    def __init__(self, hass):
        """Initialize"""
        _LOGGER.debug("Initializing Atag climate platform")
        self.atag = hass.data[DOMAIN][ATAG_HANDLE]
        self._name = 'Atag thermostat'
        #self._operation_list = [STATE_MANUAL, STATE_AUTO]
        _LOGGER.debug("Atag climate initialized")

    async def async_added_to_hass(self):
        """Register callbacks."""
        async_dispatcher_connect(
            self.hass, SIGNAL_UPDATE_ATAG, self._update_callback)

    @callback
    def _update_callback(self):
        """Call update method."""
        self.async_schedule_update_ha_state(True)

    @property
    def should_poll(self):
        """Polling needed for thermostat."""
        return False

    @property
    def supported_features(self):
        """Return the list of supported features."""
        return SUPPORT_FLAGS

    @property
    def name(self):
        """Return the name of the thermostat."""
        return self._name

    @property
    def temperature_unit(self):
        """Return the unit of measurement."""
        return TEMP_CELSIUS

    @property
    def current_temperature(self):
        """Return the current temperature."""
        if ATTR_CURRENT_TEMPERATURE in self.atag.sensordata:
            return self.atag.sensordata[ATTR_CURRENT_TEMPERATURE]
        return None

    @property
    def target_temperature(self):
        """Return the temperature we try to reach."""
        if ATTR_TEMPERATURE in self.atag.sensordata:
            return self.atag.sensordata[ATTR_TEMPERATURE]
        return None

    @property
    def current_operation(self):
        if ATTR_OPERATION_MODE in self.atag.sensordata:
            return self.atag.sensordata[ATTR_OPERATION_MODE]
        return None

    @property
    def operation_list(self):
        """List of available operation modes."""
        return OPERATION_LIST

    @property
    def max_temp(self):
        """Return the maximum temperature."""
        return convert_temperature(DEFAULT_MAX_TEMP, TEMP_CELSIUS,
                                   self.temperature_unit)

    @property
    def min_temp(self):
        """Return the maximum temperature."""
        return convert_temperature(DEFAULT_MIN_TEMP, TEMP_CELSIUS,
                                   self.temperature_unit)

    async def async_set_temperature(self, **kwargs):
        """Set new target temperature."""
        target_temp = kwargs.get(ATTR_TEMPERATURE)
        if target_temp is None:
            return
        await self.atag.async_set_atag(_target_temp=target_temp)

    async def async_set_operation_mode(self, operation_mode):
        """Set ATAG ONE mode (auto, manual)."""
        if operation_mode is None:
            return
        await self.atag.async_set_atag(_target_mode=operation_mode)
