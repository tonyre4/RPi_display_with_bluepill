
#define TEST_FONTS    // Comment out to disable custom fonts

#include "SPI.h"
#include "Waveshare_ILI9486_GFX.h"



// Waveshare shield has fixed pin mapping (defined by DEV_config.h)
Waveshare_ILI9486_GFX tft = Waveshare_ILI9486_GFX();

int x = 0 , y = 0;
//char inc[5];
int idx = 0;
char incom;
uint16_t data=0;
uint16_t inci[5];
uint16_t times[] = {1,10,100,1000,10000};

void setup(){
  tft.begin();
  Serial.begin(115200);
  Serial.print("Hi!");
  //tft.fillScreen(ILI9486_BLACK);
}

//colores = 5bits de r
//          6bits de g
//          5bits de b

const unsigned int h = 320, w = 480;

void loop(){
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
