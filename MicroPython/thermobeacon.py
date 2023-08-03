
# https://github.com/rnlgreen/thermobeacon

import struct

def can_decode(mid, data):
    if mid == 16 and len(data) == 18:
        return True
    return False

def decode(mid, data):
    if mid == 16 and len(data) == 18:
        m8, m7, m6, m5, m4, m3, m2, m1, volt, temp_raw, hum_raw = struct.unpack('BBBBBBBBHHH', data)
        temp = temp_raw / 16.0
        hum  = hum_raw / 16.0
        volt = volt / 1000.0
        return temp, hum, volt
    return -1, -1, -1
