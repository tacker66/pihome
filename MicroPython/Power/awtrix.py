
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
    r = requests.post(_api + 'settings', data=data)
    print(r.text)
    r.close()

def update_app(name, text, icon=0, color="", save=False):
    gc.collect()
    data = '{"text": "' + text + '"'
    data = data + ', "textCase": 2'
    if icon != 0:
        data = data + ', "icon": "' + str(icon) + '"' 
    if color != "":
        data = data + ', "color": "' + color + '"' 
    if save:
        data = data + ', "save": true'
    data = data + '}'
    r = requests.post(_api + 'custom?name='+name, data=data)
    print(r.text)
    r.close()

def init(config, pv):
    global _api
    _api = "http://" + config["AWTRIX"] + "/api/"

# from https://developer.lametric.com/icons
ICO_MOON    = 12181
ICO_CLOUD   = 91
ICO_SUNNY   = 4973
ICO_SUN     = 10350
ICO_BATTERY = 390

_init = False

def update(config, pv):
    global _init
    if not _init:
        update_setting("TEFF", 10)
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
    update_app("pvcur", str(val) + " W", icon, color)
    update_app("pvsum", str(pv["ENERGY"]) + " kWh", ICO_BATTERY, color)

if __name__=='__main__':
    import configs
    config = configs.read_config('power.conf')
    _api = "http://" + config["AWTRIX"] + "/api/"
    api_status()
    update_app("pvcur", "100W", ICO_SUNNY, "#FFFFFF")
    update_app("pvsum", "100kWh", ICO_BATTERY)
    print(gc.mem_free())
