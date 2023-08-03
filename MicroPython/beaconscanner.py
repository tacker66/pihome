
import uasyncio as asyncio
import bluetooth
import aioble
import binascii
import thermobeacon

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

print("=== scanning BLE devices ... ===")
asyncio.run(main())
    
for device in devices:
    print(devices[device]["name"], devices[device]["rssi"], devices[device]["connectable"], device)
    mid = devices[device]["manufacturer_id"]
    print("Manufacturer:", mid)
    for data in sorted(devices[device]["manufacturer"]):
        print("        Data:", str(binascii.hexlify(data, ' '), "utf-8"))
        print("             ", thermobeacon.decode(mid, data))

print("=== finished ===")
