
test = 1

if test:
    # 173344 v1.20.0-348-g24a6e951e on 2023-08-10
    import gc
    gc.collect()
    print("MEM", gc.mem_free())

    # 753664 v1.20.0-348-g24a6e951e on 2023-08-10
    import os
    s = os.statvfs('//')
    print("FLASH", s[0]*s[3])
else:
    exec(open("beaconscanner.py").read(), globals())
