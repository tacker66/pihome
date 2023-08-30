
# https://thingspeak.com/

test = 1

import time
import urequests as requests

if test:
    import gc

WAITTIME = 20 # thingspeak only allows ~8.200 messages per day; messages cannot be sent faster than every 10.6 seconds

url = ""
last_time = 0
telegrams = dict()

def update(config, values):
    global telegrams, url
    if url == "":
        url = "{}?".format(config["URL"])
    for device in values:
        send_values = dict()
        name  = config[device]
        symbs = config["SYMB"].split()
        key   = config[config["{}.KEY".format(name)]]
        if key not in telegrams:
            telegrams[key] = ""
        for symb in symbs:
            value = values[device][symb]
            field_name = "field{}".format(config["{}.{}".format(name, symb)])
            send_values[field_name] = value
        telegram = ""
        for send_value in send_values:
            telegram = "{}{}={};".format(telegram, send_value, send_values[send_value])
        telegrams[key] = "{}{}".format(telegrams[key], telegram)
        
def send():
    global last_time, telegrams, url
    cur_time = time.time()
    for key in telegrams:
        if len(telegrams[key]) > 0 and (cur_time - last_time) > WAITTIME:
            if test:
                try:
                    telegram = "{}{}key={};field7={:d};field8={:d}".format(url, telegrams[key], key, gc.mem_alloc(), gc.mem_free())
                    print(telegram)
                    r = requests.post(telegram)
                    r.close() # this is important to avoid memory leaks!
                except Exception as e:
                    print(e)
            else:
                try:
                    telegram = "{}{}key={}".format(url, telegrams[key], key)
                    print(telegram)
                    r = requests.post(telegram)
                    r.close() # this is important to avoid memory leaks!
                except:
                    pass
            telegrams[key] = ""
            last_time = cur_time
