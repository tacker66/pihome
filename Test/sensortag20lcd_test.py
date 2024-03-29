#!/usr/bin/env python3

#
# Copyright 2016-2021 Thomas Ackermann
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
# SensorTag 2.0 v1.3 with LCD DevPack uuids and handle ranges
#
#   IO Config (0xaa65): 0x43 (local mode "00", remote mode "01", test mode "02")
#     IO Data (0xaa66): 0x41 (in remote mode: bit 0 "Red", bit 1 "Green", bit 2 "Buzzer")
#  LCD String (0xad01): 0x65 (1-16 chars)
#  LCD Config (0xad02): 0x67 (off "01", on "02", clear all "03", clear row "04 <row>",
#                             invert "05, set row col "06 <row> <col>")
#                             settings for row and col not working as of FW v1.3
#

import os
import sys
import time
import pexpect

adr = sys.argv[1]

def write_lcd(msg):
    msg = msg[:16]
    print(msg)
    msg = msg.center(16)
    chrs = ''
    for chr in list(msg):
        chrs = chrs + hex(ord(chr))[2:]
    tool.sendline('char-write-req 65 ' + chrs)
    tool.expect('\[LE\]>')

while True:

  try:

    print(adr, "Trying to connect. You might need to press the side button ...")

    tool = pexpect.spawn('gatttool -b ' + adr + ' --interactive', encoding='utf-8')
    tool.expect('\[LE\]>')
    tool.sendline('connect')
    tool.expect('success')

    tool.sendline('char-write-req 41 00')
    tool.expect('\[LE\]>')
    tool.sendline('char-write-req 43 01')
    tool.expect('\[LE\]>')

    msg = dict()
    msg['01'] = "Red"
    msg['02'] = "Green"
    msg['04'] = "Buzzer!"
    wait = 0.1
    while True:

        for out in sorted(msg):
            write_lcd(msg[out])
            cmd = 'char-write-req 41 ' + out
            tool.sendline(cmd)
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

