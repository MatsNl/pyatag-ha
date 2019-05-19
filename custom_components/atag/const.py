#-*- coding:utf-8 -*-
DOMAIN = 'atag'
ATAG_HANDLE = 'atag_handle'
DATA_LISTENER = 'listener'
SIGNAL_UPDATE_ATAG = 'atag_update'
CONF_INTERFACE = 'interface'
DEFAULT_INTERFACE = 'eth0'

DEFAULT_PORT = 10000

SENSOR_TYPES = {
    'current_temp': ['Room Temp', '°C', 'mdi:thermometer', 'room_temp'],
    'outside_temp': ['Outside Temp', '°C', 'mdi:thermometer', 'outside_temp'],
    'outside_temp_avg': ['Average Outside Temp', '°C', 'mdi:thermometer',
                         'tout_avg'],
    'pcb_temp': ['PCB Temp', '°C', 'mdi:thermometer', 'pcb_temp'],
    'temperature': ['Target Temp', '°C', 'mdi:thermometer', 'shown_set_temp'],
    'ch_water_pressure': ['Central Heating Pressure', 'Bar', 'mdi:gauge',
                          'ch_water_pres'],
    'ch_water_temp': ['Central Heating Water Temp', '°C', 'mdi:thermometer',
                      'ch_water_temp'],
    'ch_return_temp': ['Central Heating Return Temp', '°C', 'mdi:thermometer',
                       'ch_return_temp'],
    'dhw_water_temp': ['Hot Water Temp', '°C', 'mdi:thermometer',
                       'dhw_water_temp'],
    'dhw_water_pres': ['Hot Water Pressure', 'Bar', 'mdi:gauge',
                       'dhw_water_pres'],
    'boiler_status': ['Boiler Status', '', 'mdi:flash', 'boiler_status'],
    'boiler_config': ['Boiler Config', '', 'mdi:flash', 'boiler_config'],
    'water_pressure': ['Boiler Pressure', 'Bar', 'mdi:gauge',
                       'water_pressure'],
    'burning_hours': ['Burning Hours', 'h', 'mdi:fire', 'burning_hours'],
    'voltage': ['Voltage', 'V', 'mdi:flash', 'voltage'],
    'current': ['Current', 'mA', 'mdi:flash-auto', 'current'],
    'flame_level': ['Flame', '%', 'mdi:fire', 'rel_mod_level'],
}

ATTR_REPORT_TIME = 'report_time'
