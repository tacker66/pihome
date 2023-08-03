pihome
======

Environmental monitoring for my house using a Raspberry Pi, 
two TI SensorTags and an Arduino or TI Launchpad together with
a RedBearLab BLE Mini bluetooth radio.

While this project is currently far from being completed,
files './INSTALL', './Test/*.py' and the sketches in './Arduino' 
and './Launchpad' might help as a starting point for your own experiments.
(See esp. ./Test/ble_discover.py which provides a complete
characteristic discovery of a BLE device.)

See './MicroPython' for a next-gen MicroPython-based solution which is intended to use only BLE Beacon based sensors (i.e. which radiate all important data directly in their Advertsising data).
