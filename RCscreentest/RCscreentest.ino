#include "SPI.h"
#include <SD.h>

#define  BLACK   0x0000
#define BLUE    0x001F
#define RED     0xF800
#define GREEN   0x07E0
#define CYAN    0x07FF
#define MAGENTA 0xF81F
#define YELLOW  0xFFE0
#define WHITE   0xFFFF

//#define UNOMODE

#define STMMODE

#ifdef STMOLD
#include "Adafruit_ILI9486_STM32.h"
//RED =       0xF800 --> 1111 1000 0000 0000
//GREEN =     0x07E0 --> 0000 0111 1110 0000
//BLUE BLUE = 0x001F --> 0000 0000 0001 1111
// Waveshare shield has fixed pin mapping (defined by DEV_config.h)
Adafruit_ILI9486_STM32 tft;
#define Serial Serial1
#define SS_SD PB13
#endif

#ifdef STMMODE 
#define LCD_CS PB11 // Chip Select goes to Analog 3
#define LCD_CD PB1 // Command/Data goes to Analog 2
#define LCD_WR PB0 // LCD Write goes to Analog 1
#define LCD_RD PB10 // LCD Read goes to Analog 0
#define LCD_RESET PC15 // Can alternately just connect to Arduino's reset pin
#include "Adafruit_GFX.h"// Hardware-specific library
#include <MCUFRIEND_kbv.h>
MCUFRIEND_kbv tft;
#define SS_SD PB13
#endif

#ifdef UNOMODE
#define LCD_CS A3 // Chip Select goes to Analog 3
#define LCD_CD A2 // Command/Data goes to Analog 2
#define LCD_WR A1 // LCD Write goes to Analog 1
#define LCD_RD A0 // LCD Read goes to Analog 0
#define LCD_RESET A4 // Can alternately just connect to Arduino's reset pin
#include "Adafruit_GFX.h"// Hardware-specific library
#include <MCUFRIEND_kbv.h>
MCUFRIEND_kbv tft;
#define SS_SD 10
#endif


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

#define TESTGFX



#ifdef MAIN

void setup() {
  Serial.begin(38400);
  SDinit();

  #ifndef UNOMODE
  tft.begin();
  #else
  uint16_t ID = tft.readID(); //
  Serial.print("ID = 0x");
  Serial.println(ID, HEX);
  if (ID == 0xD3D3) ID = 0x9481; // write-only shield
//    ID = 0x9329;                             // force ID
  tft.begin(ID);
  #endif
  pinMode(LED_BUILTIN, OUTPUT);
  digitalWrite(LED_BUILTIN,1);
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
  if (!SD.begin(SPI_FULL_SPEED,SS_SD)) {
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

