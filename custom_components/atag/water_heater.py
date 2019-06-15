"""Support for ATAG water heater."""
import logging

from homeassistant.components.water_heater import (
    ATTR_TEMPERATURE, STATE_ECO, STATE_PERFORMANCE,
    SUPPORT_OPERATION_MODE, SUPPORT_TARGET_TEMPERATURE, WaterHeaterDevice)
from homeassistant.const import STATE_OFF, TEMP_CELSIUS
from homeassistant.core import callback
from homeassistant.helpers.dispatcher import async_dispatcher_connect
from homeassistant.util.temperature import convert as convert_temperature

from .const import (ATAG_HANDLE, DOMAIN, SIGNAL_UPDATE_ATAG)

_LOGGER = logging.getLogger(__name__)

SUPPORT_FLAGS_HEATER = 0 # (SUPPORT_TARGET_TEMPERATURE | SUPPORT_OPERATION_MODE )

OPERATION_LIST = [STATE_OFF, STATE_ECO, STATE_PERFORMANCE]

HA_STATE_TO_ATAG = {
    STATE_ECO: 'eco',
    STATE_OFF: 'off',
    STATE_PERFORMANCE: 'comfort',
}

ATAG_STATE_TO_HA = {
    'Heating CV & Water': STATE_PERFORMANCE,
    'Heating Water': STATE_PERFORMANCE,
    'Heating CV': STATE_OFF,
    'Heating Boiler': STATE_ECO,
    'Pumping Water': STATE_OFF,
    'Pumping CV': STATE_OFF,
    'Idle': STATE_OFF
}

DHW_SETPOINT = 'dhw_temp_setp' # fixed setpoint
DHW_TEMPERATURE = 'dhw_mode_temp' # current demand
DHW_CURRENT_TEMPERATURE = 'dhw_water_temp' # current water temp
BOILERSTATUS = 'boiler_status'
DHW_MAX = 'dhw_max_set'
DHW_MIN = 'dhw_min_set'

async def async_setup_platform(hass, _config, async_add_devices,
                               _discovery_info=None): # pylint: disable=abstract-method
    """Setup for the Atag One thermostat."""
    async_add_devices([AtagOneWaterHeater(hass)])

class AtagOneWaterHeater(WaterHeaterDevice):
    """Representation of an ATAG water heater."""
 
    def __init__(self, hass):
        """Initialize"""
        _LOGGER.debug("Initializing Atag climate platform")
        self.atag = hass.data[DOMAIN][ATAG_HANDLE]
        self._name = 'Atag DHW'
        self._operation_list = OPERATION_LIST
        _LOGGER.debug("Atag heatpump initialized")

    @property
    def name(self):
        """Return the name of the thermostat."""
        return self._name

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
        return SUPPORT_FLAGS_HEATER

    @property
    def temperature_unit(self):
        """Return the unit of measurement."""
        # The Wink API always returns temp in Celsius
        return TEMP_CELSIUS

    @property
    def current_temperature(self):
        """Return the current temperature."""
        if DHW_CURRENT_TEMPERATURE in self.atag.sensordata:
            return self.atag.sensordata[DHW_CURRENT_TEMPERATURE]
        return None

    @property
    def current_operation(self):
        """
        Return current operation one of the following.

        ["eco", "performance", "heat_pump",
        "high_demand", "electric_only", "gas]
        """
        if not BOILERSTATUS in self.atag.sensordata:
            return None 
        current_op = ATAG_STATE_TO_HA.get(self.atag.sensordata[BOILERSTATUS])
        if current_op is None:
            current_op = STATE_OFF
        return current_op

    @property
    def operation_list(self):
        """List of available operation modes."""
        return OPERATION_LIST

    def set_temperature(self, **kwargs):
        """Set new target temperature."""
        target_temp = kwargs.get(ATTR_TEMPERATURE)
        self.atag.set_atag(dhw_target_temp=target_temp)

    def set_operation_mode(self, operation_mode):
        """Set operation mode."""
        return

    @property
    def target_temperature(self):
        """Return the temperature we try to reach."""
        if DHW_TEMPERATURE in self.atag.sensordata:
            temp = self.atag.sensordata[DHW_TEMPERATURE]
            if temp == 150:
                return 0
            return self.atag.sensordata[DHW_TEMPERATURE]
        return None

    @property
    def max_temp(self):
        """Return the maximum temperature."""
        if DHW_MAX in self.atag.sensordata:
            temp = self.atag.sensordata[DHW_MAX]
            return convert_temperature(temp, TEMP_CELSIUS,
                                       self.temperature_unit)
        return None

    @property
    def min_temp(self):
        """Return the minimum temperature."""
        if DHW_MIN in self.atag.sensordata:
            temp = self.atag.sensordata[DHW_MIN]
            return convert_temperature(temp, TEMP_CELSIUS,
                                       self.temperature_unit)
        return None