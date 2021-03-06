//
// Copyright 2013-15 Thomas Ackermann
//
// Licensed under the Apache License, Version 2.0 (the "License");
// you may not use this file except in compliance with the License.
// You may obtain a copy of the License at
//
//   http://www.apache.org/licenses/LICENSE-2.0
//
// Unless required by applicable law or agreed to in writing, software
// distributed under the License is distributed on an "AS IS" BASIS,
// WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
// See the License for the specific language governing permissions and
// limitations under the License.
//

/*
  loopback test for reading/writing values from/to BLEmini<->Arduino Nano

  in gatttool:
  char-write-cmd 0x16 <value> 
  yields in Arduino:
  read <value> from Serial.read

  in Arduino:
  Serial.write((byte)val1);
  Serial.write((byte)val2);
  ...
  yields in gatttool:
  char-read-hnd 0x12 -> list of val<n> 
*/

#include <SoftwareSerial.h>

SoftwareSerial myserial(3, 2); // RX, TX to BLEmini on Arduino Nano

#define TEST_PIN   10

void setup()
{  
  pinMode(TEST_PIN, OUTPUT);
  myserial.begin(57600);
  Serial.begin(57600);
}

void loop()
{
  byte toggle = HIGH;
  byte data   = 0;
  
  if(myserial.available())
  {
    digitalWrite(TEST_PIN, toggle);
    if(toggle == LOW) toggle = HIGH;
    else              toggle = LOW;

    while(myserial.available())
    {
      data = myserial.read(); // beware: BLEMini first sends a '0' before the real data
      Serial.print("0x");
      Serial.println(data, HEX);
    }
    
    myserial.write(data);
  }
}
