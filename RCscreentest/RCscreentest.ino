#include "SPI.h"
#include <SD.h>


#define BLACK   0x0000
#define BLUE    0x001F
#define RED     0xF800
#define GREEN   0x07E0
#define CYAN    0x07FF
#define MAGENTA 0xF81F
#define YELLOW  0xFFE0
#define WHITE   0xFFFF

//#define UNOMODE

#define STMMODE
#define BLUEDISP

#define TEXTGFX

#ifdef STMOLD
#include "Adafruit_ILI9486_STM32.h"
//RED =       0xF800 --> 1111 1000 0000 0000
//GREEN =     0x07E0 --> 0000 0111 1110 0000
//BLUE BLUE = 0x001F --> 0000 0000 0001 1111
// Waveshare shield has fixed pin mapping (defined by DEV_config.h)
Adafruit_ILI9486_STM32 tft;
//#define Serial Serial1
#define SS_SD PB12
#endif

#ifdef STMMODE 
//#define LCD_CS PB8 
//#define LCD_CD PB7 
//#define LCD_WR PB6 
//#define LCD_RD PB0 
//#define LCD_RESET PB9
//
//#define LCD_D0 PA0
//#define LCD_D1 PA1
//#define LCD_D2 PA2
//#define LCD_D3 PA3
//#define LCD_D4 PA4
//#define LCD_D5 PA5
//#define LCD_D6 PA6
//#define LCD_D7 PA7

#include "Adafruit_GFX.h"// Hardware-specific library
#include <MCUFRIEND_kbv.h>
MCUFRIEND_kbv tft;

#define SS_SD PB12
#define Serial Serial1

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

//#define TESTGFX



#ifdef MAIN

void setup() {
  
  #ifdef RPIDISP
  tft.begin();
  #elif BLUEDISP
  tft.begin(0x9486);
  #endif
  //pinMode(PC13, OUTPUT);
  //digitalWrite(PC13,1);
  
  Serial.begin(38400);
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
#warning Testing Graphics
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
void setup() {
  // Open Serial communications and wait for port to open:
  SPI.setModule(2);
  Serial.begin(9600);
  while (!Serial) {
    ; // wait for Serial port to connect. Needed for native USB port only
  }

  Serial.print("Initializing SD card...");

  if (!SD.begin(PB12)) {
    Serial.println("initialization failed!");
    while (1);
  }
  Serial.println("initialization done.");

  myFile = SD.open("ima0.txt");
  if (myFile) {
    Serial.println("ima0.txt:");

    // read from the file until there's nothing else in it:
    while (myFile.available()) {
      Serial.write(myFile.read());
      delay(1000);
    }
    // close the file:
    myFile.close();
  } else {
    // if the file didn't open, print an error:
    Serial.println("error opening ima.txt");
  }

  Serial.println("done!");
}

void loop() {
  // nothing happens after setup finishes.
}
#endif
