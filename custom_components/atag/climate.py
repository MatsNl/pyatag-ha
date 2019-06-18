"""Initialization of ATAG One climate platform."""
import logging
from homeassistant.components.climate import (ClimateDevice)
from homeassistant.components.climate.const import (
    STATE_HEAT, STATE_AUTO, # , STATE_MANUAL,
    SUPPORT_TARGET_TEMPERATURE, SUPPORT_OPERATION_MODE,
    ATTR_CURRENT_TEMPERATURE, ATTR_OPERATION_MODE,
    DEFAULT_MIN_TEMP, DEFAULT_MAX_TEMP)
from homeassistant.const import (TEMP_CELSIUS, ATTR_TEMPERATURE, STATE_OFF)

from homeassistant.core import callback
from homeassistant.helpers.dispatcher import async_dispatcher_connect
from homeassistant.util.temperature import convert as convert_temperature

from .const import (ATAG_HANDLE, DOMAIN, SIGNAL_UPDATE_ATAG)

# STATE_EXTEND = 'extend'

SUPPORT_FLAGS = (SUPPORT_TARGET_TEMPERATURE | SUPPORT_OPERATION_MODE)

OPERATION_LIST = [STATE_HEAT] # await climate 1.0 to implement hvac mode

BOILER_STATUS = 'boiler_status'

HA_TO_ATAG = {
    ATTR_OPERATION_MODE: 'ch_mode',
    ATTR_CURRENT_TEMPERATURE: 'room_temp',
    ATTR_TEMPERATURE: 'ch_mode_temp',
    STATE_AUTO: 2,
    STATE_HEAT: 1
}
ATAG_TO_HA = {
    'Heating CV & Water': STATE_HEAT,
    'Heating Water': STATE_OFF,
    'Heating CV': STATE_OFF,
    'Heating Boiler': STATE_HEAT,
    'Water active': STATE_OFF,
    'CV active': STATE_HEAT,
    'Idle': STATE_OFF
}

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
        self._name = 'Atag'
        self._operation_list = OPERATION_LIST
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
        field = HA_TO_ATAG[ATTR_CURRENT_TEMPERATURE]
        if field in self.atag.sensordata:
            return self.atag.sensordata[field]
        return None

    @property
    def target_temperature(self):
        """Return the temperature we try to reach."""
        field = HA_TO_ATAG[ATTR_TEMPERATURE]
        if field in self.atag.sensordata:
            return self.atag.sensordata[field]
        return None

    @property
    def current_operation(self):
        return STATE_HEAT
        #field = BOILER_STATUS
        #if field in self.atag.sensordata:
        #    current_op = ATAG_TO_HA[self.atag.sensordata[field]]
        #    return current_op
        #return None

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
        """Return the minimum temperature."""
        return convert_temperature(DEFAULT_MIN_TEMP, TEMP_CELSIUS,
                                   self.temperature_unit)

    async def async_set_temperature(self, **kwargs):
        """Set new target temperature."""
        target_temp = kwargs.get(ATTR_TEMPERATURE)
        if target_temp is None:
            return
        await self.atag.async_set_atag(temperature=target_temp)
        self.async_schedule_update_ha_state(True)

    async def async_set_operation_mode(self, operation_mode):
        """Set ATAG ONE mode (auto, manual)."""
        if operation_mode is None:
            return
        await self.atag.async_set_atag(operation_mode=HA_TO_ATAG[operation_mode])
        self.async_schedule_update_ha_state(True)
