"""Initialization of ATAG One sensor platform."""
import logging
from homeassistant.core import callback
from homeassistant.helpers.dispatcher import async_dispatcher_connect
from homeassistant.helpers.entity import Entity
from homeassistant.const import CONF_SENSORS
from pyatag.const import SENSOR_TYPES, ATTR_REPORT_TIME
from .const import (DOMAIN, ATAG_HANDLE, SIGNAL_UPDATE_ATAG)

_LOGGER = logging.getLogger(__name__)
SENSOR_PREFIX = 'Atag '

async def async_setup_platform(hass, _config, async_add_entities, discovery_info=None):
    """Initialization of ATAG One sensor platform."""
    atag = hass.data[DOMAIN][ATAG_HANDLE]
    entities = []
    if not CONF_SENSORS in discovery_info:
        return False

    for sensor in discovery_info[CONF_SENSORS]:
        sensor_type = sensor.lower()

        if sensor_type not in SENSOR_TYPES:
            _LOGGER.warning("Unknown %s sensor in config", sensor_type)
            SENSOR_TYPES[sensor_type] = [
                sensor_type.title(), '', 'mdi:flash', sensor_type.title()]

        entities.append(AtagOneSensor(atag, sensor_type))

    async_add_entities(entities)


class AtagOneSensor(Entity):
    """Representation of a AtagOne Sensor."""

    def __init__(self, atag, sensor_type):
        """Initialize the sensor."""
        self.atag = atag
        self._type = sensor_type
        self._name = SENSOR_PREFIX + SENSOR_TYPES[self._type][0]
        self._unit = SENSOR_TYPES[self._type][1]
        self._icon = SENSOR_TYPES[self._type][2]
        self._datafield = SENSOR_TYPES[self._type][3]
        self._state = None
        self._attr = {}

        _LOGGER.debug('%s Sensor initialized', self._name)

    @property
    def should_poll(self):
        """Polling needed for thermostat."""
        return False

    @property
    def name(self):
        """Return the name of the sensor."""
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
    def icon(self):
        """Icon to use in the frontend, if any."""
        return self._icon

    @property
    def state(self):
        """Return the state of the sensor."""
        return self._state

    @property
    def unit_of_measurement(self):
        """Return the unit of measurement of this entity, if any."""
        return self._unit

    @property
    def device_state_attributes(self):
        """Return the state attributes of this device."""
        return self._attr

    async def async_update(self):
        """Get the latest data and use it to update our sensor state."""
        try:
            if isinstance(self.atag.sensordata[self._type], list):
                self._state = self.atag.sensordata[self._type][0]
                self._icon = self.atag.sensordata[self._type][1]
            else:
                self._state = self.atag.sensordata[self._type]
            self._attr[ATTR_REPORT_TIME] = self.atag.sensordata[ATTR_REPORT_TIME]
            return True
        except KeyError:
            _LOGGER.debug('%s failed to update', self._name)
            return False
