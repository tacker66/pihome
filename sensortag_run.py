#!/usr/bin/env python

#
# Copyright 2013 Michael Saunby
# Copyright 2013-2016 Thomas Ackermann
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
# automating gatttool (from BlueZ 5.42) with
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
from datetime import datetime

from sensortag_funcs import *

adr = sys.argv[1]

logdir = "/tmp/pihome"
try:
    os.mkdir(logdir)
except:
    pass

ht = 0
pt = 0
hu = 0
pr = 0
exc = 0
act = 0
post = ""
stamp = ""
handle = ""

def log_values():
    print adr, "  POST 0x%s" % post
    print adr, " HMTMP %.1f" % ht
    print adr, " BRTMP %.1f" % pt
    print adr, " AVTMP %.1f" % ((ht + pt) / 2)
    print adr, " HUMID %.0f" % hu
    print adr, " BAROM %.0f" % pr
    print adr, " EXCPT %d" % exc
    print adr, " ACTEX %d" % act
    print adr, " STAMP '%s'" % stamp
    data = open(logdir+"/"+adr, "w")
    data.write(" POST 0x%s\n" % post)
    data.write("HMTMP %.1f\n" % ht)
    data.write("BRTMP %.1f\n" % pt)
    data.write("AVTMP %.1f\n" % ((ht + pt) / 2))
    data.write("HUMID %.0f\n" % hu)
    data.write("BAROM %.0f\n" % pr)
    data.write("EXCPT %d\n" % exc)
    data.write("ACTEX %d\n" % act)
    data.write("STAMP '%s'\n" % stamp)
    data.close()

def enable_sensors():
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
    global barometer
    barometer = Barometer( vals )
    tool.sendline('char-write-req 0x55 01')
    tool.expect('\[LE\]>')

def disable_sensors():
    # disable humidity sensor
    tool.sendline('char-write-req 0x3f 00')
    tool.expect('\[LE\]>')
    # disable barometric pressure sensor
    tool.sendline('char-write-req 0x55 00')
    tool.expect('\[LE\]>')

while True:

    try:

        print adr, " Trying to connect. You might need to press the side button ..."

        tool = pexpect.spawn('gatttool542 -b ' + adr + ' --interactive')
        tool.expect('\[LE\]>')
        tool.sendline('connect')
        tool.expect('success')

        print adr, " Switching to a lower energy connection ..."

        # gatttool not really connects with enough 'low energy' so reconfigure
        # the connection to the values preferred by SensorTag (see characteristic 0x2A04):
        # i.e. min interval to 100ms and max interval to 200ms.
        # By this the current needed for 'just being connected' in the SensorTag 
        # drops from 0.35mA to 0.01mA.
        cons = pexpect.run('hcitool con')
        cons = cons.split("\r\n")
        for con in cons:
            if adr in con:
                tok = con.split()
                handle = tok[4]
                state = tok[6]
                error = pexpect.run('sudo hcitool lecup --handle ' + handle + ' --min 80 --max 160')
                if error <> "":
                    print "hcittool error: '" + error + "' (handle: " + handle + ", state: " + state + ")"

        wait_timer = 0
        duty_timer = 0
        #wait_cycle = 3600
        wait_cycle = 300
        duty_cycle = 30

        while True:

            start = time.time()

            if wait_timer <= 0:
                wait_timer = wait_cycle
                duty_timer = duty_cycle
                print adr, " Enabling sensors ..."
                enable_sensors()
                # wait for the sensors to become ready
                time.sleep(1)

            print adr, " Life tick ..."
            # read POST result
            tool.sendline('char-read-hnd 0x70')
            tool.expect('descriptor: .*? \r') 
            v = tool.after.split()
            post = v[1]

            if duty_timer > 0:
                print adr, " Reading sensors ..."
                # read humidity sensor
                tool.sendline('char-read-hnd 0x3b')
                tool.expect('descriptor: .*? \r') 
                v = tool.after.split()
                rawT = long(float.fromhex(v[2] + v[1]))
                rawH = long(float.fromhex(v[4] + v[3]))
                (ht, hu) = calcHum(rawT, rawH)
                # read barometric pressure sensor
                tool.sendline('char-read-hnd 0x51')
                tool.expect('descriptor: .*? \r') 
                v = tool.after.split()
                rawT = long(float.fromhex(v[2] + v[1]))
                rawP = long(float.fromhex(v[4] + v[3]))
                (pt, pr) = barometer.calc(rawT, rawP)
                stamp = datetime.now().ctime()
                act = 0
                log_values()

            # SensorTag's preferred supervision timeout is 10000ms (see characteristic 0x2A04)
            time.sleep(10)

            elapsed = int(time.time() - start)
            wait_timer = wait_timer - elapsed
            if duty_timer > 0:
                duty_timer = duty_timer - elapsed
                if duty_timer < 0:
                    print adr, " Disabling sensors ..."
                    disable_sensors()
                    duty_timer = 0

    except KeyboardInterrupt:
        tool.sendline('quit')
        tool.close()
        sys.exit()

    except:
        if handle != "":
            pexpect.run('sudo hcitool ledc ' + handle)
        tool.sendline('quit')
        tool.close(force=True)
        exc = exc + 1
        act = 1
        log_values()

