//#########LIBS#############
#include "SPI.h"
#include <SD.h>
//#########END LIBS#########


//#######COLORS#############
#define BLACK   0x0000
#define BLUE    0x001F
#define RED     0xF800
#define GREEN   0x07E0
#define CYAN    0x07FF
#define MAGENTA 0xF81F
#define YELLOW  0xFFE0
#define WHITE   0xFFFF
//########END COLORS ########

//Testing defines
//#define TESTSD
//#define TESTGFX
#define BLUEDISP


#include "Adafruit_GFX.h"// Hardware-specific library
#include <MCUFRIEND_kbv.h>
MCUFRIEND_kbv tft;

#define SS_SD PB12
#define Serial Serial1

//#########VARS#############
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
//###########END VARS ###############

#ifndef TESTGFX | TESTSD

void setup() {
  
  //#ifdef RPIDISP
  //tft.begin();
  //#elif BLUEDISP
  SPI.setModule(2);
  tft.begin(0x9486);
  pinMode(PC13,OUTPUT);
  
  //#endif
  //pinMode(PC13, OUTPUT);
  //digitalWrite(PC13,1);
  
  //Serial.begin(38400);
  SDinit();
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
      //tft.drawPixel(y,x,BLUE);
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
  //Serial.print("Initializing SD card...");
  if (!SD.begin(SS_SD)) {
    //Serial.println("initialization failed!");
    while (1){
      digitalWrite(PC13,LOW);
      delay(250);
      digitalWrite(PC13,HIGH);
      delay(250);
    }
  }
  //Serial.println("initialization done.");
  readtxtinit();
}

boolean readtxtinit(){
  myFile = SD.open(zzz);
  fcntr = (fcntr==10) ? 0 : fcntr+1;
  zzz[3] = '0' + fcntr;
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

#endif


#ifdef TESTGFX
void setup() {
  tft.begin(0x9486);
}

void loop() {
    for(x=0;x<100;x++){
      for (y=0;y<100;y++){
        tft.drawPixel(y,x,BLUE);
      }
    }
}
#endif


#ifdef TESTSD
#warning "Testing SD card"
void setup() {
  pinMode(PC13,OUTPUT);
  digitalWrite(PC13,HIGH);
  SPI.setModule(2);
  delay(2000);

  if (!SD.begin(PB12)) {
    while (1){
      digitalWrite(PC13,HIGH);
      delay(300);
      digitalWrite(PC13,LOW);
      delay(300);
    }
  }
  else{
    digitalWrite(PC13,LOW);
  }

}

void loop() {
  // nothing happens after setup finishes.
}
#endif
