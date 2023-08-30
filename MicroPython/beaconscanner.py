
test = 1

use_display   = 1
use_webserver = 1

import gc
import asyncio
import bluetooth
import aioble

import wifi
import thingspeak
import thermobeacon

if use_display:
    import display
if use_webserver:
    import webserver

# update interval for external displays
if test:
    SLOW_UPDTIME  = 120_000
else:
    SLOW_UPDTIME  = 1800_000
SENDTIME    = 2_000   # trigger interval for sending telegrams to external displays
FAST_UPDTIME= 60_000  # update interval for local displays
WIFITIME    = 30_000  # wifi check interval
SCANTIME    = 5_000   # duration of BLE scan
WAITTIME    = 15_000  # time to next BLE scan

config = dict()
def read_config(file):
    fd = open(file)
    for line in fd:
        line = line.strip()
        if len(line) > 0 and line[0] != "#":
            tok = line.split("=")
            config[tok[0].strip()] = tok[1].strip()
read_config('beacons.conf')

lock = asyncio.Lock()

devices = dict()
async def scan_devices():
    for device in devices:
        devices[device]["rssi"] = 0 # check if we have lost some devices
    async with aioble.scan(SCANTIME, interval_us=30000, window_us=30000, active=True) as scanner:
        async for result in scanner:
            device = result.device.addr_hex()
            if device in config:
                if device not in devices:
                    device_data = dict()
                    device_data["manufacturer_id"] = 0
                    device_data["manufacturer"]    = list()
                    devices[device] = device_data
                else:
                    device_data = devices[device]
                device_data["name"]        = result.name()
                device_data["rssi"]        = result.rssi
                device_data["connectable"] = result.connectable
                for data in result.manufacturer():
                    device_data["manufacturer_id"] = data[0]
                    device_data["manufacturer"].append(data[1])
            
values = dict()
async def calc_values():
    for device in values:
        values[device]["RSSI"] = devices[device]["rssi"] # local error indicator
        if values[device]["RSSI"] == 0:
            values[device]["BAT"] = 0 # external error indicator
    for device in devices:
        name = config[device]
        mid  = devices[device]["manufacturer_id"]
        while len(devices[device]["manufacturer"]):
            data = devices[device]["manufacturer"].pop(0)
            if device not in values:
                values[device] = dict()
                values[device]["TMP"] = 0
                values[device]["HUM"] = 0
                values[device]["BAT"] = 0
            values[device]["RSSI"] = devices[device]["rssi"]
            if thermobeacon.can_decode(mid, data):
                tmp, hum, bat = thermobeacon.decode(mid, data)
                off = "{}.TMP_OFF".format(name)
                if off in config:
                    tmp = tmp + float(config[off])
                off = "{}.TMP_OFF".format(name)
                if off in config:
                    hum = hum + float(config[off])
                values[device]["TMP"] = tmp
                values[device]["HUM"] = hum
                values[device]["BAT"] = bat

async def get_values():
    while True:
        await lock.acquire()
        await scan_devices()
        await calc_values()
        lock.release()
        gc.collect()
        if test:
            print("get_values", gc.mem_free())
        await asyncio.sleep_ms(WAITTIME)

async def show_fast_values():
    while True:
        await lock.acquire()
        if use_display:
            display.update(config, values)
        if use_webserver:
            webserver.update(config, values)
        lock.release()
        gc.collect()
        if test:
            print("show_fast_values", gc.mem_free())
        await asyncio.sleep_ms(FAST_UPDTIME)

async def show_slow_values():
    while True:
        await lock.acquire()
        thingspeak.update(config, values)
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
    webserver.start_webserver("BeaconScanner")
    gc.collect()
    if test:
        print("start_webserver", gc.mem_free())
    
async def check_wifi():
    while True:
        if not wifi.is_connected():
            display.update_border(errorlevel=2)
            if test:
                print("check_wifi: reconnect")
            wifi.connect(config["SSID"], config["PASS"], True)
        else:
            display.update_border(errorlevel=0)
        await asyncio.sleep_ms(WIFITIME)
    
async def main():
    wifi.connect(config["SSID"], config["PASS"])
    gc.collect()
    if test:
        print("main", gc.mem_free())
    if use_webserver:
        await asyncio.gather(
            start_webserver(),
            get_values(),
            show_fast_values(),
            show_slow_values(),
            send_values(),
            check_wifi(),
            )
    else:
        await asyncio.gather(
            get_values(),
            show_values(),
            send_values(),
            )
        
asyncio.run(main())
