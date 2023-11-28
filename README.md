pihome
======

Environmental monitoring using Raspberry Pi B, Raspberry Pi Pico W,
TI SensorTags and BLE ThermoBeacons.

See './MicroPython' for a MicroPython-based solution which uses only
BLE Beacon sensors (i.e. which radiate all important data directly in their Advertsising data). This was featured in [MagPi #136 p26](https://magpi.raspberrypi.com/issues/136).

See [blescan.py](https://github.com/tacker66/mp_playground/blob/main/blescan.py) for a
MicroPython based BLE Characteristic discovery.

See './INSTALL' and 'sensortag*.py' for a Bluez/pexpect-based solution using Raspberry Pi B and TI SensorTags.

See './Test/ble_discover.py' for a Bluez/pexpect-based BLE Characteristic discovery.
