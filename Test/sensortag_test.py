#!/usr/bin/env python

#
# Copyright 2013 Michael Saunby
# Copyright 2013-2014 Thomas Ackermann
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
# automating gatttool (from BlueZ 5.14) with
# pexpect (3.1) we are able to read and write values.
#
# Usage: sensortag_test.py BLUETOOTH_ADR
#
# To find the address of your SensorTag run 'sudo hcitool lescan'
# To power up your bluetooth dongle run 'sudo hciconfig hci0 up'
#

#
# SensorTag v1.5 handle ranges 
# (discovered by 'primary' resp. 'characteristic' cmd in gatttool):
#
#   Temperature: 0x23 - 0x2d (set 0x29 = 01; read 0x25)
# Accelerometer: 0x2e - 0x38
#      Humidity: 0x39 - 0x43 (set 0x3f = 01; read 0x3b)
#  Magnetometer: 0x44 - 0x4e
#     Barometer: 0x4f - 0x5d (set 0x55 = 01/02; read 0x51/0x5b)
#     Gyroscope: 0x5e - 0x68
#          Keys: 0x69 - 0x6d
#          Test: 0x6e - 0x74 (POST = 0x70; bits: 0 0 gyro press acc mag hum temp, 
#                                                0x3f means "OK"
#

import os
import sys
import time
import pexpect

sys.path.append('../.')
from sensortag_funcs import *

adr = sys.argv[1]

print adr, " Trying to connect. You might need to press the side button ..."

tool = pexpect.spawn('gatttool514 -b ' + adr + ' --interactive', timeout=60)
tool.expect('\[LE\]>')
tool.sendline('connect')
tool.expect('success')

print adr, " Switching to a lower energy connection ..."

# gatttool not really connects with enough 'low energy' so reconfigure
# the connection by setting min interval to 37.5ms, max interval 
# to 75ms and timeout to 30s. By this the current needed for 
# 'just being connected' in the SensorTag drops from 0.35mA to 0.05mA.
cons = pexpect.run('hcitool con')
cons = cons.split("\r\n")
for con in cons:
  if adr in con:
    handle = con.split()[4]
    error = pexpect.run('sudo hcitool lecup --handle ' + handle + ' --min 30 --max 60 --timeout 3000')
    if error <> "":
      print "hcittool error: " + error

print adr, " Enabling sensors ..."

# enable temperature sensor
tool.sendline('char-write-req 0x29 01')
tool.expect('\[LE\]>')

# enable humidity sensor
tool.sendline('char-write-req 0x3f 01')
tool.expect('\[LE\]>')

# enable barometric pressure sensor
tool.sendline('char-write-req 0x55 02')
tool.expect('\[LE\]>')

tool.sendline('char-read-hnd 0x5b')
tool.expect('descriptor: .*? \r')

after = tool.after
v = after.split()[1:] 
vals = [long(float.fromhex(n)) for n in v]
barometer = Barometer( vals )

tool.sendline('char-write-req 0x55 01')
tool.expect('\[LE\]>')

# wait for the sensors to become ready
time.sleep(1)

# create output directory
try:
  os.mkdir("/tmp/pihome")
except:
  pass

cnt = 0
while True:

    # read POST result
    tool.sendline('char-read-hnd 0x70')
    tool.expect('descriptor: .*? \r') 
    v = tool.after.split()
    post = v[1]

    cnt = cnt + 1
    print adr, " CNT %d (POST 0x%s)" % (cnt, post)

    # read temperature sensor
    tool.sendline('char-read-hnd 0x25')
    tool.expect('descriptor: .*? \r') 
    v = tool.after.split()
    rawObjT = long(float.fromhex(v[2] + v[1]))
    rawAmbT = long(float.fromhex(v[4] + v[3]))
    (at, it) = calcTmp(rawAmbT, rawObjT)

    # read humidity sensor
    tool.sendline('char-read-hnd 0x3b')
    tool.expect('descriptor: .*? \r') 
    v = tool.after.split()
    rawT = long(float.fromhex(v[2] + v[1]))
    rawH = long(float.fromhex(v[4] + v[3]))
    (ht, h) = calcHum(rawT, rawH)

    # read barometric pressure sensor
    tool.sendline('char-read-hnd 0x51')
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

    data = open("/tmp/pihome/"+adr, "w")
    data.write(" POST %s\n" % post)
    data.write("IRTMP %.1f\n" % it)
    data.write("AMTMP %.1f\n" % at)
    data.write("HMTMP %.1f\n" % ht)
    data.write("BRTMP %.1f\n" % pt)
    data.write("HUMID %.0f\n" % h)
    data.write("BAROM %.0f\n" % p)
    data.close()

    time.sleep(10)


