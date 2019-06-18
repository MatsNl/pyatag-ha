# home-assistant-custom-components
ATAG ONE Custom Component for Home Assistant

Components for [ATAG One](https://www.atag-one.com/):

## Instalation

1. Add files to custom_components directory or use custom_updater component

    - .homeassistant/custom_components/atag/*.py
  
2. Add the new platform in the configuration.yaml:

    ```yaml
     atag:
    ```

3. Add optional configuration parameters if necessary:

    ```yaml
     atag:
       host: atagone.local # in case autodiscovery fails
       port: 10000 # in case connecting through port redirect
       email: 
       interface: 'eth0' # in case autodiscovery fails
       scan_interval: 
       sensors:
         - device_id
         - device_status
         - connection_status
         - date_time
         - current_temperature
         - outside_temp
         - outside_temp_avg
         - weather_status
         - pcb_temp
         - temperature
         - operation_mode
         - ch_water_pressure
         - ch_water_temp
         - ch_return_temp
         - dhw_water_temp
         - dhw_water_pres
         - dhw_flow_rate
         - boiler_status
         - boiler_config
         - burning_hours
         - voltage
         - current
         - flame_level
         - report_time
         - ch_status
         - ch_control_mode
         - ch_mode_duration
         - extend_duration
         - fireplace_duration
         - vacation_duration
         - dhw_temp_setp
         - dhw_status
         - dhw_mode
         - dhw_mode_temp
         - weather_current_temperature
    ```
4. Additional sensors can be added (but will show a warning), anything in the retrieve reply should be possible:
    ```yaml

    "device_id", "device_status", "connection_status", "date_time",
    "report_time", "burning_hours", "device_errors", "boiler_errors", "room_temp",
    "outside_temp", "dbg_outside_temp", "pcb_temp", "ch_setpoint", "dhw_water_temp",
    "ch_water_temp", "dhw_water_pres", "ch_water_pres", "ch_return_temp",
    "boiler_status", "boiler_config", "ch_time_to_temp", "shown_set_temp",
    "power_cons", "tout_avg", "rssi", "current", "voltage", "charge_status",
    "lmuc_burner_starts", "dhw_flow_rate", "resets", "memory_allocation"],
    "boiler_temp", "boiler_return_temp", "min_mod_level", "rel_mod_level",
    "boiler_capacity", "target_temp", "overshoot", "max_boiler_temp", "alpha_used",
    "regulation_state", "ch_m_dot_c", "c_house", "r_rad", "r_env", "alpha", "alpha_max",
    "delay", "mu", "threshold_offs", "wd_k_factor ", "wd_exponent",
    "lmuc_burner_hours", "lmuc_dhw_hours", "KP", "KI"],
    "ch_status", "ch_control_mode", "ch_mode", "ch_mode_duration", "ch_mode_temp",
    "dhw_temp_setp", "dhw_status", "dhw_mode", "dhw_mode_temp", "weather_temp",
    "weather_status", "vacation_duration", "extend_duration", "fireplace_duration"
    ```



