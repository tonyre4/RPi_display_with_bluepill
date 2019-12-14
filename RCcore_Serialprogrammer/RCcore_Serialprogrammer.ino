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

#define BRATE 9600

#include "Adafruit_GFX.h"// Hardware-specific library
#include <MCUFRIEND_kbv.h>
MCUFRIEND_kbv tft;

#define SS_SD PB12
//#define Serial Serial1

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
String filename = "ima0.txt";
uint8_t fcntr = 0;
bool progmode = false;
bool getfpointer = false;
bool filing = false;
uint8_t fpointer;
bool exitt=false;

//###########END VARS ###############

//Testing defines
//#define TESTSD
//#define TESTGFX
//#define TESTSERIAL

#if defined(TESTGFX) || defined(TESTSD) || defined(TESTSERIAL)
#else
void setup() {
  

  Serial.begin(115200);
  
  SPI.setModule(2);
  tft.begin(0x9486);
  tft.setRotation(2);
  tft.fillScreen(BLACK);
  pinMode(PC13,OUTPUT);

  SDinit();

  if (pgmMode())
    PCtransf();
  
}


void loop() {
    dec(readSDchar());
}

void PCtransf(){
  tftmgs("Entering to \nprogramming mode");
  delay(10000);
  Serial.write('r');
  tftmgs("ready");
  
  while(1){
    if (Serial.available()>0){
      char c = Serial.read();
      //tftmgs(c);
      Serial.write(c);
      dec2(c);
      if (exitt){
        break;
      }
    }
  }
}

void tftmgs(char *s){
  tft.fillScreen(BLACK);
  tft.setCursor(0, 0);
  tft.setTextColor(GREEN);
  tft.setTextSize(2);
  tft.println(s);
}
void tftmgs(char s){
  tft.fillScreen(GREEN);
  tft.setCursor(0, 0);
  tft.setTextColor(RED);
  tft.setTextSize(2);
  tft.println(s);
}



bool dec2(char c){
  switch (c){
    case 'd':
      myFile.close();
      for(int i=0;i<10;i++){ //Deleting images
          fpointer = i;
          filename[3] = '0' + fpointer;
          SD.remove(filename.c_str()); 
      }
      break;
    case 'p':
      getfpointer = true;
      break;

    case '.':
      if(getfpointer){
        getfpointer = false;
        filing = true;
      }
    break;

    case 'z':
      myFile.print(c);
      myFile.close();
      break;
      
    case '0' ... '?':
    case ',':
    case '\n':
    case '&':
        if (getfpointer){
          myFile.close();
          fpointer = c - '0';
          loadfile();
        }
        if(filing){
          myFile.print(c);
          dec(c);
        }
      break;

    case '!':
        tft.fillScreen(BLACK);
        tft.setCursor(0, 0);
        tft.setTextColor(GREEN);  
        tft.setTextSize(2);
        tft.println("Uploading done!");
      exitt = true;
      return true;
  }
  return false;
}

void loadfile(){
  filename[3] = '0' + fpointer;
  myFile = SD.open(filename,FILE_WRITE);
}

bool pgmMode(){
  for(int i=0;i<3000;i++){
    if (Serial.available()>0){
      return true;
    }
    else{
      if(i%1000==0){
        tft.fillScreen(BLACK);
        tft.setCursor(0, 0);
        tft.setTextColor(RED);  
        tft.setTextSize(2);
        tft.println("Loading... ");
        int ii = i/1000;
        tft.print(3-ii);
        tft.print("s left");
        Serial.print("Hello");
      }
    }
    delay(1);
  }
  return false;
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
    tft.fillScreen(BLACK);
    tft.setCursor(0, 0);
    tft.setTextColor(RED);  tft.setTextSize(2);
    tft.println("SD card not found!");
    while (1);
  }
  readtxtinit();
}

boolean readtxtinit(){
  myFile = SD.open(filename);
  fcntr = (fcntr==10) ? 0 : fcntr+1;
  filename[3] = '0' + fcntr;
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


#ifdef TESTSERIAL
void setup(){
  //SPI.setModule(2);
  Serial.begin(BRATE);  
}

void loop(){
  Serial.print("Hello");
  for(int i=0;i<1000;i++){
  delay(1);
    if (Serial.available()>0){
      Serial.write(Serial.read());
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
      tft.fillScreen(BLACK);
      tft.setCursor(0, 0);
      tft.setTextColor(RED);  tft.setTextSize(1);
      tft.println("SD card not found!");
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
