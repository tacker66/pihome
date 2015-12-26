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
# Displaying pihome diagnostic data with PiGlow
# (see http://shop.pimoroni.com/products/piglow
# and https://github.com/benleb/PyGlow)
#

import glob, string, time, os, PyGlow

path = "/tmp/pihome/*"

pyglow = PyGlow.PyGlow()

intensity = 1

try:
    while True:
        files = sorted(glob.glob(path))
        arm = 1
        pyglow.all(0)
        leds = []
        for file in files:
            if arm <= 3:
                fd = open(file)
                for line in fd:
                    tok = string.strip(line).split()
                    if tok[0] == "ACTEX":
                        off = 1 # red led
                        if tok[1] == "0":
                            off = 6 # white led
                        leds = leds + [(arm - 1) * 6 + off]
                    if tok[0] == "DATA":
                        bits = bin(string.atoi(tok[1], 16))
                        bits = bits[2:]
                        led = (arm - 1) * 6 + 2 # the four leds between white and red 
                                                # are used to show lower nibble of DATA
                        numbits = 4
                        while len(bits) > 0 and numbits > 0:
                            bit = bits[-1:]
                            bits = bits[:-1]
                            if bit == "1":
                                leds = leds + [led]
                            led = led + 1
                            numbits = numbits - 1
                fd.close()
            arm = arm + 1

        for i in range(0, 10):
            pyglow.set_leds(leds, intensity)
            pyglow.update_leds()
            time.sleep(0.5)
            pyglow.set_leds(leds, 0)
            pyglow.update_leds()
            time.sleep(0.5)

except KeyboardInterrupt:
    pyglow.all(0)
