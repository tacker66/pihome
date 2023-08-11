
# https://thingspeak.com/

import time
import requests

import gc

WAITTIME = 15 # thingspeak only allows ~8.200 messages per day; messages cannot be sent faster than every 10.6 seconds

telegram_list = list()

def update(config, values):
    global telegram_list
    for device in values:
        send_values = dict()
        name  = config[device]
        symbs = config["SYMB"].split()
        key   = config[config[name + ".KEY"]]
        send_values["api_key"] = key
        for symb in symbs:
            value = values[device][symb]
            field_name = "field" + config[name + "." + symb]
            send_values[field_name] = str(value)
        url = config["URL"] +  "?"
        for send_value in send_values:
            url = url + send_value + "=" + send_values[send_value] + ";"
        telegram_list.append(url)
        
last_time = 0

def send():
    global last_time, telegram_list
    cur_time = time.time()
    if len(telegram_list) > 0 and (cur_time - last_time) > WAITTIME:
        telegram = telegram_list.pop(0)
        print(len(telegram_list), "SEND", telegram)
        try:
            r = requests.post(telegram)
            log = str(r.status_code) + " " + r.text
        except:
            log = "Error"
        print(log)
        last_time = cur_time
