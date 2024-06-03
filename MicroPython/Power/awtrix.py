
# https://github.com/Blueforcer/awtrix-light
# https://blueforcer.github.io/awtrix-light/#/api

import gc
import requests

_api = ""

def api_status():
    gc.collect()
    r = requests.get(_api + "stats")
    print(r.text)
    r.close()
    r = requests.get(_api + "loop")
    print(r.text)
    r.close()
    r = requests.get(_api + "settings")
    print(r.text)
    r.close()

def update_setting(setting, value):
    gc.collect()
    data = '{"' + setting + '": "' + str(value) + '"}'
    try:
        r = requests.post(_api + 'settings', data=data)
    except:
        pass
    r.close()

def update_app(name, text, icon=0, color="", save=False):
    gc.collect()
    data = '{"text": "' + text + '"'
    data = data + ', "textCase": 2'
    data = data + ', "lifetime": 600'
    data = data + ', "lifetimeMode": 1'
    if icon != 0:
        data = data + ', "icon": "' + str(icon) + '"' 
    if color != "":
        data = data + ', "color": "' + color + '"' 
    if save:
        data = data + ', "save": true'
    data = data + '}'
    try:
        r = requests.post(_api + 'custom?name='+name, data=data)
    except:
        pass
    r.close()

def init(config, pv):
    global _api
    _api = "http://" + config["AWTRIX"] + "/api/"

# from https://developer.lametric.com/icons
ICO_MOON  = 12181
ICO_CLOUD = 1531
ICO_SUNNY = 4973
ICO_SUN   = 10350
ICO_MONTH = 8480
ICO_YEAR  = 8481

_init = False

def update(config, pv):
    try:
        global _init
        if not _init:
            update_setting("TEFF", 10)
            update_setting("TSPEED", 400)
            update_setting("ATIME", 4)
            _init = True
        icon = ICO_MOON
        val = int(pv["POWER"])
        if val >= int(config["CLOUDLEVEL"]):
            icon = ICO_CLOUD
        if val >= int(config["SUNNYLEVEL"]):
            icon = ICO_SUNNY
        if val >= int(config["SUNLEVEL"]):
            icon = ICO_SUN
        color = "#FF0000"
        if int(pv["ERROR"]) == 0:
            color = "#FFFFFF"
        update_app("pvcur",  str(int(val)) + " W", icon, color)
        update_app("pvmonth",str(int(pv["ENERGYMONTH"])) + " kWh / Month", ICO_MONTH, color)
        update_app("pvyear", str(int(pv["ENERGYYEAR"])) + " kWh / Year", ICO_YEAR, color)
    except Exception as e:
        print(e)

if __name__=='__main__':
    import configs
    config = configs.read_config('power.conf')
    _api = "http://" + config["AWTRIX"] + "/api/"
    api_status()
    update_app("pvcur", "100W", ICO_SUNNY, "#FFFFFF")
    update_app("pvsum", "100kWh", ICO_BATTERY)
    print(gc.mem_free())
