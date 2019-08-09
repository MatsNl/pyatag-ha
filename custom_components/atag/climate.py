"""Initialization of ATAG One climate platform."""
import logging
from typing import List, Optional  # Any, Dict

from homeassistant.components.climate import (ClimateDevice)
from homeassistant.components.climate.const import (
    HVAC_MODE_HEAT, HVAC_MODE_AUTO, HVAC_MODE_OFF, ATTR_CURRENT_TEMPERATURE,
    SUPPORT_TARGET_TEMPERATURE, CURRENT_HVAC_HEAT,  # SUPPORT_PRESET_MODE,
    CURRENT_HVAC_IDLE, DEFAULT_MIN_TEMP, DEFAULT_MAX_TEMP)

from homeassistant.const import (TEMP_CELSIUS, ATTR_TEMPERATURE)

from homeassistant.core import callback
from homeassistant.helpers.dispatcher import async_dispatcher_connect
from homeassistant.util.temperature import convert as convert_temperature
from homeassistant.helpers.restore_state import RestoreEntity

from .const import (ATAG_HANDLE, DOMAIN, SIGNAL_UPDATE_ATAG)

SUPPORT_FLAGS = SUPPORT_TARGET_TEMPERATURE  # | SUPPORT_PRESET_MODE
SUPPORT_PRESET = []  # [PRESET_AWAY, PRESET_COMFORT, PRESET_HOME, PRESET_SLEEP]

BOILER_STATUS = 'boiler_status'
CH_CONTROL_MODE = 'ch_control_mode'

HA_TO_ATAG = {
    # ATTR_OPERATION_MODE: 'ch_mode',
    ATTR_CURRENT_TEMPERATURE: 'room_temp',
    ATTR_TEMPERATURE: 'ch_mode_temp',
    HVAC_MODE_AUTO: 1,
    HVAC_MODE_HEAT: 0
}

ATAG_TO_HA = {
    'Heating CV & Water': CURRENT_HVAC_HEAT,
    'Heating Water': CURRENT_HVAC_IDLE,
    'Heating CV': CURRENT_HVAC_HEAT,
    'Heating Boiler': CURRENT_HVAC_HEAT,
    'Pumping Water': CURRENT_HVAC_IDLE,
    'Pumping CV': CURRENT_HVAC_IDLE,
    'Idle': CURRENT_HVAC_IDLE,
    'Weather based': HVAC_MODE_AUTO,
    'Thermostat': HVAC_MODE_HEAT
}

_LOGGER = logging.getLogger(__name__)


async def async_setup_platform(hass, _config, async_add_devices,
                               _discovery_info=None):
    """Setup for the Atag One thermostat."""
    async_add_devices([AtagOneThermostat(hass)])


# pylint: disable=abstract-method
class AtagOneThermostat(ClimateDevice, RestoreEntity):
    """Representation of the ATAG One thermostat."""

    def __init__(self, hass):
        """Initialize"""
        _LOGGER.debug("Initializing Atag climate platform")
        self.atag = hass.data[DOMAIN][ATAG_HANDLE]
        self._name = 'Atag'
        self._on = None

    async def async_added_to_hass(self):
        """Register callbacks & state restore for fake "Off" mode."""
        async_dispatcher_connect(
            self.hass, SIGNAL_UPDATE_ATAG, self._update_callback)
        await super().async_added_to_hass()
        last_state = await self.async_get_last_state()
        if last_state:
            self._on = last_state.state != HVAC_MODE_OFF

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
    def hvac_mode(self) -> Optional[str]:
        """Return hvac operation ie. heat, cool mode."""
        if self._on is None:
            return None
        if not self._on:
            return HVAC_MODE_OFF
        if self._on:
            _mode = self.atag.sensordata.get(CH_CONTROL_MODE)
            return ATAG_TO_HA.get(_mode)
        return

    @property
    def hvac_modes(self) -> List[str]:
        """Return the list of available hvac operation modes."""
        return [HVAC_MODE_HEAT, HVAC_MODE_AUTO, HVAC_MODE_OFF]

    @property
    def hvac_action(self) -> Optional[str]:
        """Return the current running hvac operation."""
        field = BOILER_STATUS
        if field in self.atag.sensordata:
            return ATAG_TO_HA[self.atag.sensordata[field]]
        return None

    @property
    def temperature_unit(self):
        """Return the unit of measurement."""
        return TEMP_CELSIUS

    @property
    def current_temperature(self) -> Optional[float]:
        """Return the current temperature."""
        field = HA_TO_ATAG[ATTR_CURRENT_TEMPERATURE]
        if field in self.atag.sensordata:
            return self.atag.sensordata[field]
        return None

    @property
    def target_temperature(self) -> Optional[float]:
        """Return the temperature we try to reach."""
        field = HA_TO_ATAG[ATTR_TEMPERATURE]
        if field in self.atag.sensordata:
            return self.atag.sensordata[field]
        return None

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

    async def async_set_temperature(self, **kwargs) -> None:
        """Set new target temperature."""
        target_temp = kwargs.get(ATTR_TEMPERATURE)
        if target_temp is None or not self._on:
            return None
        await self.atag.async_set_atag(temperature=target_temp)
        self.async_schedule_update_ha_state(True)

    async def async_set_hvac_mode(self, hvac_mode: str) -> None:
        """Set new target hvac mode."""
        if hvac_mode == HVAC_MODE_OFF:
            _LOGGER.debug("Turning off climate")
            self._on = False
            self.async_schedule_update_ha_state(True)
            return None

        self._on = True
        field = CH_CONTROL_MODE
        if ATAG_TO_HA.get(self.atag.sensordata.get(field)) == hvac_mode:
            _LOGGER.debug("Already on %s mode, no API call", hvac_mode)
            self.async_schedule_update_ha_state(True)
            return None
        _LOGGER.debug("Setting Atag to %s mode", hvac_mode)
        await self.atag.async_set_atag(ch_control_mode=HA_TO_ATAG[hvac_mode])
        self.async_schedule_update_ha_state(True)
        return None
