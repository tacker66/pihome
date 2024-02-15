
# https://thingspeak.com/

import gc
import time
import requests

WAITTIME = 20   # thingspeak only allows ~8.200 messages per day so
                # messages cannot be sent faster than every 10.6 seconds;
                # otherwise r.text == "0" will be returned

url = ""
last_time = 0
telegrams = dict()

last_stat = "-"
def update(config, values):
    global telegrams, url, last_stat
    if url == "":
        url = "{}?".format(config["URL"])
    name  = "pv"
    symbs = config["SYMB"].split()
    key   = config[config["{}.KEY".format(name)]]
    stat  = ""
    for symb in symbs:
        symbol = "{}.{}".format(name, symb)
        if symbol in config:
            if config[symbol] != "S":
                field = "field{}={};".format(config[symbol], values[symb])
                val_key = "{}.{}.KEY".format(name, symb)
                if val_key in config:
                    key = config[config[val_key]]
                if key not in telegrams:
                    telegrams[key] = ""
                telegrams[key] = "{}{}".format(telegrams[key], field)
            else:
                stat = stat + values[symb] + " "
    last_stat = stat
    
last_ret = "-"
last_exc = "-"
cnt_exc  = 0
def format_status():
    msg = "ret: " + last_ret + " cnt: " + str(cnt_exc) + " exc: " + last_exc  + " " + last_stat
    msg = msg.replace("\n", " ")
    msg = msg.replace("\t", " ")
    msg = msg.replace(" ", "%20")
    return msg

def send():
    global last_time, telegrams, url, last_ret, last_exc, cnt_exc
    cur_time = time.time()
    for key in telegrams:
        if len(telegrams[key]) > 0 and (cur_time - last_time) > WAITTIME:
            try:
                telegram = "{}{}key={}".format(url, telegrams[key], key)
                if "field8" not in telegram:
                    telegram = "{};field8={:d}".format(telegram, gc.mem_free())
                    telegram = "{};status={}".format(telegram, format_status())
                r = requests.post(telegram)
                last_ret = r.text
                if last_ret == "0": # too many telegrams
                    last_exc = last_ret
                cnt_exc = 0
                r.close() # this is important to avoid memory leaks!
            except Exception as e:
                last_exc = str(e)
                cnt_exc += 1
            telegrams[key] = ""
            last_time = cur_time
