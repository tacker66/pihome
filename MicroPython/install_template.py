
#
# Installation:
# - rename beacons_template.conf to beacons.conf and add your private data
# - rename install_template.conf to install.conf and add your private data
# - run install.py
# - set 'test = 0' in beaconscanner.py, thingspeak.py, display.py
# - use 'test = 1' in beaconscanner.py to identify new beacons
# - use 'test = 1' in display.py to ease finding calibration values
# - set 'use_display = 1' in beaconscanner.py if needed
# - set 'use_webserver = 1' in beaconscanner.py if needed
# - in display.py: adapt _used_pos and _used_len to your needs
#

import time
import network

SSID = "XXXXXXXX"
PASS = "XXXXXXXX"

wlan = network.WLAN(network.STA_IF)
wlan.active(True)
wlan.connect(SSID, PASS)

while not wlan.isconnected():
    time.sleep(1)
    
print("Connected")

import mip
mip.install("github:tacker66/picoweb")
mip.install("github:tacker66/Pico_LCD_114_V2")
