#!/usr/bin/env python

#
# Copyright 2014-16 Thomas Ackermann
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
# Simple web interface for pihome data. 
# A standard lighttpd installation is assumed for this functionality
# and this script must be run as root.
#

import glob, string, time, os, sys

path = "/tmp/pihome/*"
html = "/var/www/index.html"

config = dict()
def read_config(file):
    fd = open(file)
    for line in fd:
        line = string.strip(line)
        if len(line) > 0 and line[0] != "#":
            tok = string.split(line, "=")
            config[string.strip(tok[0])] = string.strip(tok[1])

if len(sys.argv) > 1:
    read_config(sys.argv[1])

while True:
    hd = open(html, "w")
    hd.write('<html><head><title>\n')
    hd.write('pihome data\n')
    hd.write('</title><meta http-equiv="refresh" content="30">\n')
    hd.write('<head><body>\n')
    hd.write('<h2>pihome data</h2>\n')
    files = sorted(glob.glob(path))
    for file in files:
        device_id = os.path.basename(file)
        if device_id not in config:
            device_name = "unknown"
        else:
            device_name = config[device_id]
        hd.write('<h3>' + device_id + ' (' + device_name + ')' + '</h3>')
        hd.write('<table border="1">\n')
        fd = open(file)
        for line in fd:
            tok = string.strip(line).split()
            hd.write('<tr><td align="right">' + tok[0] + '</td>\n')
            hd.write('<td align="left">' + string.join(tok[1:]) + '</td></tr>\n')
        fd.close()
        hd.write('</table>\n')
    hd.write('</body></html>\n')
    hd.close()
    time.sleep(30)
    
