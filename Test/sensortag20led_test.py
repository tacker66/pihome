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
# SensorTag 2.0 v1.2 with LED DevPack handle ranges 
#
#     Red: set 0x21 with intensity (1 byte)
#   Green: set 0x24 with intensity (1 byte)
#    Blue: set 0x27 with intensity (1 byte)
#   White: set 0x2a with intensity (1 byte)
#    RGBW: set 0x2d with intensities (4 bytes)
#

import os
import sys
import time
import pexpect

adr = sys.argv[1]

while True:

  try:

    print adr, "Trying to connect. You might need to press the side button ..."

    tool = pexpect.spawn('gatttool535 -b ' + adr + ' --interactive')
    tool.expect('\[LE\]>')
    tool.sendline('connect')
    tool.expect('success')

    print adr, "Lighting the LEDs ..."
    wait = 0.1
    intensity = '03'
    while True:

        for led in ['0x21', '0x24', '0x27', '0x2a']:
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

