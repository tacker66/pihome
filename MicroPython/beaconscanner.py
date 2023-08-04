
import uasyncio as asyncio
import bluetooth
import aioble
import binascii
import thermobeacon
import Pico_LCD_114_V2
import webserver

config = dict()
def read_config(file):
    fd = open(file)
    for line in fd:
        line = line.strip()
        if len(line) > 0 and line[0] != "#":
            tok = line.split("=")
            config[tok[0].strip()] = tok[1].strip()
read_config('beacons.conf')

write_lock = asyncio.Lock()

SCANTIME  = 5000
SLEEPTIME = 5000
DISPTIME  = 5000

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
            device_data["name"] = result.name()
            device_data["rssi"] = result.rssi
            device_data["connectable"] = result.connectable
            for data in result.manufacturer():
                device_data["manufacturer_id"] = data[0]
                device_data["manufacturer"].add(data[1])
        
values = dict()
async def calc_values():
    for device in devices:
        #print(devices[device]["name"], devices[device]["rssi"], devices[device]["connectable"], device)
        mid = devices[device]["manufacturer_id"]
        for data in sorted(devices[device]["manufacturer"]):
            #print(mid, str(binascii.hexlify(data, ' '), "utf-8"))
            if device in config:
                if device not in values:
                    values[device] = dict()
                    values[device]["ERR"] = 0
                    values[device]["ACT"] = 0
                if thermobeacon.can_decode(mid, data):
                    tmp, hum, bat = thermobeacon.decode(mid, data)
                    values[device]["TMP"] = tmp
                    values[device]["HUM"] = hum
                    values[device]["BAT"] = bat

async def get_values():
    while True:
        await write_lock.acquire()
        await scan_devices()
        await calc_values()
        write_lock.release()
        await asyncio.sleep_ms(SLEEPTIME)

disp = Pico_LCD_114_V2.LCD_114()
async def display_values():
    while True:
        while write_lock.locked():
            await asyncio.sleep(1)
        for device in values:
            name = config[device]
            print(device, name, values[device])
            pos = int(config[name+".POS"])
            act = int(values[device]["ACT"])
            msg = "{:.1f} {:.1f} {:.1f} ({:d})".format(values[device]["TMP"], values[device]["HUM"], values[device]["BAT"], values[device]["ERR"])
            disp.display(pos, name, msg, False, act)
        await asyncio.sleep_ms(DISPTIME)
        webserver.update_index(config, values)
        await asyncio.sleep_ms(DISPTIME)

async def start_webserver():
    webserver.wlan_connect(config["SSID"], config["PASS"])
    webserver.start_webserver("BeaconScanner")
    
async def main():
    await asyncio.gather(
        get_values(),
        display_values(),
        start_webserver()
        )

asyncio.run(main())
