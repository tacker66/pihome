#!/usr/bin/env python3

#
# Copyright 2014-2023 Thomas Ackermann
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
# Discover characteristics of BLE (Bluetooth low energy) devices
#
# Usage: ble_discover.py BLUETOOTH_ADR
#

import re
import sys
import time
import pexpect

def read_number(handle):
  tool.sendline("char-read-hnd " + handle)
  tool.expect("descriptor:.*\r\n")
  chars = tool.after.split()[1:]
  l = len(chars)
  n = 0
  m = 1
  if l > 0:
    for char in reversed(chars):
      idx = int(char, 16)
      n = n + m * idx
      m = m * 256
  return n

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
  desc = tool.after.split()
  val = int(desc[1], 16)
  prop = ""
  if val & 0x01:
    prop = prop + "broadcast, "
  if val & 0x02:
    prop = prop + "read, "
  if val & 0x04:
    prop = prop + "write request, "
  if val & 0x08:
    prop = prop + "write, "
  if val & 0x10:
    prop = prop + "notify, "
  if val & 0x20:
    prop = prop + "indicate, "
  if val & 0x40:
    prop = prop + "signed write, "
  if val & 0x80:
    prop = prop + "extended, "
  hndl = str(hex(int(desc[2], 16) + 256 * int(desc[3], 16)))
  idx = 4
  if len(desc) == 20:
   idx = 16
  uuid = "0x" + desc[idx+1] + desc[idx]
  prop = prop + "handle=" + hndl + ", uuid=" + uuid
  return prop

def read_conprop(handle):
  tool.sendline("char-read-hnd " + handle)
  tool.expect("descriptor: .*? \r")
  v = tool.after.split()
  min_int   = str((float.fromhex(v[2] + v[1])) * 1.25)
  max_int   = str((float.fromhex(v[4] + v[3])) * 1.25)
  slave_lat = str((float.fromhex(v[6] + v[5])) * 1.25)
  timeout   = str((float.fromhex(v[8] + v[7])) * 10)
  ret_str  = "min = " + min_int + "ms; max = " + max_int + "ms; "
  ret_str += "lat = " + slave_lat + "ms; timeout = " + timeout + "ms"
  return ret_str

adr = sys.argv[1]
print("Trying to connect to '" + adr + "' (device must be advertising) ...")

tool = pexpect.spawn('gatttool -b ' + adr + ' --interactive', encoding='utf-8')
tool.expect('\[LE\]>')
tool.sendline('connect')
tool.expect('success')

print("Starting discovery (this may take some time) ...")

# char-desc is running asynchronously and no kind of 'finished'
# message is printed by gatttool, so we have to greedily read
# everything until pexpect timeouts
tool.sendline('char-desc')
tool.expect(['WILLNOTMATCH', pexpect.TIMEOUT], timeout=20)
lines = tool.before.split('\r')

print("HANDLE : VALUE")
print("--------------")

for line in lines:
  if "handle:" in line:
    tok = line
    tok = re.sub("^.*handle: ", "", tok)
    tok = re.sub("uuid:", "", tok)
    tok = re.sub(",", "", tok)
    (handle, uuid) = tok.split()
    handle = handle.lower()
    uuid = uuid.lower()
    if "2800-" in uuid:
      sys.stdout.write(handle + " : primary ------------------------------------------------------\n")
    elif "2803-" in uuid:
      sys.stdout.write(handle + " :              property : ")
      sys.stdout.write(read_property(handle) + "\n")
    elif "2901-" in uuid:
      sys.stdout.write(handle + " :           description : ")
      sys.stdout.write(read_string(handle) + "\n")
    elif "2902-" in uuid:
      sys.stdout.write(handle + " : characteristic config : '" + uuid + "'" + "\n")
    elif "2a00-" in uuid:
      sys.stdout.write(handle + " :                  name : ")
      sys.stdout.write(read_string(handle) + "\n")
    elif "2a04-" in uuid:
      sys.stdout.write(handle + " :  preferred connection : ")
      sys.stdout.write(read_conprop(handle) + "\n")
    elif "2a19-" in uuid:
      sys.stdout.write(handle + " :         battery level : ")
      sys.stdout.write(str(read_number(handle)) + "\n")
    elif "2a24-" in uuid:
      sys.stdout.write(handle + " :          model number : ")
      sys.stdout.write(read_string(handle) + "\n")
    elif "2a25-" in uuid:
      sys.stdout.write(handle + " :         serial number : ")
      sys.stdout.write(read_string(handle) + "\n")
    elif "2a26-" in uuid:
      sys.stdout.write(handle + " :     firmware revision : ")
      sys.stdout.write(read_string(handle) + "\n")
    elif "2a27-" in uuid:
      sys.stdout.write(handle + " :     hardware revision : ")
      sys.stdout.write(read_string(handle) + "\n")
    elif "2a28-" in uuid:
      sys.stdout.write(handle + " :     software revision : ")
      sys.stdout.write(read_string(handle) + "\n")
    elif "2a29-" in uuid:
      sys.stdout.write(handle + " :          manufacturer : ")
      sys.stdout.write(read_string(handle) + "\n")
    else:
      sys.stdout.write(handle + " :        characteristic : '" + uuid + "'" + "\n")


