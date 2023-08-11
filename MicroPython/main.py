
print("=== main.py ===")

import micropython
micropython.opt_level(3)

exec(open("beaconscanner.py").read(), globals())
#exec(open("rpi_boot.py").read(), globals())

print("=== finished ===")
