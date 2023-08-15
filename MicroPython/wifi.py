
import utime
import network

acp_if = network.WLAN(network.AP_IF)
sta_if = network.WLAN(network.STA_IF)

acp_if.active(False)
sta_if.active(True)

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
    return _status(sta_if.status())

def connect(ssid, pwd):
    try:
        if sta_if.isconnected():
            sta_if.disconnect()
            while sta_if.isconnected():
                print(status())
                utime.sleep_ms(1000)
        if not sta_if.isconnected():
            sta_if.connect(ssid, pwd)
            while not sta_if.isconnected():
                print(status())
                utime.sleep_ms(1000)
    except:
        pass
    print(status(), sta_if.ifconfig())
