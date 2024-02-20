
# https://file.apsystemsema.com:8083/apsystems/apeasypower/resource/APsystems%20EZ1%20Local%20API%20User%20Manual.pdf

import gc
import json
import myrequests

_api  = ""
_port = "8050"

def init(config, pv=None):
    global _api, _port
    _api = "http://" + config["PV"] + ":" + _port + "/"

_last_exc = "-"
_cnt_exc  = 0
def call_cmd(cmd):
    global _last_exc, _cnt_exc
    gc.collect()
    ret = "{}"
    try:
        r = myrequests.get(cmd, timeout=20)
        ret = r.text
        r.close()
        _cnt_exc = 0
    except Exception as e:
        _last_exc = str(e)
        _cnt_exc += 1
    return ret

def read_info():
    val = call_cmd(_api + 'getDeviceInfo')
    return(val)
    
def read_values():
    val = call_cmd(_api + 'getOutputData')
    return(val)
    
def read_alarms():
    val = call_cmd(_api + 'getAlarm')
    return(val)
    
def read_maxpower():
    val = call_cmd(_api + 'getMaxPower')
    return(val)

def update(config, pv):
    alarms = read_alarms()
    values = read_values()
    pv["ALARMS"] = "pv alarms: " + alarms
    pv["EXCEPT"] = "pv cnt: " + str(_cnt_exc) + " pv exc: " + _last_exc
    try:
        values = json.loads(values) # json might be corrupted due to incomplete read
    except:
        values = dict()
    if "data" in values:
        value = values["data"]
        if ("p1" in value) and ("p2" in value) and ("te1" in value) and ("te2" in value): # json might be incomplete due to incomplete read
            pv["POWER1"] = int(value["p1"])
            pv["POWER2"] = int(value["p2"])
            pv["POWER"]  = int(value["p1"] + value["p2"])
            pv["ENERGY"] = int(value["te1"] + value["te2"])
    try:
        alarms = json.loads(alarms) # json might be corrupted due to incomplete read
    except:
        alarms = dict()
    if "data" in alarms:
        alarm = alarms["data"]
        if ("og" in alarm) and ("isce1" in alarm) and ("isce2" in alarm) and ("oe" in alarm): # json might be incomplete due to incomplete read
            pv["ERROR"] = int(alarm["og"]) + int(alarm["isce1"]) + int(alarm["isce2"]) + int(alarm["oe"])
        else:
            pv["ERROR"] = -2 # incomplete data
    else:
        pv["ERROR"] = -1 # device is offline or corrupt data
        
if __name__=='__main__':
    import configs
    config = configs.read_config('power.conf')
    init(config)
    print(read_info())
    print(read_values())
    print(read_alarms())
    print(read_maxpower())
