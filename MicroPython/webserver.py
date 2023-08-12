
# https://github.com/tacker66/picoweb/tree/micropython

import utime
import network
import picoweb

acp_if = network.WLAN(network.AP_IF)
sta_if = network.WLAN(network.STA_IF)

acp_if.active(False)
sta_if.active(True)

def _wlan_status(status):
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

def wlan_status():
    return _wlan_status(sta_if.status())

def wlan_connect(ssid, pwd):
    try:
        if sta_if.isconnected():
            sta_if.disconnect()
            while sta_if.isconnected():
                print(wlan_status())
                utime.sleep_ms(1000)
        if not sta_if.isconnected():
            sta_if.connect(ssid, pwd)
            while not sta_if.isconnected():
                print(wlan_status())
                utime.sleep_ms(1000)
    except:
        pass
    print(wlan_status(), sta_if.ifconfig())

index_html = '<html><head><title>Hello</title></head><body><h1>Hello</h1></body></html>'

def update(config, values):
    global index_html
    s = '<html><head><title>pihome</title><meta http-equiv="refresh" content="30"><head><body><h2>pihome</h2>'                       
    for device in values:
        name = config[device]
        s = s + '\n<h3>' + device + ' (' + name + ')' + '</h3>' + '<table border="1">\n'
        for value in sorted(values[device]):
            s = s + '<tr><td align="right">' + str(value) + '</td>\n' + '<td align="left">' + str(values[device][value]) + '</td></tr>\n'
        s = s + '</table>\n'
    s = s + '</body></html>\n'
    index_html = s
    
def indexhtml(req, resp):
    yield from resp.awrite(index_html)

ROUTES  = [("/", indexhtml), ]

def start_webserver(name):
    app = picoweb.WebApp(name, ROUTES)
    app.run()
