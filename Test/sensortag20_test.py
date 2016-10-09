#!/usr/bin/env python

#
# Copyright 2016 Thomas Ackermann
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
# SensorTag 2.0 v1.3 uuids and handle ranges
#
#   Temperature (0xaa01): 0x22 - 0x29 (set 0x27 = 01; read 0x24)
#      Humidity (0xaa21): 0x2a - 0x31 (set 0x2f = 01; read 0x2c)
#     Barometer (0xaa41): 0x32 - 0x39 (set 0x37 = 01; read 0x34)
#           IOs (0xaa65): 0x4f - 0x53 (test mode: set 0x53 = 02; read 0x51;
#                                      bits: 0 flash ios move press light hum temp;
#                                      0x7f means "OK")
#

import os
import sys
import time
import pexpect
from datetime import datetime

sys.path.append('../.')
from sensortag20_funcs import *

adr = sys.argv[1]

logdir = "/tmp/pihome"
try:
  os.mkdir(logdir)
except:
  pass

cnt = 0
it = 0
at = 0
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
  print adr, "   CNT %d" % cnt
  print adr, "  POST 0x%s" % post
  print adr, " IRTMP %.1f" % it
  print adr, " AMTMP %.1f" % at
  print adr, " HMTMP %.1f" % ht
  print adr, " BRTMP %.1f" % pt
  print adr, " HUMID %.1f" % hu
  print adr, " BAROM %.0f" % pr
  print adr, " EXCPT %d" % exc
  print adr, " ACTEX %d" % act
  print adr, " STAMP '%s'" % stamp

  data = open(logdir+"/"+adr, "w")
  data.write(" POST 0x%s\n" % post)
  data.write("IRTMP %.1f\n" % it)
  data.write("AMTMP %.1f\n" % at)
  data.write("HMTMP %.1f\n" % ht)
  data.write("BRTMP %.1f\n" % pt)
  data.write("HUMID %.1f\n" % hu)
  data.write("BAROM %.0f\n" % pr)
  data.write("EXCPT %d\n" % exc)
  data.write("ACTEX %d\n" % act)
  data.write("STAMP '%s'\n" % stamp)
  data.close()

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

    print adr, " Enabling sensors ..."

    # enable test mode
    tool.sendline('char-write-req 0x53 02')
    tool.expect('\[LE\]>')

    # enable temperature sensor
    tool.sendline('char-write-req 0x27 01')
    tool.expect('\[LE\]>')

    # enable humidity sensor
    tool.sendline('char-write-req 0x2f 01')
    tool.expect('\[LE\]>')

    # enable barometric pressure sensor
    tool.sendline('char-write-req 0x37 01')
    tool.expect('\[LE\]>')

    # wait for the sensors to become ready
    time.sleep(1)

    while True:

        # read POST result
        tool.sendline('char-read-hnd 0x51')
        tool.expect('descriptor: .*? \r') 
        v = tool.after.split()
        post = v[1]

        # read temperature sensor
        tool.sendline('char-read-hnd 0x24')
        tool.expect('descriptor: .*? \r') 
        v = tool.after.split()
        rawObjT = long(float.fromhex(v[2] + v[1]))
        rawAmbT = long(float.fromhex(v[4] + v[3]))
        (at, it) = calcTmp(rawAmbT, rawObjT)

        # read humidity sensor
        tool.sendline('char-read-hnd 0x2c')
        tool.expect('descriptor: .*? \r') 
        v = tool.after.split()
        rawT = long(float.fromhex(v[2] + v[1]))
        rawH = long(float.fromhex(v[4] + v[3]))
        (ht, hu) = calcHum(rawT, rawH)

        # read barometric pressure sensor
        tool.sendline('char-read-hnd 0x34')
        tool.expect('descriptor: .*? \r') 
        v = tool.after.split()
        rawT = long(float.fromhex(v[3] + v[2] + v[1]))
        rawP = long(float.fromhex(v[6] + v[5] + v[4]))
        (pt, pr) = calcBar(rawT, rawP)

        cnt = cnt + 1

        stamp = datetime.now().ctime()
        act = 0

        log_values()

        time.sleep(3)

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

