
#
# Installation:
# - copy all files in this folder to your device
# - rename beacons_template.conf to beacons.conf and add your wifi credentials and thingspeak channel keys
# - run install.py
# - beaconscanner.py: set 'use_display = 0' if no display is used
# - beaconscanner.py: set 'use_webserver = 0' if no webserver is used
# - adding a beacon:
#   - set 'test = 1' in beaconscanner.py and display.py
#   - activate the beacon and run beaconsscanner.py in your IDE
#   - the unknown beacon will be shown with its name and address
#   - add the address data in beacons.conf
#   - add configuration data for this beacon in beacons.conf
#   - run beaconscanner.py again; beacon values will be displayed
#   - if you have several beacons consider chosing suitable calibration values for TMP and HUM to get identical readings 
# - display.py: set _used_pos to the number of beacons to be displayed
# - display.py: set _used_len to the number of horizontal pixels to be used for displaying entries
# - set 'test = 0' in beaconscanner.py, display.py, thingspeak.py
# - restart your device
#

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
