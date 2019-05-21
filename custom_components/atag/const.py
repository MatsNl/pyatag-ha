#-*- coding:utf-8 -*-
"""Constants for Homeassistant"""

DOMAIN = 'atag'
ATAG_HANDLE = 'atag_data'
DATA_LISTENER = 'atag_listener'
SIGNAL_UPDATE_ATAG = 'atag_update'
CONF_INTERFACE = 'interface'
DEFAULT_INTERFACE = 'eth0'
DEFAULT_PORT = 10000

DEFAULT_SENSORS = [
    'current_temperature',
    'outside_temp',
    'outside_temp_avg',
    'weather_status',
    'pcb_temp',
    'temperature',
    'operation_mode',
    'ch_water_pressure',
    'ch_water_temp',
    'ch_return_temp',
    'dhw_water_temp',
    'dhw_water_pres',
    'boiler_status',
    'boiler_config',
    'burning_hours',
    'voltage',
    'current',
    'flame_level',
    'report_time'
]
