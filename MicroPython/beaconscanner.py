
import uasyncio as asyncio
import bluetooth
import aioble
import binascii

import thermobeacon
import Pico_LCD_114_V2
import webserver
import thingspeak

test = 1

if test:
    SCANTIME = 5_000
    WAITTIME = 15_000
    UPDTIME  = 120_000
else:
    SCANTIME = 10_000
    WAITTIME = 300_000
    UPDTIME  = 1800_000
SNDTIME  = 2_000

# start with clean memory
import gc
gc.collect()

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
    async with aioble.scan(SCANTIME, interval_us=30000, window_us=30000, active=True) as scanner:
        async for result in scanner:
            device = result.device.addr_hex()
            if device not in devices:
                device_data = dict()
                device_data["manufacturer_id"] = 0
                device_data["manufacturer"]    = set()
                devices[device] = device_data
            else:
                device_data = devices[device]
            device_data["name"]        = result.name()
            device_data["rssi"]        = result.rssi
            device_data["connectable"] = result.connectable
            device_data["manufacturer"].clear() # clear values from last scan; otherwise the set would grow indefinitely
            for data in result.manufacturer():
                device_data["manufacturer_id"] = data[0]
                device_data["manufacturer"].add(data[1])
            
values = dict()
async def calc_values():
    for device in devices:
        #print(devices[device]["name"], devices[device]["rssi"], devices[device]["connectable"], device)
        mid = devices[device]["manufacturer_id"]
        for data in devices[device]["manufacturer"]:
            #print(mid, str(binascii.hexlify(data, ' '), "utf-8"))
            if device in config:
                name = config[device]
                if device not in values:
                    values[device] = dict()
                    values[device]["ERR"] = 0
                    values[device]["ACT"] = 0
                    values[device]["TMP"] = 0
                    values[device]["HUM"] = 0
                    values[device]["BAT"] = 0
                if thermobeacon.can_decode(mid, data):
                    tmp, hum, bat = thermobeacon.decode(mid, data)
                    off = name + ".TMP_OFF"
                    if off in config:
                        tmp = tmp + float(config[off])
                    off = name + ".HUM_OFF"
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
        print("GET", gc.mem_free())
        await asyncio.sleep_ms(WAITTIME)

disp = Pico_LCD_114_V2.LCD_114()
async def show_values():
    while True:
        await lock.acquire()
        for device in values:
            name = config[device]
            pos = int(config[name+".POS"])
            act = int(values[device]["ACT"])
            msg = "{:.1f} {:.1f} {:.1f} ({:d})".format(values[device]["TMP"], values[device]["HUM"], values[device]["BAT"], values[device]["ERR"])
            disp.display(pos, name, msg, False, act)
            print(device, name, values[device])
        webserver.update(config, values)
        thingspeak.update(config, values)
        lock.release()
        gc.collect()
        print("SHOW", gc.mem_free())
        await asyncio.sleep_ms(UPDTIME)

async def send_values():
    while True:
        thingspeak.send()
        gc.collect()
        #print("SEND", gc.mem_free())
        await asyncio.sleep_ms(SNDTIME)
        
async def start_webserver():
    webserver.start_webserver("BeaconScanner")
    
async def main():
    webserver.wlan_connect(config["SSID"], config["PASS"])
    await asyncio.gather(
        start_webserver(),
        get_values(),
        show_values(),
        send_values(),
        )

asyncio.run(main())
