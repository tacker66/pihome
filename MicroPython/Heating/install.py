
#
# Installation:
# - copy all files in this folder to your device
# - rename beacons_template.conf to beacons.conf and add your wifi credentials and thingspeak channel keys
# - run install.py
# - beaconscanner.py: set 'display_entries' and 'display_width' in beacons.conf according to your needs or set 'use_display = 0' if no display is used
# - beaconscanner.py: set 'use_webserver = 0' if no webserver is used
# - adding a beacon:
#   - set 'test = 1' in beaconscanner.py and display.py
#   - activate the beacon and run beaconsscanner.py in your IDE
#   - the unknown beacon will be shown with its name and address
#   - add the address data in beacons.conf
#   - add configuration data for this beacon in beacons.conf
#   - run beaconscanner.py again; beacon values will be displayed
#   - if you have several beacons consider chosing suitable calibration values for TMP and HUM to get identical readings 
# - set 'test = 0' in beaconscanner.py, display.py
# - restart your device
#


import micropython
micropython.opt_level(3)

import time
import network

config = dict()
def read_config(file):
    fd = open(file)
    for line in fd:
        line = line.strip()
        if len(line) > 0 and line[0] != "#":
            tok = line.split("=")
            config[tok[0].strip()] = tok[1].strip()
read_config('beacons.conf')

wlan = network.WLAN(network.STA_IF)
wlan.active(True)
wlan.connect(config["SSID"], config["PASS"])

while not wlan.isconnected():
    time.sleep(1)
    
print("Connected")

import mip
mip.install("github:tacker66/picoweb")
mip.install("github:tacker66/Pico_LCD_114_V2")
