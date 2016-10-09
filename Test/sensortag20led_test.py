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
# SensorTag 2.0 v1.3 with LED DevPack uuids and handle ranges
#
#     Red (0xffb1): set 0x40 with intensity (1 byte)
#   Green (0xffb2): set 0x43 with intensity (1 byte)
#    Blue (0xffb3): set 0x46 with intensity (1 byte)
#   White (0xffb4): set 0x49 with intensity (1 byte)
#    RGBW (0xffb5): set 0x4c with intensities (4 bytes)
#

import os
import sys
import time
import pexpect

adr = sys.argv[1]

while True:

  try:

    print adr, "Trying to connect. You might need to press the side button ..."

    tool = pexpect.spawn('gatttool542 -b ' + adr + ' --interactive')
    tool.expect('\[LE\]>')
    tool.sendline('connect')
    tool.expect('success')

    print adr, "Lighting the LEDs ..."
    wait = 0.1
    intensity = '03'
    while True:

        for led in ['0x40', '0x43', '0x46', '0x49']:
            cmd = 'char-write-req ' + led + ' '
            tool.sendline(cmd + intensity)
            tool.expect('\[LE\]>')
            time.sleep(wait)
            tool.sendline(cmd + '00')
            tool.expect('\[LE\]>')
            time.sleep(wait)

  except KeyboardInterrupt:
    tool.sendline('quit')
    tool.close()
    sys.exit()

  except:
    tool.sendline('quit')
    tool.close(force=True)

