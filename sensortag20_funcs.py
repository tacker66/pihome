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
# Algorithms below are from 
# http://processors.wiki.ti.com/index.php/CC2650_SensorTag_User's_Guide#Gatt_Server
#

def calcTmp(ambT, objT):
    ambT = float(ambT >> 2)
    objT = float(objT >> 2)
    SCALE_LSB = 0.03125
    return (ambT * SCALE_LSB, objT * SCALE_LSB)

def calcHum(rawT, rawH):
    tmp = (float(rawT) / 65536 ) * 165 - 40
    hum = (float(rawH) / 65536 ) * 109 # 109 (and not 100) gives the same value as the app
    return (tmp, hum)

def calcBar(rawT, rawP):
    tmp = float(rawT) / 100
    bar = float(rawP) / 100
    return (tmp, bar)

