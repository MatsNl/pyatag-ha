"""Support for ATAG water heater."""
import logging

from homeassistant.components.water_heater import (
    ATTR_TEMPERATURE,
    STATE_ECO,
    STATE_PERFORMANCE,
    WaterHeaterDevice,
)
from homeassistant.const import STATE_OFF, TEMP_CELSIUS

from .const import ATAG_HANDLE, DOMAIN
from . import AtagEntity

_LOGGER = logging.getLogger(__name__)

# (SUPPORT_TARGET_TEMPERATURE | SUPPORT_OPERATION_MODE )
SUPPORT_FLAGS_HEATER = 0

OPERATION_LIST = [STATE_OFF, STATE_ECO, STATE_PERFORMANCE]

HA_STATE_TO_ATAG = {STATE_ECO: "eco", STATE_OFF: "off", STATE_PERFORMANCE: "comfort"}

ATAG_STATE_TO_HA = {
    "Heating CV & Water": STATE_PERFORMANCE,
    "Heating Water": STATE_PERFORMANCE,
    "Heating CV": STATE_OFF,
    "Heating Boiler": STATE_ECO,
    "Pumping Water": STATE_OFF,
    "Pumping CV": STATE_OFF,
    "Idle": STATE_OFF,
}

DHW_SETPOINT = "dhw_temp_setp"  # water demand setpoint
DHW_TEMPERATURE = "dhw_mode_temp"  # comfort demand setpoint
DHW_CURRENT_TEMPERATURE = "dhw_water_temp"  # current water temp
BOILERSTATUS = "boiler_status"
DHW_MAX = "dhw_max_set"
DHW_MIN = "dhw_min_set"


async def async_setup_platform(hass, _config, async_add_devices, _discovery_info=None):
    """Atag updated to use config entry."""
    pass


async def async_setup_entry(hass, config_entry, async_add_entities):
    """Setup DHW device from config entry"""
    atag = hass.data[DOMAIN][ATAG_HANDLE][config_entry.entry_id]
    async_add_entities([AtagOneWaterHeater(atag, "DHW")])


class AtagOneWaterHeater(
    AtagEntity, WaterHeaterDevice
):  # pylint: disable=abstract-method
    """Representation of an ATAG water heater."""

    @property
    def supported_features(self):
        """Return the list of supported features."""
        return SUPPORT_FLAGS_HEATER

    @property
    def temperature_unit(self):
        """Return the unit of measurement."""
        return TEMP_CELSIUS

    @property
    def current_temperature(self):
        """Return the current temperature."""
        return self.atag.sensordata.get(DHW_CURRENT_TEMPERATURE)

    @property
    def current_operation(self):
        """Return current operation"""
        return ATAG_STATE_TO_HA.get(self.atag.sensordata.get(BOILERSTATUS))

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
        pass

    @property
    def target_temperature(self):
        """Return the setpoint if water demand, otherwise return base temp (comfort level)."""
        current_op = ATAG_STATE_TO_HA.get(self.atag.sensordata.get(BOILERSTATUS))
        if current_op != STATE_OFF:
            return self.atag.sensordata[DHW_SETPOINT]

        temp = self.atag.sensordata.get(DHW_TEMPERATURE)
        if temp == 150:
            return 0
        return temp

    @property
    def max_temp(self):
        """Return the maximum temperature."""
        return self.atag.sensordata.get(DHW_MAX)

    @property
    def min_temp(self):
        """Return the minimum temperature."""
        return self.atag.sensordata.get(DHW_MIN)
