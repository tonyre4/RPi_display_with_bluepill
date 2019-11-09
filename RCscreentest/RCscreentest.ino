#include "SPI.h"
#include "Adafruit_ILI9486_STM32.h"

//RED =       0xF800 --> 1111 1000 0000 0000
//GREEN =     0x07E0 --> 0000 0111 1110 0000
//BLUE BLUE = 0x001F --> 0000 0000 0001 1111


// Waveshare shield has fixed pin mapping (defined by DEV_config.h)
Adafruit_ILI9486_STM32 tft;

#define Serial Serial1

void setup() {
  tft.begin();
  Serial.begin(500000);
  Serial.print("Hi!");
}

const unsigned int h = 320, w = 480;
int x = 0 , y = 0;
//char inc[5];
int idx = 0;
char incom;
uint16_t data=0;
uint16_t inci[5];
uint16_t times[] = {1,10,100,1000,10000};

void loop() {
  if(Serial.available()>0){
    incom = Serial.read();
    dec(incom);
  }
}

void dec(char c){
  switch (c){
    case '&':
      x = 0;
      y = 0;
      idx = 0;
      break;
    case ',':
      idx = 0;
      tft.drawPixel(y,x,data);
      data = 0;
      x++;
      break;
    case '\n':
      idx = 0;
      x = 0;
      y++;
      break;
    case '0' ... '?':
      uint16_t cc = c;
      data |= (cc-'0'<<idx*4);
      idx++;
      break;
      
      }
      
}
