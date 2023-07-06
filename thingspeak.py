#!/usr/bin/env python3

#
# Copyright 2021-2023 Thomas Ackermann
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
# Update a thingspeak channel
#

import glob, string, time, os, sys
import requests

path = "/tmp/pihome/*"

config = dict()
def read_config(file):
    fd = open(file)
    for line in fd:
        line = line.strip()
        if len(line) > 0 and line[0] != "#":
            tok = line.split("=")
            config[tok[0].strip()] = tok[1].strip()

if len(sys.argv) > 1:
    read_config(sys.argv[1])

def setBit(int_type, offset):
  mask = 1 << offset
  return(int_type | mask)

while True:
    files = sorted(glob.glob(path))
    values = {"key" : config["KEY"]}
    for file in files:
        device_id = os.path.basename(file)
        if device_id not in config:
            continue
        device_name = config[device_id]
        fd = open(file)
        for line in fd:
            tok = line.strip().split()
            symbol = tok[0]
            full_symbol = device_name + "." + symbol
            if full_symbol in config:
                value = tok[1]
                if "0x" in value:
                    value = float.fromhex(value)
                else:
                    value = float(value)
                field_num = config[full_symbol]
                if "." not in field_num:
                    field_name = "field" + config[device_name + "." + symbol]
                    values[field_name] = str(value)
                else:
                    tok = field_num.strip().split(".")
                    field_num = tok[0]
                    field_bit = tok[1]
                    field_name = "field" + field_num
                    if field_name not in values:
                        values[field_name] = 0
                    if value > 0:
                        values[field_name] = setBit(int(values[field_name]), int(field_bit))
        fd.close()

    log = ""
    try:
        response = requests.get(config["URL"], params=values)
        log = log + "Response: " + response.text
    except:
        log = log + "Error"
    print(log)

    time.sleep(1800)

