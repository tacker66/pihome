
# https://thingspeak.com/

import urequests

def update(config, values):
    send_values = dict()
    for device in values:
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
    print(url)
    log = ""
    try:
        r = urequests.post(url)
        log = str(r.status_code) + " " + r.text
    except:
        log = "Error"
    print(log)
