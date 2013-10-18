#!/usr/bin/env python

#
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
# Read digital inputs from an Arduino connected to a RedBearLabs BLEmini. 
# BLEmini is a BLE (Bluetooth low energy) device so by
# automating gatttool (from BlueZ 5.9) with
# pexpect we are able to read and write values.
#
# Usage: blemini_test.py BLUETOOTH_ADR
#
# To find the address of your BLEmini run 'sudo hcitool lescan'
# To power up your bluetooth dongle run 'sudo hciconfig hci0 up'
#

import sys
import time
import pexpect

# start gatttool
adr = sys.argv[1]
tool = pexpect.spawn('gatttool59 -b ' + adr + ' --interactive')
tool.expect('\[LE\]>')

# bug in pexpect? automating gatttool works only if we are using a logfile!
logfile = open("/dev/null", "w")
tool.logfile = logfile

# connect to BLEmini
print adr, " Trying to connect ..."
tool.sendline('connect')
tool.expect('\[LE\]>')

cnt = 0
while True:

    cnt = cnt + 1
    print adr, " CNT %d" % cnt

    # trigger a latch of digital inputs on Arduino
    tool.sendline('char-write-cmd 0x19 00')
    tool.expect('\[LE\]>')
    
    # read digital input values from Arduino
    tool.sendline('char-read-hnd 0x15')
    tool.expect('descriptor: .*? \r') 
    v = tool.after.split()
    data = long(float.fromhex(v[2] + v[1]))

    print adr, " DATA 0x%4x" % data

    data = open("/home/pi/tmp/pihome/"+adr, "w")
    data.write("DATA 0x%4x" % data)
    data.close()

    time.sleep(10)
