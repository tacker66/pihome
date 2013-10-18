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
  read all digital inputs when triggered by Serial and write result back to Serial
  
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

#define TEST_PIN   10

void setup()
{  
  pinMode(TEST_PIN, OUTPUT);
  Serial.begin(57600);
}

void loop()
{
  static byte toggle = HIGH;
  static byte data;
  
  if(Serial.available())
  {
    digitalWrite(TEST_PIN, toggle);
    if(toggle == LOW) toggle = HIGH;
    else              toggle = LOW;

    while(Serial.available())  Serial.read(); // ignore values
    
    Serial.write((byte)random(256));
    Serial.write((byte)random(256));
 
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
