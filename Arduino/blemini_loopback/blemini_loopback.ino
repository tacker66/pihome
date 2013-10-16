//
// Copyright 2013 Thomas Ackermann
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
  char-write-cmd 0x19 <value> 
  yields in Arduino:
  read <value> from Serial.read

  in Arduino:
  Serial.write((byte)val1);
  Serial.write((byte)val2);
  ...
  yields in gatttool:
  char-read-hnd 0x15 -> list of val<n> 
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
  static byte toggle = HIGH;
  static byte data;
  
  if(myserial.available())
  {
    digitalWrite(TEST_PIN, toggle);
    if(toggle == LOW) toggle = HIGH;
    else              toggle = LOW;

    while(myserial.available())
    {
      byte cnt = 0;
      data = myserial.read();
      Serial.print(cnt++); 
      Serial.print(": 0x"); 
      Serial.println(data, HEX);
    }
    
    myserial.write((byte)0xAA);
    myserial.write(data);

    myserial.write((byte)0xBB);
    myserial.write(data);

    myserial.write((byte)0xCC);
    myserial.write(data);

    myserial.write((byte)0xDD);
    
    /*
    static byte old_state = LOW;
    if(digitalRead(IN_PIN) != old_state)
    {
      old_state = digitalRead(IN_PIN);

      if(digitalRead(IN_PIN) == HIGH)
      {
        Serial.write((byte)0x11);
        Serial.write((byte)0x01);
      }
      else
      {
        Serial.write((byte)0x11);
        Serial.write((byte)0x00);
      }
    }
    */
  }
}
