
#
# Installation:
# - rename beacons_template.conf to beacons.conf and add your private data
# - rename install_template.conf to install.conf and add your private data
# - run install.py
# - set 'test = 0' in main.py, beaconscanner.py and thingspeak.py
# - set 'use_webserver = 1' in beaconscanner.py if you have enough heap memory ;-)
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
