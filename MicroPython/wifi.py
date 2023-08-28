
import time
import network

nic = network.WLAN(network.STA_IF)

def _status(status):
    if status == network.STAT_IDLE:
        return 'IDLE'
    elif status == network.STAT_CONNECTING:
        return 'CONNECTING'
    elif status == network.STAT_NO_AP_FOUND:
        return 'NO_AP_FOUND'
    elif status == network.STAT_GOT_IP:
        return 'STAT_GOT_IP'
    else:
        return "UNKNOWN: {}".format(status) 

def status():
    return _status(nic.status())

def is_connected():
    return nic.isconnected()

def connect(ssid, pwd, reconnect=False):
    try:
        if reconnect:
            nic.active(False)
        if not nic.isconnected():
            nic.active(True)
            nic.connect(ssid, pwd)
            wait = 30
            while not nic.isconnected() and wait:
                print(status())
                time.sleep(1)
                wait = wait - 1
    except:
        pass
    print(status(), nic.ifconfig())
