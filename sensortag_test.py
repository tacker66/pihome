#!/usr/bin/env python

#
# Copyright 2013 Michael Saunby
# Copyright 2013 Thomas Ackermann
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#   http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#

#
# Read sensors from the TI SensorTag. It's a
# BLE (Bluetooth low energy) device so by
# automating gatttool (from BlueZ 5.9) with
# pexpect we are able to read and write values.
#
# Usage: sensortag_test.py BLUETOOTH_ADR
#
# To find the address of your SensorTag run 'sudo hcitool lescan'
# To power up your bluetooth dongle run 'sudo hciconfig hci0 up'
#

import sys
import time
import pexpect
from sensortag_funcs import *

# start gatttool
adr = sys.argv[1]
tool = pexpect.spawn('gatttool59 -b ' + adr + ' --interactive')
tool.expect('\[LE\]>')

# bug in pexpect? automating gatttool works only if we are using a logfile!
logfile = open("/dev/null", "w")
tool.logfile = logfile

# connect to SensorTag
print adr, " Trying to connect. You might need to press the side button ..."
tool.sendline('connect')
tool.expect('\[LE\]>')

print adr, " Enabling sensors ..."
# enable temperature sensor
tool.sendline('char-write-cmd 0x29 01')
tool.expect('\[LE\]>')

# enable humidity sensor
tool.sendline('char-write-cmd 0x3c 01')
tool.expect('\[LE\]>')

# enable barometric pressure sensor
tool.sendline('char-write-cmd 0x4f 02')
tool.expect('\[LE\]>')

tool.sendline('char-read-hnd 0x52')
tool.expect('descriptor: .*? \r')

after = tool.after
v = after.split()[1:] 
vals = [long(float.fromhex(n)) for n in v]
barometer = Barometer( vals )
tool.sendline('char-write-cmd 0x4f 01')
tool.expect('\[LE\]>')

# wait for the sensors to become ready
time.sleep(1)

cnt = 0
while True:

    cnt = cnt + 1
    print adr, " CNT %d" % cnt

    # read temperature sensor
    tool.sendline('char-read-hnd 0x25')
    tool.expect('descriptor: .*? \r') 
    v = tool.after.split()
    rawObjT = long(float.fromhex(v[2] + v[1]))
    rawAmbT = long(float.fromhex(v[4] + v[3]))
    (at, it) = calcTmp(rawAmbT, rawObjT)

    # read humidity sensor
    tool.sendline('char-read-hnd 0x38')
    tool.expect('descriptor: .*? \r') 
    v = tool.after.split()
    rawT = long(float.fromhex(v[2] + v[1]))
    rawH = long(float.fromhex(v[4] + v[3]))
    (ht, h) = calcHum(rawT, rawH)

    # read barometric pressure sensor
    tool.sendline('char-read-hnd 0x4B')
    tool.expect('descriptor: .*? \r') 
    v = tool.after.split()
    rawT = long(float.fromhex(v[2] + v[1]))
    rawP = long(float.fromhex(v[4] + v[3]))
    (pt, p) = barometer.calc(rawT, rawP)

    print adr, " IRTMP %.1f" % it
    print adr, " AMTMP %.1f" % at
    print adr, " HMTMP %.1f" % ht
    print adr, " BRTMP %.1f" % pt
    print adr, " HUMID %.0f" % h
    print adr, " BAROM %.0f" % p

    data = open("/home/pi/tmp/pihome/"+adr, "w")
    data.write("IRTMP %.1f\n" % it)
    data.write("AMTMP %.1f\n" % at)
    data.write("HMTMP %.1f\n" % ht)
    data.write("BRTMP %.1f\n" % pt)
    data.write("HUMID %.0f\n" % h)
    data.write("BAROM %.0f\n" % p)
    data.close()

    time.sleep(30)

