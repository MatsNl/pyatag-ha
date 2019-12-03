"""Constants for Homeassistant"""

DOMAIN = "atag"
ATAG_HANDLE = "atag_data"
DATA_LISTENER = "atag_listener"
SIGNAL_UPDATE_ATAG = "atag_update"
CONF_INTERFACE = "interface"
DEFAULT_PORT = 10000
DEVICEID = "device_id"
DEFAULT_SCAN_INTERVAL = 30
PROJECT_URL = "https://www.atag-one.com"


DEFAULT_SENSORS = [
    #    'current_temperature',
    "outside_temp",
    "outside_temp_avg",
    "weather_status",
    #    'temperature',
    "operation_mode",
    "ch_water_pressure",
    #   'ch_water_temp',
    #   'ch_return_temp',
    "dhw_water_temp",
    #   'dhw_flow_rate',
    "dhw_water_pres",
    "boiler_status",
    #   'boiler_config',
    "burning_hours",
    "flame_level",
    # "ch_status",
    #   "ch_control_mode",
    #  "dhw_temp_setp",
    #    "dhw_status",
    #    "dhw_mode",
    #    "dhw_mode_temp",
]
