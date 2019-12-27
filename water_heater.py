"""Support for ATAG water heater."""
import logging

from homeassistant.components.water_heater import (
    ATTR_TEMPERATURE,
    STATE_ECO,
    STATE_PERFORMANCE,
    WaterHeaterDevice,
)
from homeassistant.const import STATE_OFF, TEMP_CELSIUS

from . import AtagEntity, DOMAIN

_LOGGER = logging.getLogger(__name__)

# (SUPPORT_TARGET_TEMPERATURE | SUPPORT_OPERATION_MODE )
SUPPORT_FLAGS_HEATER = 0

OPERATION_LIST = [STATE_OFF, STATE_ECO, STATE_PERFORMANCE]

async def async_setup_platform(hass, config, async_add_devices, _discovery_info=None):
    """Atag updated to use config entry."""
    pass


async def async_setup_entry(hass, config_entry, async_add_entities):
    """Setup DHW device from config entry"""
    atag = hass.data[DOMAIN][config_entry.entry_id]
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
        return self.atag.dhw_temperature

    @property
    def current_operation(self):
        """Return current operation"""
        if self.atag.dhw_status:
            return STATE_PERFORMANCE
        return STATE_OFF

    @property
    def operation_list(self):
        """List of available operation modes."""
        return OPERATION_LIST

    async def set_temperature(self, **kwargs):
        """Set new target temperature."""
        if await self.atag.dhw_set_temp(kwargs.get(ATTR_TEMPERATURE)):
            self.async_schedule_update_ha_state(True)

    def set_operation_mode(self, operation_mode):
        """Set operation mode."""
        pass

    @property
    def target_temperature(self):
        """Return the setpoint if water demand, otherwise return base temp (comfort level)."""
        return self.atag.dhw_target_temperature

    @property
    def max_temp(self):
        """Return the maximum temperature."""
        return self.atag.dhw_max_temp

    @property
    def min_temp(self):
        """Return the minimum temperature."""
        return self.atag.dhw_min_temp
