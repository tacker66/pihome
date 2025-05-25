
#
# Installation:
# - copy all files in this folder to your device
# - rename power_template.conf to power.conf and add your wifi credentials, awtrix and pv addresses and thingspeak channel keys
# - run install.py
# - restart your device
# - add 'update_energy_per_interval.matlab' in ThingSpeak as a MATLAB Analysis 
#   together with a TimeControl to calculate energy production per month and year
#

import mip

mip.install("requests")
mip.install("github:tacker66/picoweb")
