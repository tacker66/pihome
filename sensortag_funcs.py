#
# Copyright 2013 Michael Saunby
# Copyright 2013-2023 Thomas Ackermann
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
# Algorithms below are from (partly adapted)
# https://web.archive.org/web/20180918194512/http://processors.wiki.ti.com/index.php/SensorTag_User_Guide
#

tosigned = lambda n: float(n-0x10000) if n>0x7fff else float(n)
tosignedbyte = lambda n: float(n-0x100) if n>0x7f else float(n)

def calcTmp(ambT, objT):
    ambT = tosigned(ambT)
    objT = tosigned(objT)
    m_tmpAmb = ambT/128.0
    Vobj2 = objT * 0.00000015625
    Tdie2 = m_tmpAmb + 273.15
    S0 = 6.4E-14
    a1 = 1.75E-3
    a2 = -1.678E-5
    b0 = -2.94E-5
    b1 = -5.7E-7
    b2 = 4.63E-9
    c2 = 13.4
    Tref = 298.15
    S = S0*(1+a1*(Tdie2 - Tref)+a2*pow((Tdie2 - Tref),2))
    Vos = b0 + b1*(Tdie2 - Tref) + b2*pow((Tdie2 - Tref),2)
    fObj = (Vobj2 - Vos) + c2*pow((Vobj2 - Vos),2)
    tObj = pow(pow(Tdie2,4) + (fObj/S),.25)
    tObj = (tObj - 273.15)
    return (m_tmpAmb, tObj)

def calcHum(rawT, rawH):
    t = -46.85 + 175.72/65536.0 * rawT
    rawH = float(int(rawH) & ~0x0003);
    rh = -6.0 + 125.0/65536.0 * rawH
    return (t, rh)

def calcAccel(rawX, rawY, rawZ):
    accel = lambda v: tosignedbyte(v) / 64.0
    xyz = [accel(rawX), accel(rawY), accel(rawZ)]
    mag = (xyz[0]**2 + xyz[1]**2 + xyz[2]**2)**0.5 # additionally compute magnitude to quickly infer if we are in rest or moving
    return (xyz, mag)

def calcMagn(rawX, rawY, rawZ):
    magforce = lambda v: (tosigned(v) * 1.0) / (65536.0/2000.0)
    return [magforce(rawX), magforce(rawY), magforce(rawZ)]

class Barometer:

    def calcBarTmp(self, raw_temp):
        c1 = self.m_barCalib.c1
        c2 = self.m_barCalib.c2
        val = int((c1 * raw_temp) * 100)
        temp = val >> 24
        val = int(c2 * 100)
        temp += (val >> 10)
        return float(temp) / 100.0

    def calcBarPress(self,Tr,Pr):
        c3 = self.m_barCalib.c3
        c4 = self.m_barCalib.c4
        c5 = self.m_barCalib.c5
        c6 = self.m_barCalib.c6
        c7 = self.m_barCalib.c7
        c8 = self.m_barCalib.c8
        s = int(c3)
        val = int(c4 * Tr)
        s += (val >> 17)
        val = int(c5 * Tr * Tr)
        s += (val >> 34)
        o = int(c6) << 14
        val = int(c7 * Tr)
        o += (val >> 3)
        val = int(c8 * Tr * Tr)
        o += (val >> 19)
        pres = ((s * Pr) + o) >> 14
        return float(pres)/100.0

    def calc(self,  rawT, rawP):
        self.m_raw_temp = tosigned(rawT)
        self.m_raw_pres = rawP
        bar_temp = self.calcBarTmp( self.m_raw_temp )
        bar_pres = self.calcBarPress( self.m_raw_temp, self.m_raw_pres )
        return( bar_temp, bar_pres)

    def __init__(self, rawCalibration):
        self.m_barCalib = self.Calib( rawCalibration )
        return

    class Calib:

        def bld_int(self, lobyte, hibyte):
            return (lobyte & 0x0FF) + ((hibyte & 0x0FF) << 8)

        def __init__( self, pData ):
            self.c1 = self.bld_int(pData[0],pData[1])
            self.c2 = self.bld_int(pData[2],pData[3])
            self.c3 = self.bld_int(pData[4],pData[5])
            self.c4 = self.bld_int(pData[6],pData[7])
            self.c5 = tosigned(self.bld_int(pData[8],pData[9]))
            self.c6 = tosigned(self.bld_int(pData[10],pData[11]))
            self.c7 = tosigned(self.bld_int(pData[12],pData[13]))
            self.c8 = tosigned(self.bld_int(pData[14],pData[15]))
