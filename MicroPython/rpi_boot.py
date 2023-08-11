
print("=== rpi_boot.py ===")

import gc
import uos as os
import uerrno as errno
import time
import machine
import micropython

start = ""
#start = "beaconscanner.py"

MACHINEFREQ = 125_000_000
#machine.freq(MACHINEFREQ)

#micropython.opt_level(3)

def reset_cause():
    rc = machine.reset_cause()
    if rc == machine.PWRON_RESET:
        return "PWRON_RESET"
    elif rc == machine.WDT_RESET:
        return "WDT_RESET"
    elif machine.DEEPSLEEP_RESET:
        return "DEEPSLEEP_RESET"
    elif machine.SOFT_RESET:
        return "SOFT_RESET"
    else:
        return "UNKNOWN RESET CAUSE"

print("Reset cause", reset_cause())

print("Enable a Debugger to connect ...")
from time import sleep
from machine import Pin
led = Pin("LED", Pin.OUT)
led.value(1)
sleep(3)
led.value(0)

IS_DIR = 0x4000
IS_REGULAR = 0x8000

print('{0} MHz clock frequeny'.format(machine.freq()/1000000))
micropython.mem_info()
s = os.statvfs('//')
print('{0} MB free flash memory'.format((s[0]*s[3])/1048576))

found = False
iter = os.ilistdir()
while True:
    try:
        entry = next(iter)
        filename = entry[0]
        filetype = entry[1]
        if filetype == IS_REGULAR:
            print("FILE", filename)
            if filename == start:
                found = True
        if filetype == IS_DIR:
            print(" DIR", filename)
    except StopIteration:
        break

if found:
    print("=== exec", start, "===")
    exec(open(start).read(), globals())

print("=== finished ===")
