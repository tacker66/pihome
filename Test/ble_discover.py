#!/usr/bin/env python

#
# Copyright 2014 Thomas Ackermann
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
# Disvover characteristics of BLE (Bluetooth low energy) devices
#
# Usage: ble_discover.py BLUETOOTH_ADR
#

import re
import sys
import time
import pexpect

def read_string(handle):
  tool.sendline("char-read-hnd " + handle)
  tool.expect("descriptor:.*\r\n")
  chars = tool.after.split()[1:]
  if len(chars) > 0:
    string = ""
    for char in chars:
      idx = int(char, 16)
      if idx > 0:
        string = string + chr(idx)
      else:
        string = string + "\\" + char
    return "'" + string + "'"
  else:
    return "<empty>"

def read_property(handle):
  tool.sendline("char-read-hnd " + handle)
  tool.expect("descriptor: .*? \r")
  prop = tool.after.split()[1]
  val = int(prop, 16)
  prop = prop + " = "
  if val & 0x01:
    prop = prop + "? "
  if val & 0x02:
    prop = prop + "read "
  if val & 0x04:
    prop = prop + "? "
  if val & 0x08:
    prop = prop + "write "
  if val & 0x10:
    prop = prop + "notify "
  if val & 0x20:
    prop = prop + "indicate "
  if val & 0x40:
    prop = prop + "? "
  if val & 0x80:
    prop = prop + "? "
  return prop

adr = sys.argv[1]
tool = pexpect.spawn('gatttool514 -b ' + adr + ' --interactive')
tool.expect('\[LE\]>')

sys.stdout.write("Trying to connect to '" + 
  adr + "'. (Device must be advertising ...)\n")
tool.sendline('connect')
tool.expect('success')

sys.stdout.write("Starting discovery ...\n")

tool.sendline('char-desc')
tool.expect('finished')

lines = tool.before.split("\r\n")[2:-1]

for line in lines:
  tok = line
  tok = re.sub("^.*handle: ", "", tok)
  tok = re.sub("uuid:", "", tok)
  tok = re.sub(",", "", tok)
  (handle, uuid) = tok.split()
  handle = handle.lower()
  uuid = uuid.lower()
  if uuid == "2800":
    sys.stdout.write(handle + " : primary -------------------------------" + "\n")
  elif len(uuid) > 4:
    sys.stdout.write(handle + " :    characteristic = '" + uuid + "'" + "\n")
  elif uuid == "2803":
    sys.stdout.write(handle + " :          property = ")
    sys.stdout.write(read_property(handle) + "\n")
  elif uuid == "2901":
    sys.stdout.write(handle + " :       description = ")
    sys.stdout.write(read_string(handle) + "\n")
  elif uuid == "2a00":
    sys.stdout.write(handle + " :              name = ")
    sys.stdout.write(read_string(handle) + "\n")
  elif uuid == "2a24":
    sys.stdout.write(handle + " :      model number = ")
    sys.stdout.write(read_string(handle) + "\n")
  elif uuid == "2a25":
    sys.stdout.write(handle + " :     serial number = ")
    sys.stdout.write(read_string(handle) + "\n")
  elif uuid == "2a26":
    sys.stdout.write(handle + " : firmware revision = ")
    sys.stdout.write(read_string(handle) + "\n")
  elif uuid == "2a27":
    sys.stdout.write(handle + " : hardware revision = ")
    sys.stdout.write(read_string(handle) + "\n")
  elif uuid == "2a28":
    sys.stdout.write(handle + " : software revision = ")
    sys.stdout.write(read_string(handle) + "\n")
  elif uuid == "2a29":
    sys.stdout.write(handle + " :      manufacturer = ")
    sys.stdout.write(read_string(handle) + "\n")

sys.stdout.write("Discovery finished.\n")


