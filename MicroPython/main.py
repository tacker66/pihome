
import gc
gc.collect()
#print(gc.mem_free())

exec(open("beaconscanner.py").read(), globals())
