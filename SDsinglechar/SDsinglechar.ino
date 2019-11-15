#include <SPI.h>
#include <SD.h>
#define Serial Serial1

File myFile;

void setup() {
  // Open Serial communications and wait for port to open:
  Serial.begin(9600);
  while (!Serial) {
    ; // wait for Serial port to connect. Needed for native USB port only
  }

  Serial.print("Initializing SD card...");

  if (!SD.begin(PB13)) {
    Serial.println("initialization failed!");
    while (1);
  }
  Serial.println("initialization done.");

  myFile = SD.open("ima.txt");
  if (myFile) {
    Serial.println("ima.txt:");

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
