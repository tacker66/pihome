
# https://thingspeak.com/

test = 1

import time
import requests

if test:
    import gc

WAITTIME = 20   # thingspeak only allows ~8.200 messages per day so
                # messages cannot be sent faster than every 10.6 seconds;
                # otherwise r.text == "0" will be returned

url = ""
last_time = 0
telegrams = dict()

def update(config, values):
    global telegrams, url
    if url == "":
        url = "{}?".format(config["URL"])
    for device in values:
        name  = config[device]
        symbs = config["SYMB"].split()
        key   = config[config["{}.KEY".format(name)]]
        for symb in symbs:
            symbol = "{}.{}".format(name, symb)
            if symbol in config:
                field = "field{}={};".format(config[symbol], values[device][symb])
                val_key = "{}.{}.KEY".format(name, symb)
                if val_key in config:
                    key = config[config[val_key]]
                if key not in telegrams:
                    telegrams[key] = ""
                telegrams[key] = "{}{}".format(telegrams[key], field)

last_ret = "-"
last_exc = "-"
def format_status():
    return "ret:%20" + last_ret + "%20exc:%20" + last_exc

def send():
    global last_time, telegrams, url, last_ret, last_exc
    cur_time = time.time()
    for key in telegrams:
        if len(telegrams[key]) > 0 and (cur_time - last_time) > WAITTIME:
            try:
                telegram = "{}{}key={}".format(url, telegrams[key], key)
                if test and "field8" not in telegram:
                    telegram = "{};field8={:d}".format(telegram, gc.mem_free())
                    telegram = "{};status={}".format(telegram, format_status())
                r = requests.post(telegram)
                last_ret = r.text
                if last_ret == "0": # too many telegrams
                    last_exc = last_ret
                r.close() # this is important to avoid memory leaks!
            except Exception as e:
                last_exc = str(e)
                if test:
                    print(e)
            telegrams[key] = ""
            last_time = cur_time
