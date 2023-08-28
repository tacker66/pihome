
# https://thingspeak.com/

test = 1

import time
import urequests as requests

if test:
    import gc

WAITTIME = 20 # thingspeak only allows ~8.200 messages per day; messages cannot be sent faster than every 10.6 seconds

url = ""
last_time = 0
telegram_list = list()

def update(config, values):
    global telegram_list, url
    if url == "":
        url = "{}?".format(config["URL"])
    for device in values:
        send_values = dict()
        name  = config[device]
        symbs = config["SYMB"].split()
        key   = config[config["{}.KEY".format(name)]]
        send_values["key"] = key
        for symb in symbs:
            value = values[device][symb]
            field_name = "field{}".format(config["{}.{}".format(name, symb)])
            send_values[field_name] = value
        telegram = ""
        for send_value in send_values:
            telegram = "{}{}={};".format(telegram, send_value, send_values[send_value])
        telegram_list.append(telegram)
        
def send():
    global last_time, telegram_list, url
    cur_time = time.time()
    if len(telegram_list) > 0 and (cur_time - last_time) > WAITTIME:
        if test:
            try:
                telegram = "{}{};field7={:d};field8={:d}".format(url, telegram_list.pop(0), gc.mem_alloc(), gc.mem_free())
                r = requests.post(telegram)
                r.close() # this is important to avoid memory leaks!
            except Exception as e:
                print(e)
        else:
            try:
                telegram = "{}{}".format(url, telegram_list.pop(0))
                r = requests.post(telegram)
                r.close() # this is important to avoid memory leaks!
            except:
                pass
        last_time = cur_time
