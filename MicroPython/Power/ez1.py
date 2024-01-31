
# https://file.apsystemsema.com:8083/apsystems/apeasypower/resource/APsystems%20EZ1%20Local%20API%20User%20Manual.pdf

import gc
import requests

_api = ""

def read_values(v):
    gc.collect()
    data = '{"' + setting + '": "' + str(value) + '"}'
    r = requests.post(_api + 'settings', data=data)
    print(r.text)
    r.close()

def init(config, pv):
    global _api
    _api = "http://" + config["PV"] + ":PORT/"

def update(config, pv):
    try:
        import random
        pv["POWER1"] = random.randint(0, 400)
        pv["POWER2"] = random.randint(0, 400)
        pv["POWER"]  = int(pv["POWER1"]) + int(pv["POWER2"])
        pv["ENERGY"] = random.randint(0, 1000)
        pv["ERROR"]  = 1 if random.randint(0, 9) < 4 else 0
        print(pv)
    except Exception as e:
        print(e)
    
if __name__=='__main__':
    import configs
    config = configs.read_config('power.conf')
    _api = "http://" + config["PV"] + ":PORT/"
    #read_values()
    print(gc.mem_free())
