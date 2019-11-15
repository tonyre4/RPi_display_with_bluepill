#include "SPI.h"
#include "Adafruit_ILI9486_STM32.h"
#include <SD.h>

//RED =       0xF800 --> 1111 1000 0000 0000
//GREEN =     0x07E0 --> 0000 0111 1110 0000
//BLUE BLUE = 0x001F --> 0000 0000 0001 1111


// Waveshare shield has fixed pin mapping (defined by DEV_config.h)
Adafruit_ILI9486_STM32 tft;

#define Serial Serial1

File myFile;
const unsigned int h = 320, w = 480;
int x = 0 , y = 0;
//char inc[5];
int idx = 0;
char incom;
uint16_t data=0;
uint16_t inci[5];
uint16_t times[] = {1,10,100,1000,10000};
char filename[] = "ima";
char id[] = "0";
char prefix[] = ".txt";
String zzz = "ima0.txt";
uint8_t fcntr = 0;

void setup() {
  Serial.begin(500000);
  SDinit();
  tft.begin();
  pinMode(PC13, OUTPUT);
  digitalWrite(PC13,1);
}

void loop() {
  //if(Serial.available()>0){
    incom = readSDchar();
    //Serial.println(incom);
    //delay(1);
    dec(incom);
  //}
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
    case 'z':
      delay(2000);
      break;
    case '0' ... '?':
      uint16_t cc = c;
      data |= (cc-'0'<<idx*4);
      idx++;
      break;
    
      }
}

void SDinit(){
  Serial.print("Initializing SD card...");
  if (!SD.begin(PB13)) {
    Serial.println("initialization failed!");
    while (1);
  }
  Serial.println("initialization done.");
  readtxtinit();
}

boolean readtxtinit(){
  //myFile = SD.open(f);
  //myFile = SD.open("ima0.txt");
  //String aaa = filename + id + prefix;
  myFile = SD.open(zzz);
  fcntr = (fcntr==10) ? 0 : fcntr+1;
  //id[0]= '0'+fcntr;
  zzz[3] = '0' + fcntr;
  delay(1);
  if (myFile){
    return true;
  }
  else{
    return false;
  }
}

char readSDchar(){
  if (myFile.available()){
    return myFile.read();
  }
  else{
    myFile.close();
    readtxtinit();
    return 'z';
  }
}


