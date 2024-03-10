
test = 1

import gc
import asyncio

import configs
import wifi
import ez1
import awtrix
import led
import webserver
import thingspeak

# indicate wifi-not-connected status
led.update(1)

# update interval for external displays
if test:
    SLOW_UPDTIME = 120_000
    FAST_UPDTIME = 20_000  # update interval for local displays
    WAITTIME     = 30_000  # time to next pv read
else:
    SLOW_UPDTIME = 420_000
    FAST_UPDTIME = 42_000  # update interval for local displays
    WAITTIME     = 210_000 # time to next pv read
SENDTIME    = 20_000  # trigger interval for re-sending telegrams to external displays
WIFITIME    = 20_000  # wifi check interval

config = configs.read_config('power.conf')

pv = dict()
pv["POWER1"] = 0
pv["POWER2"] = 0
pv["POWER"]  = 0
pv["ENERGY"] = 0
pv["ERROR"]  = 0
pv["ALARMS"] = ""
pv["EXCEPT"] = ""
pv["ENERGYYEAR"] = 0

ez1.init(config, pv)
awtrix.init(config, pv)

lock = asyncio.Lock()

async def get_values():
    while True:
        await lock.acquire()
        ez1.update(config, pv)
        lock.release()
        gc.collect()
        if test:
            print("get_values", gc.mem_free())
            print(pv)
        await asyncio.sleep_ms(WAITTIME)

async def show_fast_values():
    while True:
        await lock.acquire()
        awtrix.update(config, pv)
        webserver.update(config, pv)
        lock.release()
        gc.collect()
        if test:
            print("show_fast_values", gc.mem_free())
        await asyncio.sleep_ms(FAST_UPDTIME)

async def show_slow_values():
    while True:
        await lock.acquire()
        thingspeak.pre_update(config, pv)
        thingspeak.update(config, pv)
        lock.release()
        gc.collect()
        if test:
            print("show_slow_values", gc.mem_free())
        await asyncio.sleep_ms(SLOW_UPDTIME)

async def send_values():
    while True:
        thingspeak.send()
        gc.collect()
        await asyncio.sleep_ms(SENDTIME)
        
async def start_webserver():
    webserver.start_webserver("PV Monitor")
    
async def check_wifi():
    while True:
        if not wifi.is_connected():
            led.update(1)
            if test:
                print("check_wifi: reconnect")
            wifi.connect(config["SSID"], config["PASS"], True)
        else:
            led.update(0)
        await asyncio.sleep_ms(WIFITIME)
    
async def main():
    wifi.connect(config["SSID"], config["PASS"])
    gc.collect()
    if test:
        print("main", gc.mem_free())
    await asyncio.gather(
        start_webserver(),
        get_values(),
        show_fast_values(),
        show_slow_values(),
        send_values(),
        check_wifi(),
        )
        
asyncio.run(main())
