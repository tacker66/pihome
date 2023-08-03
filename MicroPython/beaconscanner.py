
import uasyncio as asyncio
import bluetooth
import aioble
import binascii
import thermobeacon
import Pico_LCD_114_V2

config = dict()
def read_config(file):
    fd = open(file)
    for line in fd:
        line = line.strip()
        if len(line) > 0 and line[0] != "#":
            tok = line.split("=")
            config[tok[0].strip()] = tok[1].strip()

devices = dict()
async def scan():
    async with aioble.scan(5000, interval_us=30000, window_us=30000, active=True) as scanner:
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

async def main():
    await scan()

values = dict()
read_config('beacons.conf')

disp = Pico_LCD_114_V2.LCD_114()

asyncio.run(main())
    
for device in devices:
    #print(devices[device]["name"], devices[device]["rssi"], devices[device]["connectable"], device)
    mid = devices[device]["manufacturer_id"]
    for data in sorted(devices[device]["manufacturer"]):
        #print(str(binascii.hexlify(data, ' '), "utf-8"))
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

for device in values:
    name = config[device]
    pos = int(config[name+".POS"])
    act = int(values[device]["ACT"])
    msg = "{:.1f} {:.1f} {:.1f} ({:d})".format(values[device]["TMP"], values[device]["HUM"], values[device]["BAT"], values[device]["ERR"])
    disp.display(pos, name, msg, False, act)
