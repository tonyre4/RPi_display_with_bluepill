import serial
import time
t = 0.00001

if True:
    ser = serial.Serial('/dev/ttyUSB0',500000)
   
    
    with open("dec.txt", "r") as f:
        for l in f:
            for c in l:
                #print(c,end="")
                ser.write('{}'.format(c).encode())
                #time.sleep(t)

    ser.close()

