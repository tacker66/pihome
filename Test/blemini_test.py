#!/usr/bin/env python

#
# Copyright 2013-2015 Thomas Ackermann
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
# Read digital inputs from a RedBearLabs BLEmini. 
# BLEmini is a BLE (Bluetooth low energy) device so by
# automating gatttool (from BlueZ 5.18) with
# pexpect (3.1) we are able to read and write values.
#
# Usage: blemini_test.py BLUETOOTH_ADR
#
# To find the address of your BLEmini run 'sudo hcitool lescan'
# To power up your bluetooth dongle run 'sudo hciconfig hci0 up'
#

#
# BLEMini Biscuit v2.0 handles
# (discovered by 'primary' resp. 'characteristic' cmd in gatttool):
#
# 0x12: read list of bytes transferred to BLEMini via serial connection
# 0x16: write byte to BLEMini to be received via serial connection
# 0x19: set baudrate for serial port (value is remanent; possible values are: 
#                      00=9600, 01=19200, 02=38400, 03=57600(default), 04=115200)
#

import os
import sys
import time
import random
import pexpect
from datetime import datetime

adr = sys.argv[1]

logdir = "/tmp/pihome"
try:
  os.mkdir(logdir)
except:
  pass

cnt = 0
rnd = 0
val = 0
err = 0
exc = 0
stamp = ""
handle = ""

def log_values():
  print adr, " CNT %04d, RND 0x%02X, DATA 0x%02X, ERR %d, EXC %d" % (cnt, rnd, val, err, exc)
  print adr, " STAMP '%s'" % stamp

  data = open(logdir+"/"+adr, "w")
  data.write("  RND 0x%02X\n" % rnd)
  data.write(" DATA 0x%02X\n" % val)
  data.write("  ERR %d\n" % err)
  data.write("EXCPT %d\n" % exc)
  data.write("STAMP '%s'\n" % stamp)
  data.close()

while True:

  try:

    print adr, " Trying to connect ..."

    tool = pexpect.spawn('gatttool518 -b ' + adr + ' --interactive')
    tool.expect('\[LE\]>')
    tool.sendline('connect')
    tool.expect('success')

    # find handle
    cons = pexpect.run('hcitool con')
    cons = cons.split("\r\n")
    for con in cons:
      if adr in con:
        tok = con.split()
        handle = tok[4]

    # set baudrate to 9600
    tool.sendline('char-write-cmd 0x19 00')
    tool.expect('\[LE\]>')

    while True:

        rnd = random.randint(0, 255)

        # send byte to BLEMini
        tool.sendline('char-write-cmd 0x16 ' + ("%02X" % rnd))
        tool.expect('\[LE\]>')
        
        # read byte/s from BLEMini
        tool.sendline('char-read-hnd 0x12')
        tool.expect('descriptor: .*? \r') 
        v = tool.after.split()
        val = int(float.fromhex(v[1]))

        cnt = cnt + 1

        if val != rnd:
            err = err + 1

        stamp = datetime.now().ctime()

        log_values()

        time.sleep(5)

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
    log_values()

