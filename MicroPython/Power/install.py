
#
# Installation:
# - copy all files in this folder to your device
# - rename power_template.conf to power.conf and add your wifi credentials, awtrix and pv addresses and thingspeak channel keys
# - run install.py
# - set 'test = 0' in power.py
# - restart your device
#

import mip

mip.install("requests")
mip.install("github:tacker66/picoweb")
