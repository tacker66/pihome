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
# Usage:
#  sensortag_test.py BLUETOOTH_ADR
# 
# Read temperature from the TMP006 sensor in the TI SensorTag 
# It's a BLE (Bluetooth low energy) device so use gatttool (from bluez V5.4)
# to read and write values. 
#
# To find the address of your SensorTag run 'sudo hcitool lescan'
# You'll need to press the side button to enable discovery.
#

import sys
import time
import pexpect
from sensortag_funcs import *

bluetooth_adr = sys.argv[1]
tool = pexpect.spawn('gatttool54 -b ' + bluetooth_adr + ' --interactive')
tool.expect('\[LE\]>')
print "Preparing to connect. You might need to press the side button..."
tool.sendline('connect')
tool.expect('\[CON\].*>')

tool.sendline('char-write-cmd 0x29 01')
tool.expect('\[LE\]>')
# wait a second for the sensor to become ready
time.sleep(1)

cnt = 0

while True:
    cnt = cnt + 1
    print "CNT %d" % cnt
    tool.sendline('char-read-hnd 0x25')
    tool.expect('descriptor: .*') 
    rval = tool.after.split()
    objT = floatfromhex(rval[2] + rval[1])
    ambT = floatfromhex(rval[4] + rval[3])
    print "IRTMP %.2f C" % calcIRTmpTarget(objT, ambT)
    print "AMTMP %.2f C" % calcAmbTmpTarget(objT, ambT)
    time.sleep(30)
