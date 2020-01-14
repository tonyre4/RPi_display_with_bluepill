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
uint32_t delays[] = {1000,3000,5000,7000,10000,13000,15000};
String filename = "ima00.txt";
uint8_t fcntr = 0;
bool progmode = false;
bool getfpointer = false;
bool filing = false;
uint8_t fpointer,fpointerdec,fpointeruni;
bool exitt=false;
bool delaymode = false;

//###########END VARS ###############

//Testing defines
//#define TESTSD
//#define TESTGFX
//#define TESTSERIAL

void SDinit();
bool pgmMode();

#if defined(TESTGFX) || defined(TESTSD) || defined(TESTSERIAL)
#else

char waitResponse(){
  while(1){
    if (Serial.available()>0){
      return Serial.read();
      }
    }
}

void PCtransf(){
  tftmsg("Entering to \nprogramming mode");
  delay(2000);
  tftmsg("Please press 'Conectar' button");
  while(waitResponse() != 'r');
  Serial.write('r');
  tftmsg("Device connected to software,\nmanage your images and then press 'Cargar!' button");
  
  while(1){
    if (Serial.available()>0){
      char c = Serial.read();
      //tftmsg(c);
      //Serial.write(c);
      dec2(c);
      if (exitt){
        break;
      }
    }
  }
}

void tftmsg(char *s, uint16_t background, uint16_t fcolor){
  tft.fillScreen(background);
  tft.setCursor(0, 0);
  tft.setTextColor(fcolor);
  tft.setTextSize(2);
  tft.println(s);
}

void tftmsg(char *s){
  tftmsg(s,BLACK,RED);
}

void openNext(){
  fnmaker();
  myFile.close();
  myFile = SD.open(filename);
  fpointer++;
}
void loadfile(){
  fnmaker();
  myFile.close();
  myFile = SD.open(filename,FILE_WRITE);
  fpointer++;
}

void fnmaker(){
  fpointeruni = fpointer%10;
  fpointerdec = fpointer/10;
  filename[3] = '0' + fpointerdec;
  filename[4] = '0' + fpointeruni;
}


bool dec2(char c){
  switch (c){
    case 'd':
      tftmsg("Deleting existing images...");
      for(int i=0;i<100;i++){ //Deleting images
          fpointer = i;
          fnmaker();
          if (SD.exists(filename))
            SD.remove(filename.c_str()); 
      }
      tftmsg("Images deleted succesfully!");
      fpointer = 0;
      break;
      
      
    //case 'p':
    //  getfpointer = true;
    //  break;

    case '.':
//      if(getfpointer){
//        getfpointer = false;
//        filing = true;
//      }
      //openNext();
      loadfile();
    break;

    case 'z':
      myFile.print(c);
      delaymode = true;
      //myFile.close();
      break;
      
    case '0' ... '?':
        if (delaymode){
          myFile.print(c);
          delaymode=false;
          break;
        }
    case ',':
    case '\n':
    case '&':
      myFile.print(c);
      dec(c);
      break;

    case '!':
      tftmsg("Uploading done!", GREEN, BLACK);
      exitt = true;
      fpointer = 0;
      myFile.print(c);
      myFile.close();
      delay(5000);
      return true;
  }
  return false;
}



bool pgmMode(){
  for(int i=0;i<7000;i++){
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
        tft.print(7-ii);
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
      delaymode=true;
      //delay(5000);
      break;
    case '0' ... '?':
      if (delaymode){
        delay(delays[c-'0']);
        delaymode = false; 
      }
      else{
        uint16_t cc = c;
        data |= (cc-'0'<<idx*4);
        idx++;
      }
      break;
      case '!':
        fpointer=0;
      break;
      }

}

void SDinit(){
  //Serial.print("Initializing SD card...");
  if (!SD.begin(SS_SD)) {
    tftmsg("SD card not found!\nPlease contact to support:\nRedTam SA CV\n8341006372", BLACK,RED);
    while (1);
  }
  ///readtxtinit();
}

//boolean readtxtinit(){
//
//  openNext();
//  
//  if (myFile){
//    return true;
//  }
//  else{
//    return false;
//  }
//}

char readSDchar(){
  if (myFile.available()){
    return myFile.read();
  }
  else{
    //myFile.close();
    openNext();
//    while( !readtxtinit() ){
//      ;
//    }
    //return 'z';
    return myFile.read();
  }
}

void setup() {
  

  //Serial.begin(115200);
  Serial.begin(500000);
  
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

#endif
///////////////////////////////////////////////////
///////////////////////////////////////////////////
///////////////////////////////////////////////////

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
