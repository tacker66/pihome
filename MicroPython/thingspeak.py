
# https://thingspeak.com/

test = 1

import time
import requests

import gc

WAITTIME = 20 # thingspeak only allows ~8.200 messages per day; messages cannot be sent faster than every 10.6 seconds

url = ""
last_time = 0
telegram_list = list()

def update(config, values):
    global telegram_list, url
    if url == "":
        url = config["URL"] + "?"
    for device in values:
        send_values = dict()
        name  = config[device]
        symbs = config["SYMB"].split()
        key   = config[config[name + ".KEY"]]
        send_values["key"] = key
        for symb in symbs:
            value = values[device][symb]
            field_name = "field" + config[name + "." + symb]
            send_values[field_name] = str(value)
        telegram = ""
        for send_value in send_values:
            telegram = telegram + send_value + "=" + send_values[send_value] + ";"
        telegram_list.append(telegram)
        
def send():
    global last_time, telegram_list, url
    cur_time = time.time()
    if len(telegram_list) > 0 and (cur_time - last_time) > WAITTIME:
        telegram = url + telegram_list.pop(0)
        if test:
            try:
                r = requests.post(telegram)
                print(str(len(telegram_list)) + " " + str(r.status_code) + " " + r.text)
            except:
                print("Error")
        else:
            try:
                requests.post(telegram)
            except:
                print("Error")
        last_time = cur_time
