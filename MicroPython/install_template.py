
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

# mip.install("pkg_resources")
