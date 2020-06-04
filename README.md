# TempDAQ
Data Acquisition (DAQ) for 1-wire temperature sensors like the digital sensor [DS18S20](https://www.adafruit.com/product/374) or [the thermocouple adapter MAX31850K](https://www.adafruit.com/product/1727).

## Installation
1. Enable 1-Wire support as described here: https://learn.adafruit.com/adafruits-raspberry-pi-lesson-11-ds18b20-temperature-sensing/ds18b20
2. Run: `pip3 install -r requirements.txt`

### Enable/Disable Autostart
1. Edit temp_daq.py and temp_daq_config.yaml paths in temp_daq.service file to your own needs 
2. `sudo systemctl enable [full path to temp_daq.service file]`    
    This automatically links the service and enables it. Replace `enable` with `disable` to disable service.

## Usage
Start with `python3 temp_daq.py [full path to temp_daq_config.yaml]`

**Important: you might need to reboot the Raspberry Pi if plug sensors in order to be detected!**

### Get sensor id
1. Plug in **exclusively** the sensor you want to identify
2. The bash command `w1thermsensor ls` lists the _HWID_ and _Type_ of the sensor
3. Enter the _HWID_ in the temp_daq_config.yaml

### Status led
If the status led is enabled in config, it will glow when running:
- Constant glow: app is started, but not yet fully initialized
- Slow blinking: app is running normally, waiting for next acquisition
- Fast blinking: temperature acquisition is happening

## Config file
short primer on syntax of yaml: https://learnxinyminutes.com/docs/yaml/

### Example config with explanation
```yaml
storage_directory: "/home/pi/Documents/temp_daq/" # directory where to put output csv files
interval: 10 # log temperature every [x] seconds
status_led: true # enable/disable status led, blinks everytime a vibration file is written
status_led_pin: 21  # only read if status_led == true
sensors: 
  - name: sensor1 # name of sensor which is used for the output csv
    id: 00000c43b797 # id of sensor
  - name: sensor2
    id: 00000c43ed7d
```
