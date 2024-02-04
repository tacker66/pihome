
# https://file.apsystemsema.com:8083/apsystems/apeasypower/resource/APsystems%20EZ1%20Local%20API%20User%20Manual.pdf

import gc
import json
import requests

_api  = ""
_port = "8050"

def init(config, pv=None):
    global _api, _port
    _api = "http://" + config["PV"] + ":" + _port + "/"

def call_cmd(cmd):
    print(cmd)
    gc.collect()
    ret = ""
    try:
        r = requests.get(cmd, timeout=10)
        ret = r.text
        r.close()
    except:
        pass
    return ret

def read_info():
    val = call_cmd(_api + 'getDeviceInfo')
    print(val)
    
def read_values():
    val = call_cmd(_api + 'getOutputData')
    print(val)
    
def read_alarms():
    val = call_cmd(_api + 'getAlarm')
    print(val)

def update(config, pv):
    try:
        import random
        pv["POWER1"] = random.randint(0, 400)
        pv["POWER2"] = random.randint(0, 400)
        pv["POWER"]  = int(pv["POWER1"]) + int(pv["POWER2"])
        pv["ENERGY"] = random.randint(0, 1000)
        pv["ERROR"]  = 1 if random.randint(0, 9) < 4 else 0
    except Exception as e:
        print(e)
    
if __name__=='__main__':
    import configs
    config = configs.read_config('power.conf')
    init(config)
    read_info()
    read_values()
    read_alarms()
