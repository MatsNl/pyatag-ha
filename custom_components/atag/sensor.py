"""Initialization of ATAG One sensor platform."""
import logging
from pyatag.const import SENSOR_TYPES

from homeassistant.const import (
    CONF_SENSORS,
    DEVICE_CLASS_TEMPERATURE,
    DEVICE_CLASS_PRESSURE,
)

from .const import DOMAIN, ATAG_HANDLE, DEFAULT_SENSORS
from . import AtagEntity

_LOGGER = logging.getLogger(__name__)
UNIT_TO_CLASS = {"°C": DEVICE_CLASS_TEMPERATURE, "Bar": DEVICE_CLASS_PRESSURE}


async def async_setup_platform(hass, _config, async_add_entities, discovery_info=None):
    """Atag updated to use config entry."""
    pass


async def async_setup_entry(hass, config_entry, async_add_entities):
    """Setup from config entry"""
    atag = hass.data[DOMAIN][ATAG_HANDLE][config_entry.entry_id]
    sensors = config_entry.data.get(CONF_SENSORS, DEFAULT_SENSORS)
    entities = []

    for sensor in map(str.lower, sensors):
        if sensor not in SENSOR_TYPES:
            _LOGGER.warning("Unknown %s sensor in config", sensor)
            SENSOR_TYPES[sensor] = [sensor.title(), "", "mdi:flash", sensor]
        entities.append(AtagOneSensor(atag, sensor))
    async_add_entities(entities)


class AtagOneSensor(AtagEntity):
    """Representation of a AtagOne Sensor."""

    @property
    def unit_of_measurement(self):
        """Return the unit of measurement of this entity, if any."""
        return self._unit

    @property
    def device_class(self):
        """Return the device class."""
        return UNIT_TO_CLASS.get(self._unit)

    @property
    def state(self):
        """Return the state of the sensor."""
        return self._state

    async def async_update(self):
        """Get latest data from datastore."""
        data = self.atag.sensordata.get(self._datafield)
        if isinstance(data, list):
            self._state = data[0]
            self._icon = data[1]
        elif data:
            self._state = data

